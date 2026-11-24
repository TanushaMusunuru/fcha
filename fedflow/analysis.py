"""Attention diagnostics for FCHA: on hosts that mix traffic classes, does a flow attend to
same-class flows more than uniform averaging would? Hosts are selected from the data, not by name.
Labels are used here only after prediction, for analysis.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
import torch

from .graph import FlowGraph


@torch.no_grad()
def attention_lift(model, X: torch.Tensor, graph: FlowGraph, y: np.ndarray, classes: List[str],
                   batch_size: int, seed: int, max_queries_per_class: int = 2000) -> Dict[str, Any]:
    if getattr(model, "aggregator", None) != "attention":
        return {}
    model.eval()
    y_t = torch.as_tensor(y, device=X.device)
    src = graph.src.cpu().numpy()
    dst = graph.dst.cpu().numpy()
    # Mixed hosts: a host whose incident flows contain at least two classes.
    inc = pd.DataFrame({"h": np.concatenate([src, dst]), "y": np.concatenate([y, y])})
    n_cls = inc.groupby("h")["y"].nunique()
    mixed = np.zeros(graph.num_hosts, dtype=bool)
    mixed[n_cls.index.to_numpy()] = n_cls.to_numpy() >= 2
    on_mixed = mixed[src] | mixed[dst]
    rng = np.random.RandomState(seed)
    gen = torch.Generator().manual_seed(seed)
    result: Dict[str, Any] = {"n_mixed_hosts": int(mixed.sum()), "per_class": {}}
    for c, name in enumerate(classes):
        q = np.where((y == c) & on_mixed)[0]
        if len(q) == 0:
            continue
        q = rng.choice(q, size=min(len(q), max_queries_per_class), replace=False)
        attn_same, unif_same = [], []
        for s in range(0, len(q), batch_size):
            b = torch.as_tensor(q[s:s + batch_size], device=X.device)
            _, _, extras = model(X, graph, b, gen, return_attention=True)
            for side, (attn, nbr, valid) in extras.items():
                host = (src if side == 0 else dst)[b.cpu().numpy()]
                keep = mixed[host] & (valid.sum(1) > 0).cpu().numpy()
                same = (y_t[nbr] == c) & valid
                a = (attn * same).sum(1)
                u = same.sum(1).float() / valid.sum(1).clamp(min=1)
                attn_same.append(a.cpu().numpy()[keep])
                unif_same.append(u.cpu().numpy()[keep])
        a = np.concatenate(attn_same)
        u = np.concatenate(unif_same)
        if len(a):
            result["per_class"][name] = {"queries": int(len(a)), "attention_on_same_class": float(a.mean()),
                                         "uniform_same_class": float(u.mean()),
                                         "lift": float(a.mean() / max(u.mean(), 1e-9))}
    return result
