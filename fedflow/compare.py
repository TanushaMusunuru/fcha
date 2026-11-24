"""Cross-dataset comparison: one table and one chart from several results.jsonl files.

    python -m fedflow.compare results/fedflow/a/results.jsonl results/fedflow/b/results.jsonl \
        --out results/comparison --models fcha,fcha_centralised,flow_mlp,random_forest

Values are mean ± sample SD over all (fold, seed) runs found for each dataset and model, so the
same command works for a single fold now and for the full grid later.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

from .summarize import load

METRICS = [("bal_acc", "Balanced accuracy"), ("macro_f1", "Macro-F1"), ("fpr", "False-positive rate")]


def _cell(x: pd.Series) -> str:
    x = x.dropna() * 100
    if x.empty:
        return "—"
    return f"{x.mean():.1f}" if len(x) == 1 else f"{x.mean():.1f} ± {x.std(ddof=1):.1f}"


def compare(paths: List[Path], out: Path, models: Optional[List[str]] = None, split: Optional[str] = None,
            partitions: Optional[List[str]] = None) -> pd.DataFrame:
    df = pd.concat([load(p) for p in paths], ignore_index=True)
    df = df[~df["model"].str.contains("permuted")]
    if split:
        df = df[df["split"] == split]
    if partitions:
        df = df[df["partition"].isin(partitions)]
    if models:
        df = df[df["model"].isin(models)]
    order = models or sorted(df["model"].unique())
    datasets = list(dict.fromkeys(df["dataset"]))

    rows = []
    for m in order:
        g = df[df.model == m]
        if g.empty:
            continue
        row = {"Model": m, "Training": "centralised" if (g["partition"] == "centralised").all() else "federated"}
        for d in datasets:
            gd = g[g.dataset == d]
            for key, label in METRICS:
                row[f"{d} | {label}"] = _cell(gd[key])
            row[f"{d} | runs"] = len(gd)
        rows.append(row)
    table = pd.DataFrame(rows)
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "comparison.csv", index=False)
    with open(out / "comparison.md", "w", encoding="utf-8") as fh:
        fh.write("Balanced accuracy, macro-F1 and false-positive rate (%), test set; mean ± sample SD when "
                 "several (fold, seed) runs exist.\n\n")
        fh.write(table.to_string(index=False))
        fh.write("\n")
    _chart(df, order, datasets, out / "comparison.png")
    return table


def _chart(df: pd.DataFrame, order: List[str], datasets: List[str], path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    import textwrap
    present = [m for m in order if (df.model == m).any()]
    fig, axes = plt.subplots(1, 2, figsize=(max(11, 3.0 * len(datasets)), 4.8), sharey=True)
    tick_labels = [textwrap.fill(d.replace("-", "- "), 14).replace("- ", "-") for d in datasets]
    width = 0.8 / max(len(present), 1)
    x = np.arange(len(datasets))
    for ax, (key, label) in zip(axes, METRICS[:2]):
        for i, m in enumerate(present):
            means, sds = [], []
            for d in datasets:
                v = df[(df.model == m) & (df.dataset == d)][key].dropna() * 100
                means.append(v.mean() if len(v) else np.nan)
                sds.append(v.std(ddof=1) if len(v) > 1 else 0.0)
            bars = ax.bar(x + (i - (len(present) - 1) / 2) * width, means, width, yerr=sds, capsize=3, label=m)
            for b, v in zip(bars, means):
                if not np.isnan(v):
                    ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}", ha="center", va="bottom", fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels(tick_labels, fontsize=9)
        ax.set_title(label)
        ax.set_ylim(0, 105)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("%")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=len(present), fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results", nargs="+", help="results.jsonl files, one or more per dataset")
    ap.add_argument("--out", default="results/comparison")
    ap.add_argument("--models", help="comma-separated models, in display order")
    ap.add_argument("--split", default="signature", help="split name to compare (default: signature)")
    ap.add_argument("--partitions", help="comma-separated partitions to include (default: all)")
    a = ap.parse_args()
    t = compare([Path(p) for p in a.results], Path(a.out), a.models.split(",") if a.models else None,
                a.split, a.partitions.split(",") if a.partitions else None)
    print(t.to_string(index=False))


if __name__ == "__main__":
    main()
