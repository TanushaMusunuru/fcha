"""Paper tables and figures from the merged paper results.

    python -m fedflow.paper_report                      # all datasets under results/paper/
    python -m fedflow.paper_report --datasets nf_ton_iot_v2,ton_iot_network --out results/paper/report

Writes REPORT.md, LaTeX tables (booktabs) and PNG figures:
  T1 main results       signature and leave-attacker-out splits, IID clients, mean ± SD over folds × seeds,
                        paired Wilcoxon vs FCHA (Holm-corrected)
  T2 heterogeneity      IID vs label-skewed (Dirichlet) clients
  T3 ablation           aggregation type, SupCon, centralised training (signature split)
  T4 per-class recall   FCHA and the strongest baselines
  T5 attention lift     same-class attention on mixed hosts
  T6 data reduction     duplicate capping per class
  F1 main bar chart, F2 FCHA confusion matrices, F3 attention lift
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAIN_MODELS = ["fcha", "egraphsage_mean", "host_mean_only", "flow_mlp", "random_forest", "xgboost"]
ABLATION_MODELS = ["fcha", "fcha_supcon", "fcha_centralised", "egraphsage_mean", "host_mean_only", "flow_mlp"]
LABELS = {"fcha": "FCHA (ours)", "egraphsage_mean": "E-GraphSAGE-style", "host_mean_only": "Host-mean (FedGATSage-style)",
          "flow_mlp": "Flow-MLP", "random_forest": "Random Forest†", "xgboost": "XGBoost†",
          "fcha_supcon": "FCHA + SupCon", "fcha_centralised": "FCHA, centralised†"}


def load_runs(path: Path) -> pd.DataFrame:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        m = r["metrics"]
        rows.append({"dataset": r["dataset"], "split": r["split"].split("-")[0], "partition": r["partition"],
                     "model": r["model"], "fold": r["fold"], "seed": r["seed"],
                     # Leave-attacker-out folds score only supported classes (see fedflow.metrics).
                     "bal_acc": m.get("balanced_accuracy_supported", m["balanced_accuracy"]),
                     "macro_f1": m.get("macro_f1_supported", m["macro_f1"]), "accuracy": m["accuracy"],
                     "fpr": m.get("false_positive_rate"),
                     "recall": {c: v["recall"] for c, v in m["per_class"].items() if v["support"]},
                     "cm": np.array(m["confusion_matrix"]), "classes": r["classes"],
                     "lift": {c: v["lift"] for c, v in (r.get("attention") or {}).get("per_class", {}).items()},
                     "comm_mb": (r.get("comm_bytes") or 0) / 1e6})
    return pd.DataFrame(rows)


def md_table(t: pd.DataFrame) -> str:
    """Markdown table without the optional ``tabulate`` dependency."""
    head = "| " + " | ".join(map(str, t.columns)) + " |"
    sep = "|" + "|".join("---" for _ in t.columns) + "|"
    body = ["| " + " | ".join(str(v) for v in row) + " |" for row in t.itertuples(index=False)]
    return "\n".join([head, sep, *body])


def fmt(x: pd.Series) -> str:
    x = x.dropna() * 100
    if x.empty:
        return "—"
    return f"{x.mean():.1f}" if len(x) == 1 else f"{x.mean():.1f} ± {x.std(ddof=1):.1f}"


def holm(pvals: Dict[str, float]) -> Dict[str, float]:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def paired_tests(df: pd.DataFrame, ref: str, models: List[str]) -> Dict[str, float]:
    from scipy.stats import wilcoxon
    r = df[df.model == ref][["fold", "seed", "bal_acc"]]
    p = {}
    for m in models:
        if m == ref:
            continue
        pair = df[df.model == m][["fold", "seed", "bal_acc"]].merge(r, on=["fold", "seed"], suffixes=("", "_ref"))
        if len(pair) >= 5 and (pair.bal_acc_ref - pair.bal_acc).abs().sum() > 0:
            p[m] = float(wilcoxon(pair.bal_acc_ref, pair.bal_acc).pvalue)
    return holm(p) if p else {}


def table(df: pd.DataFrame, models: List[str], split: str, partitions: List[str]) -> pd.DataFrame:
    sub = df[(df.split == split) & (df.partition.isin(partitions))]
    tests = paired_tests(sub, "fcha", models)
    rows = []
    for m in models:
        g = sub[sub.model == m]
        if g.empty:
            continue
        p = tests.get(m)
        rows.append({"Model": LABELS.get(m, m), "runs": len(g), "Accuracy": fmt(g.accuracy),
                     "Balanced acc.": fmt(g.bal_acc), "Macro-F1": fmt(g.macro_f1), "FPR": fmt(g.fpr),
                     "p vs FCHA (Holm)": "—" if p is None else (f"{p:.3f}" if p >= 0.001 else "<0.001")})
    return pd.DataFrame(rows)


def to_latex(t: pd.DataFrame, caption: str, label: str) -> str:
    cols = "l" + "r" * (len(t.columns) - 1)
    lines = [r"\begin{table}[t]", r"\centering", rf"\caption{{{caption}}}", rf"\label{{{label}}}",
             rf"\begin{{tabular}}{{{cols}}}", r"\toprule", " & ".join(t.columns) + r" \\", r"\midrule"]
    for _, row in t.iterrows():
        lines.append(" & ".join(str(v).replace("±", r"$\pm$").replace("†", r"$^\dagger$")
                                .replace("<", r"$<$") for v in row.values) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines)


def per_class(df: pd.DataFrame, models: List[str]) -> pd.DataFrame:
    sub = df[(df.split == "signature") & (df.partition.isin(["iid", "centralised"]))]
    classes = sorted({c for r in sub.recall for c in r})
    rows = []
    for c in classes:
        row = {"Class": c}
        for m in models:
            v = [r.get(c) for r in sub[sub.model == m].recall if r.get(c) is not None]
            row[LABELS.get(m, m)] = f"{100 * np.mean(v):.1f}" if v else "—"
        rows.append(row)
    return pd.DataFrame(rows)


def lift_table(df: pd.DataFrame) -> pd.DataFrame:
    sub = df[(df.model == "fcha") & (df.partition == "iid")]
    classes = sorted({c for r in sub.lift for c in r})
    rows = []
    for split in ["signature", "attacker", "host"]:
        s = sub[sub.split == split]
        if s.empty:
            continue
        row = {"Split": split}
        for c in classes:
            v = [r[c] for r in s.lift if c in r]
            row[c] = f"{np.mean(v):.2f}" if v else "—"
        rows.append(row)
    return pd.DataFrame(rows)


def figures(df: pd.DataFrame, name: str, out: Path) -> List[str]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    files = []
    sub = df[df.partition.isin(["iid", "centralised"])]
    models = [m for m in MAIN_MODELS if (sub.model == m).any()]
    splits = [s for s in ["signature", "attacker", "host"] if (sub.split == s).any()]
    if models and splits:
        fig, ax = plt.subplots(figsize=(1.6 + 1.3 * len(models) * len(splits) / 2, 4))
        w = 0.8 / len(models)
        for i, m in enumerate(models):
            vals = [sub[(sub.model == m) & (sub.split == s)].bal_acc * 100 for s in splits]
            ax.bar(np.arange(len(splits)) + (i - (len(models) - 1) / 2) * w, [v.mean() for v in vals], w,
                   yerr=[v.std(ddof=1) if len(v) > 1 else 0 for v in vals], capsize=3, label=LABELS.get(m, m))
        ax.set_xticks(np.arange(len(splits)))
        ax.set_xticklabels([f"{s} split" for s in splits])
        ax.set_ylabel("Balanced accuracy (%)")
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=7, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.38), frameon=False)
        ax.set_title(name)
        fig.tight_layout()
        f = out / f"F1_main_{name}.png"
        fig.savefig(f, dpi=200)
        plt.close(fig)
        files.append(f.name)
    for split in splits:
        s = sub[(sub.model == "fcha") & (sub.split == split)]
        if s.empty:
            continue
        cm = sum(s.cm)
        classes = s.classes.iloc[0]
        norm = cm / np.maximum(cm.sum(1, keepdims=True), 1)
        fig, ax = plt.subplots(figsize=(5.5, 4.8))
        im = ax.imshow(norm * 100, cmap="Blues", vmin=0, vmax=100)
        ax.set_xticks(range(len(classes)))
        ax.set_xticklabels(classes, rotation=45, ha="right", fontsize=8)
        ax.set_yticks(range(len(classes)))
        ax.set_yticklabels(classes, fontsize=8)
        for i in range(len(classes)):
            for j in range(len(classes)):
                if norm[i, j] >= 0.01:
                    ax.text(j, i, f"{100 * norm[i, j]:.0f}", ha="center", va="center", fontsize=7,
                            color="white" if norm[i, j] > 0.5 else "black")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")
        ax.set_title(f"FCHA, {name}, {split} split (row %)")
        fig.colorbar(im, ax=ax, fraction=0.046)
        fig.tight_layout()
        f = out / f"F2_confusion_{name}_{split}.png"
        fig.savefig(f, dpi=200)
        plt.close(fig)
        files.append(f.name)
    return files


def build(datasets: List[str], out: Path, results_root: Optional[Path] = None) -> None:
    results_root = Path(results_root) if results_root else ROOT / "results" / "paper"
    out.mkdir(parents=True, exist_ok=True)
    md = ["# FedFlow paper results", "",
          "Mean ± sample SD over folds × seeds. † = centralised (sees pooled data); all others are federated "
          "(5 clients). p-values: paired Wilcoxon signed-rank vs FCHA over matched (fold, seed), Holm-corrected.", ""]
    tex = []
    for d in datasets:
        path = results_root / d / "results.jsonl"
        if not path.exists():
            md += [f"## {d}", "", "_No results yet._", ""]
            continue
        df = load_runs(path)
        df = df[~df.model.str.contains("permuted")]
        name = df.dataset.iloc[0]
        md += [f"## {name}", ""]
        for split in ["signature", "attacker", "host"]:
            t = table(df, MAIN_MODELS, split, ["iid", "centralised"])
            if not t.empty:
                md += [f"### T1 — main results, {split} split, IID clients", "", md_table(t), ""]
                tex.append(to_latex(t, f"{name}: {split} split, IID clients.", f"tab:{d}_{split}"))
        het = df[(df.split == "signature") & (df.model.isin(["fcha", "flow_mlp"]))]
        if (het.partition != "iid").any():
            rows = [{"Model": LABELS.get(m, m), "Partition": p, "Balanced acc.": fmt(g.bal_acc), "Macro-F1": fmt(g.macro_f1)}
                    for (m, p), g in het.groupby(["model", "partition"])]
            md += ["### T2 — client heterogeneity (signature split)", "", md_table(pd.DataFrame(rows)), ""]
        t3 = table(df, ABLATION_MODELS, "signature", ["iid", "centralised"])
        if not t3.empty:
            md += ["### T3 — ablation (signature split)", "", md_table(t3), ""]
        md += ["### T4 — per-class recall (%), signature split", "",
               md_table(per_class(df, ["fcha", "flow_mlp", "random_forest", "xgboost"])), ""]
        lt = lift_table(df)
        if not lt.empty:
            md += ["### T5 — attention lift on mixed hosts (FCHA)", "", md_table(lt), ""]
        dr = results_root / d
        reports = list(dr.rglob("dedup_report.json")) if dr.exists() else []
        if reports:
            rep = json.loads(reports[0].read_text(encoding="utf-8"))
            rows = [{"Class": c, "Before": v["before"], "After": v["after"]} for c, v in rep["per_class"].items()]
            md += [f"### T6 — duplicate capping (≤{rep['max_copies']} copies per identical flow)", "",
                   md_table(pd.DataFrame(rows)), ""]
        for f in figures(df, d, out):
            md += [f"![{f}]({f})", ""]
    (out / "REPORT.md").write_text("\n".join(md), encoding="utf-8")
    (out / "tables.tex").write_text("\n\n".join(tex), encoding="utf-8")
    print(f"wrote {out / 'REPORT.md'} and {out / 'tables.tex'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--datasets", default=None, help="comma-separated paper dataset names (default: all found)")
    ap.add_argument("--out", default=str(ROOT / "results" / "paper" / "report"))
    a = ap.parse_args()
    ds = a.datasets.split(",") if a.datasets else sorted(p.parent.name for p in (ROOT / "results" / "paper").glob("*/results.jsonl"))
    build(ds, Path(a.out))


if __name__ == "__main__":
    main()
