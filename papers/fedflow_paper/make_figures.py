"""Figures for the FedFlow/FCHA paper, computed from paper_results/runs/*.results.jsonl.

    py -3 papers/fedflow_paper/make_figures.py
"""
import collections
import json
import statistics as st
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "paper_results" / "runs"
OUT = Path(__file__).resolve().parent / "figures"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({"font.family": "serif", "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
                     "legend.fontsize": 7, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
                     "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})

DATASETS = [("nf_ton_iot_v2", "NF-ToN-IoT-v2"), ("ton_iot_network", "ToN-IoT-Network"),
            ("nf_cse_cic_ids2018_v2", "NF-CIC-IDS2018-v2")]
MODELS = [("fcha", "iid", "FCHA (ours)"), ("egraphsage_mean", "iid", "E-GraphSAGE-mean"),
          ("host_mean_only", "iid", "Host-mean"), ("flow_mlp", "iid", "Flow-MLP"),
          ("random_forest", "centralised", "Random Forest†"), ("xgboost", "centralised", "XGBoost†")]
COLORS = ["#1f4e9c", "#5b9bd5", "#a5a5a5", "#70ad47", "#c55a11", "#ffc000"]


def load(d):
    return [json.loads(l) for l in open(RUNS / f"{d}.results.jsonl", encoding="utf-8") if l.strip()]


def metric(r, key="balanced_accuracy"):
    m = r["metrics"]
    if key == "balanced_accuracy" and r["split"].startswith("attacker"):
        return 100 * m.get("balanced_accuracy_supported", m["balanced_accuracy"])
    return 100 * m[key]


def select(R, split, model, part):
    return [r for r in R if r["split"].startswith(split) and r["model"] == model
            and r["partition"] == part and not r["permuted_labels"]]


def fpr(r):
    m = r["metrics"]
    for k in ("false_positive_rate", "fpr"):
        if k in m:
            return 100 * m[k]
    raise KeyError(list(m))


# ---------------------------------------------------------------- Fig. 2: main results
def fig_main():
    fig, axes = plt.subplots(1, 2, figsize=(7.16, 2.5), sharey=False)
    for ax, (split, title) in zip(axes, [("signature", "(a) Signature split: unseen flow patterns"),
                                         ("attacker", "(b) Leave-attacker-out split: unseen attackers")]):
        w = 0.13
        for j, (m, p, lab) in enumerate(MODELS):
            means, sds = [], []
            for d, _ in DATASETS:
                v = [metric(r) for r in select(load(d), split, m, p)]
                means.append(st.mean(v)); sds.append(st.stdev(v))
            xs = [i + (j - 2.5) * w for i in range(len(DATASETS))]
            ax.bar(xs, means, w, yerr=sds, color=COLORS[j], label=lab, edgecolor="white", linewidth=0.3,
                   error_kw={"elinewidth": 0.6, "capsize": 1.2, "ecolor": "#333333"})
        ax.set_xticks(range(len(DATASETS)))
        ax.set_xticklabels(["NF-ToN-IoT-v2", "ToN-IoT-\nNetwork", "NF-CIC-\nIDS2018-v2"])
        ax.set_ylabel("Balanced accuracy (%)")
        ax.set_title(title)
        ax.set_ylim(30 if split == "attacker" else 60, 104)
        ax.yaxis.grid(True, linewidth=0.3, alpha=0.6)
        ax.set_axisbelow(True)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=6, frameon=False, bbox_to_anchor=(0.5, 1.04))
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(OUT / "fig_main.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig_main.png", dpi=200, bbox_inches="tight")


# ---------------------------------------------------------------- Fig. 3: per-fold + FPR, attacker split
def fig_attacker():
    fig, axes = plt.subplots(2, 3, figsize=(7.16, 3.9))
    sel = [0, 1, 3, 4, 5]
    for c, (d, name) in enumerate(DATASETS):
        R = load(d)
        ax = axes[0, c]
        for j in sel:
            m, p, lab = MODELS[j]
            per = collections.defaultdict(list)
            for r in select(R, "attacker", m, p):
                per[r["fold"]].append(metric(r))
            folds = sorted(per)
            ax.plot(folds, [st.mean(per[f]) for f in folds], marker="o", ms=3, lw=1.4 if j == 0 else 0.9,
                    color=COLORS[j], label=lab, zorder=3 if j == 0 else 2)
        ax.set_title(name)
        ax.set_xticks(range(5)); ax.set_xticklabels([f"F{i}" for i in range(5)])
        ax.set_ylim(20, 100)
        ax.yaxis.grid(True, linewidth=0.3, alpha=0.6)
        if c == 0:
            ax.set_ylabel("Balanced accuracy (%)")
        ax2 = axes[1, c]
        for j in sel:
            m, p, lab = MODELS[j]
            rs = select(R, "attacker", m, p)
            x = st.mean(fpr(r) for r in rs); y = st.mean(metric(r) for r in rs)
            ax2.scatter(x, y, s=46 if j == 0 else 28, color=COLORS[j], edgecolor="black", linewidth=0.4,
                        zorder=3, marker="*" if j == 0 else "o")
        ax2.set_xlabel("False-positive rate (%)")
        if c == 0:
            ax2.set_ylabel("Mean balanced acc. (%)")
        ax2.grid(True, linewidth=0.3, alpha=0.6)
        ax2.margins(0.25)
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=5, frameon=False, bbox_to_anchor=(0.5, 1.02))
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUT / "fig_attacker.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig_attacker.png", dpi=200, bbox_inches="tight")


# ---------------------------------------------------------------- Fig. 1: architecture
def box(ax, x, y, w, h, text, fc, ec="#1f3864", fs=7, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=0.8))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, a, b, color="#333333", style="-|>", lw=0.8, ls="-"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=7, color=color, lw=lw, linestyle=ls))


def fig_arch():
    fig, ax = plt.subplots(figsize=(7.16, 2.9))
    ax.set_xlim(0, 20); ax.set_ylim(0, 8); ax.axis("off")
    # (a) host graph
    ax.text(2.6, 7.7, "(a) Flow graph on one client", ha="center", fontsize=8, fontweight="bold")
    hosts = {"u": (1.0, 4.3), "v": (4.4, 4.3), "a": (0.4, 6.6), "b": (0.3, 2.0), "c": (5.0, 6.6), "d": (5.0, 2.0)}
    for k, (x, y) in hosts.items():
        ax.add_patch(plt.Circle((x, y), 0.36, fc="#dce6f2" if k in "uv" else "#f2f2f2", ec="#1f3864", lw=0.8))
        ax.text(x, y, k, ha="center", va="center", fontsize=8, style="italic")
    arrow(ax, (1.36, 4.3), (4.04, 4.3), color="#c00000", lw=1.6)
    ax.text(2.7, 4.55, "query flow $e$", ha="center", fontsize=7, color="#c00000")
    for (p, q, col) in [("a", "u", "#1f4e9c"), ("u", "b", "#1f4e9c"), ("b", "u", "#1f4e9c"),
                        ("c", "v", "#70ad47"), ("v", "d", "#70ad47"), ("d", "v", "#70ad47")]:
        (x1, y1), (x2, y2) = hosts[p], hosts[q]
        dx, dy = x2 - x1, y2 - y1; n = (dx * dx + dy * dy) ** 0.5
        arrow(ax, (x1 + 0.38 * dx / n, y1 + 0.38 * dy / n), (x2 - 0.38 * dx / n, y2 - 0.38 * dy / n), color=col)
    ax.text(0.1, 1.1, r"$\mathcal{N}_s(e)$: other flows of sender $u$", fontsize=6.5, color="#1f4e9c")
    ax.text(2.7, 0.55, r"$\mathcal{N}_r(e)$: other flows of receiver $v$", fontsize=6.5, color="#2e7d32")
    # (b) FCHA
    ax.text(10.4, 7.7, "(b) Flow-conditioned host attention", ha="center", fontsize=8, fontweight="bold")
    box(ax, 6.6, 5.9, 2.2, 0.9, "flow $\\mathbf{x}_e$", "#fbe5d6")
    box(ax, 6.6, 3.7, 2.2, 0.9, "sender flows\n$\\{\\mathbf{x}_f\\}_{f\\in\\mathcal{N}_s}$", "#dce6f2", fs=6.5)
    box(ax, 6.6, 1.5, 2.2, 0.9, "receiver flows\n$\\{\\mathbf{x}_f\\}_{f\\in\\mathcal{N}_r}$", "#e2efda", fs=6.5)
    box(ax, 9.3, 1.5, 1.4, 5.3, "shared\nflow\nencoder\n$\\phi$\n\n+ role\n+ side\nembed.", "#ffffff", fs=6.5)
    for y in (6.35, 4.15, 1.95):
        arrow(ax, (8.8, y), (9.3, y))
    box(ax, 11.2, 3.55, 1.9, 1.2, "multi-head\nattention\nQ: $\\mathbf{h}_e$", "#dce6f2", fs=6.5)
    box(ax, 11.2, 1.35, 1.9, 1.2, "multi-head\nattention\nQ: $\\mathbf{h}_e$", "#e2efda", fs=6.5)
    arrow(ax, (10.7, 4.15), (11.2, 4.15)); arrow(ax, (10.7, 1.95), (11.2, 1.95))
    arrow(ax, (10.7, 6.35), (12.15, 4.75), color="#c00000", ls="--")
    arrow(ax, (10.7, 6.35), (11.6, 2.55), color="#c00000", ls="--")
    ax.text(12.0, 6.55, "query = the flow\nbeing classified", fontsize=6.2, color="#c00000", ha="center")
    box(ax, 13.6, 2.6, 1.0, 3.3, "concat\n$[\\mathbf{h}_e;$\n$\\mathbf{c}_s;$\n$\\mathbf{c}_r]$", "#ffffff", fs=6.5)
    arrow(ax, (13.1, 4.15), (13.6, 4.15)); arrow(ax, (13.1, 1.95), (13.6, 2.9))
    arrow(ax, (10.7, 6.6), (13.6, 5.6))
    box(ax, 14.9, 3.65, 1.3, 1.2, "MLP\nhead\n$\\to\\hat{y}_e$", "#fbe5d6", fs=6.5)
    arrow(ax, (14.6, 4.25), (14.9, 4.25))
    # (c) federation
    ax.text(18.2, 7.7, "(c) Federated training", ha="center", fontsize=8, fontweight="bold")
    box(ax, 16.8, 5.9, 2.6, 0.9, "server\nFedAvg", "#fff2cc", fs=6.8, bold=True)
    ys = (4.45, 3.25, 2.05)
    for i, y in enumerate(ys):
        box(ax, 16.8, y, 2.2, 0.85, f"client {i + 1}\nflows + graph", "#f2f2f2", fs=6.2)
        ax.plot([19.0, 19.55], [y + 0.42, y + 0.42], color="#7f6000", lw=0.8)
    arrow(ax, (19.55, ys[-1] + 0.42), (19.55, 6.35), color="#7f6000", style="<|-|>")
    ax.plot([19.4, 19.55], [6.35, 6.35], color="#7f6000", lw=0.8)
    ax.text(18.1, 1.05, "shared: weights, feature moments,\nvalidation confusion counts\n"
            "never shared: flows, labels, IPs", ha="center", va="center", fontsize=5.6, color="#404040")
    fig.savefig(OUT / "fig_arch.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig_arch.png", dpi=200, bbox_inches="tight")


if __name__ == "__main__":
    fig_arch(); fig_main(); fig_attacker()
    print("figures written to", OUT)
