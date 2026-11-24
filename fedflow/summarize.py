"""Summarise results.jsonl into Markdown/CSV tables.

Mean and *sample* standard deviation (ddof=1) over all (fold, seed) runs, per-class recall, and a
paired Wilcoxon signed-rank test of every model against ``summary.reference_model`` on matched
(fold, seed) pairs.

    python -m fedflow.summarize results/fedflow/results.jsonl --reference fcha
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

KEYS = ["dataset", "split", "partition", "model"]


def load(path: Path) -> pd.DataFrame:
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            row = {k: r[k] for k in KEYS + ["fold", "seed", "kind"]}
            m = r["metrics"]
            row.update(bal_acc=m["balanced_accuracy"], macro_f1=m["macro_f1"], accuracy=m["accuracy"],
                       bal_acc_seen=m.get("balanced_accuracy_seen_classes", np.nan),
                       fpr=m.get("false_positive_rate"), comm_mb=(r.get("comm_bytes") or 0) / 1e6)
            for cls, v in m["per_class"].items():
                row[f"recall:{cls}"] = v["recall"] if v["support"] else np.nan
            rows.append(row)
    return pd.DataFrame(rows)


def _fmt(x: pd.Series) -> str:
    x = x.dropna() * 100
    if len(x) == 0:
        return "n/a"
    sd = x.std(ddof=1) if len(x) > 1 else 0.0
    return f"{x.mean():.2f} ± {sd:.2f}"


def summarize(results: Path, out_dir: Path, scfg: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    scfg = scfg or {}
    df = load(Path(results))
    if df.empty:
        return df
    rows = []
    ref = scfg.get("reference_model")
    for key, g in df.groupby(KEYS):
        row = dict(zip(KEYS, key))
        row.update(runs=len(g), folds=g["fold"].nunique(), seeds=g["seed"].nunique(),
                   balanced_accuracy=_fmt(g["bal_acc"]), bal_acc_seen_classes=_fmt(g["bal_acc_seen"]),
                   macro_f1=_fmt(g["macro_f1"]),
                   accuracy=_fmt(g["accuracy"]), comm_mb=round(g["comm_mb"].mean(), 2))
        if ref and key[3] != ref:
            # Same partition when comparable; centralised baselines are compared with the reference
            # model trained under summary.reference_partition.
            part = key[2] if (df.partition[df.model == ref] == key[2]).any() else scfg.get("reference_partition", "iid")
            r = df[(df.dataset == key[0]) & (df.split == key[1]) & (df.model == ref) & (df.partition == part)]
            pair = g.merge(r[["fold", "seed", "bal_acc"]], on=["fold", "seed"], suffixes=("", "_ref"))
            if len(pair) >= 5:
                from scipy.stats import wilcoxon
                diff = pair["bal_acc_ref"] - pair["bal_acc"]
                row[f"delta_vs_{ref}"] = f"{diff.mean() * 100:+.2f}"
                row["wilcoxon_p"] = float(wilcoxon(diff).pvalue) if diff.abs().sum() > 0 else 1.0
            else:
                row[f"delta_vs_{ref}"] = "n<5 pairs"
        rows.append(row)
    table = pd.DataFrame(rows)
    recall_cols = [c for c in df.columns if c.startswith("recall:")]
    recall = df.groupby(KEYS)[recall_cols].mean().mul(100).round(1).reset_index()
    out_dir = Path(out_dir)
    table.to_csv(out_dir / "summary.csv", index=False)
    recall.to_csv(out_dir / "per_class_recall.csv", index=False)
    with open(out_dir / "summary.md", "w", encoding="utf-8") as fh:
        fh.write("# Results (mean ± sample SD over folds x seeds, %)\n\n")
        fh.write(table.to_markdown(index=False) if _has_tabulate() else table.to_string(index=False))
        fh.write("\n\n# Per-class recall (%, mean over runs)\n\n")
        fh.write(recall.to_markdown(index=False) if _has_tabulate() else recall.to_string(index=False))
        fh.write("\n")
    print(table.to_string(index=False))
    return table


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--out", default=None)
    ap.add_argument("--reference", default=None)
    a = ap.parse_args()
    summarize(Path(a.results), Path(a.out or Path(a.results).parent), {"reference_model": a.reference})


if __name__ == "__main__":
    main()
