"""Client partitioning of the training flows.

* ``iid``: every class split evenly over clients (the original paper's setting).
* ``dirichlet``: label skew; class c is divided over clients with proportions ~ Dir(alpha).
* ``host``: each source host (a site/device) belongs to exactly one client, i.e. topology skew.
"""
from __future__ import annotations

from typing import Any, Dict, List

import numpy as np


def partition(y: np.ndarray, src: np.ndarray, pcfg: Dict[str, Any], n_clients: int, seed: int) -> List[np.ndarray]:
    kind = pcfg.get("type", "iid")
    rng = np.random.RandomState(seed)
    if n_clients == 1:
        return [np.arange(len(y))]
    if kind == "iid":
        parts: List[list] = [[] for _ in range(n_clients)]
        for c in np.unique(y):
            idx = np.where(y == c)[0]
            rng.shuffle(idx)
            for i, chunk in enumerate(np.array_split(idx, n_clients)):
                parts[i].extend(chunk.tolist())
    elif kind == "dirichlet":
        alpha = float(pcfg.get("alpha", 0.5))
        min_size = int(pcfg.get("min_client_size", 50))
        for _ in range(100):
            parts = [[] for _ in range(n_clients)]
            for c in np.unique(y):
                idx = np.where(y == c)[0]
                rng.shuffle(idx)
                props = rng.dirichlet(np.full(n_clients, alpha))
                cuts = (np.cumsum(props) * len(idx)).astype(int)[:-1]
                for i, chunk in enumerate(np.split(idx, cuts)):
                    parts[i].extend(chunk.tolist())
            if min(len(p) for p in parts) >= min_size:
                break
    elif kind == "host":
        hosts = np.unique(src)
        rng.shuffle(hosts)
        # Greedy balancing by flow count so no client is empty.
        counts = {h: c for h, c in zip(*np.unique(src, return_counts=True))}
        load = np.zeros(n_clients)
        owner = {}
        for h in sorted(hosts, key=lambda h: -counts[h]):
            i = int(np.argmin(load))
            owner[h] = i
            load[i] += counts[h]
        own = np.array([owner[h] for h in src])
        parts = [np.where(own == i)[0].tolist() for i in range(n_clients)]
    else:
        raise ValueError(f"Unknown partition.type {kind!r}")
    return [np.sort(np.asarray(p, dtype=np.int64)) for p in parts]
