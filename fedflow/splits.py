"""Train/test splits with audits. No host or IP is ever chosen by hand.

* ``signature``: StratifiedGroupKFold over flow signatures (exact or log-binned).
* ``host``: K-fold over source hosts. The test set is every flow sent by the fold's source hosts.
  In ``endpoints`` mode every training flow that touches *any* host seen in the test set (sender
  or receiver) is dropped, so attackers and victims are both unseen; the audit reports how many
  flows that removes. ``source`` mode only separates source hosts.
* ``attacker``: leave-attacker-out. Attacker hosts (sources of at least ``min_attack_flows``
  attack flows) are spread over the folds so each fold holds out different attackers, heaviest
  first, each going to the fold with the fewest attack flows so far. With ``n_folds`` >= the number of
  attackers this is leave-one-attacker-out. All other source hosts (benign senders, sparse
  attackers) are assigned to folds at random. Benchmarks have only a handful of attacker hosts,
  so a plain K-fold over hosts leaves most test folds without any attack; this split does not.
  A class whose every attacker is in the test fold cannot be learned: metrics report it in
  ``test_classes_unseen_in_training`` and ``balanced_accuracy_seen_classes`` leaves it out.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

from .data import FlowDataset, flow_signatures

log = logging.getLogger("fedflow")


@dataclass
class Split:
    name: str
    fold: int
    train_idx: np.ndarray
    test_idx: np.ndarray
    audit: Dict[str, Any] = field(default_factory=dict)


def iter_splits(ds: FlowDataset, scfg: Dict[str, Any], folds: List[int] | None = None) -> Iterator[Split]:
    kind = scfg["type"]
    k = int(scfg.get("n_folds", 5))
    seed = int(scfg.get("seed", 42))
    wanted = set(range(k)) if folds is None else set(folds)
    if kind == "signature":
        groups = flow_signatures(ds, scfg.get("signature", {}))
        sgkf = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed)
        for f, (tr, te) in enumerate(sgkf.split(np.zeros(len(ds)), ds.y, groups=groups)):
            if f in wanted:
                yield Split("signature", f, tr, te, audit_split(ds, tr, te, groups))
    elif kind == "host":
        yield from _host_splits(ds, scfg, k, seed, wanted)
    elif kind == "attacker":
        yield from _attacker_splits(ds, scfg, k, seed, wanted)
    else:
        raise ValueError(f"Unknown split.type {kind!r} (use 'signature', 'host' or 'attacker')")


def _train_test(ds: FlowDataset, test_sources: np.ndarray, mode: str):
    src, dst = ds.src, ds.dst
    is_test_src = np.isin(src, test_sources)
    te = np.where(is_test_src)[0]
    if mode == "source":
        tr = np.where(~is_test_src)[0]
    elif mode == "endpoints":
        test_hosts = np.union1d(src[te], dst[te])
        tr = np.where(~(np.isin(src, test_hosts) | np.isin(dst, test_hosts)))[0]
    else:
        raise ValueError(f"Unknown split.host_mode {mode!r}")
    return tr, te


def _attacker_splits(ds: FlowDataset, scfg, k, seed, wanted) -> Iterator[Split]:
    if ds.benign_class is None:
        raise ValueError("split.type 'attacker' needs dataset.benign_class")
    mode = scfg.get("host_mode", "source")
    src, y = ds.src, ds.y
    attack = y != ds.classes.index(ds.benign_class)
    n_hosts = int(max(src.max(), ds.dst.max())) + 1
    attack_flows = np.bincount(src[attack], minlength=n_hosts)
    min_flows = int(scfg.get("min_attack_flows", 50))
    attackers = [h for h in np.argsort(-attack_flows, kind="stable") if attack_flows[h] >= min_flows]
    if len(attackers) < 2:
        raise ValueError(f"Only {len(attackers)} attacker host(s) with >= {min_flows} attack flows")
    k_eff = min(k, len(attackers))
    fold_of = np.full(n_hosts, -1)
    load = np.zeros(k_eff)
    for h in attackers:                                  # heaviest attacker first, to the lightest fold
        f = int(np.argmin(load))
        fold_of[h] = f
        load[f] += attack_flows[h]
    rng = np.random.default_rng(seed)
    rest = np.where(fold_of < 0)[0]
    fold_of[rest] = rng.integers(0, k_eff, size=len(rest))
    names = ds.hosts or None
    for f in range(k_eff):
        if f not in wanted:
            continue
        test_sources = np.where(fold_of == f)[0]
        tr, te = _train_test(ds, test_sources, mode)
        audit = audit_split(ds, tr, te, None)
        audit["dropped_flows"] = int(len(ds) - len(tr) - len(te))
        audit["host_mode"] = mode
        held = [h for h in attackers if fold_of[h] == f]
        audit["test_attackers"] = [names[h] if names is not None else int(h) for h in held]
        audit["n_attackers_total"] = len(attackers)
        yield Split(f"attacker-{mode}", f, tr, te, audit)


def _host_splits(ds: FlowDataset, scfg, k, seed, wanted) -> Iterator[Split]:
    mode = scfg.get("host_mode", "endpoints")
    src, dst, y = ds.src, ds.dst, ds.y
    # Folds are formed over source hosts, stratified by each host's dominant class so attack
    # classes are spread over folds; the assignment is driven only by the data and the seed.
    sgkf = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed)
    for f, (_, te_rows) in enumerate(sgkf.split(np.zeros(len(ds)), y, groups=src)):
        if f not in wanted:
            continue
        test_sources = np.unique(src[te_rows])
        is_test_src = np.isin(src, test_sources)
        if mode == "source":
            te = np.where(is_test_src)[0]
            tr = np.where(~is_test_src)[0]
        elif mode == "endpoints":
            te = np.where(is_test_src)[0]
            test_hosts = np.union1d(src[te], dst[te])
            touches = np.isin(src, test_hosts) | np.isin(dst, test_hosts)
            tr = np.where(~touches)[0]
        else:
            raise ValueError(f"Unknown split.host_mode {mode!r}")
        audit = audit_split(ds, tr, te, None)
        audit["dropped_flows"] = int(len(ds) - len(tr) - len(te))
        audit["host_mode"] = mode
        yield Split(f"host-{mode}", f, tr, te, audit)


def audit_split(ds: FlowDataset, tr: np.ndarray, te: np.ndarray, groups) -> Dict[str, Any]:
    src, dst, y = ds.src, ds.dst, ds.y
    a: Dict[str, Any] = {"n_train": int(len(tr)), "n_test": int(len(te))}
    if groups is not None:
        a["signature_overlap"] = int(len(np.intersect1d(groups[tr], groups[te])))
    a["shared_src_hosts"] = int(len(np.intersect1d(src[tr], src[te])))
    a["shared_dst_hosts"] = int(len(np.intersect1d(dst[tr], dst[te])))
    a["shared_any_hosts"] = int(len(np.intersect1d(np.union1d(src[tr], dst[tr]), np.union1d(src[te], dst[te]))))
    n_cls = len(ds.classes)
    a["train_support"] = np.bincount(y[tr], minlength=n_cls).tolist()
    a["test_support"] = np.bincount(y[te], minlength=n_cls).tolist()
    missing = [ds.classes[c] for c in range(n_cls) if a["test_support"][c] == 0 or a["train_support"][c] == 0]
    a["classes_missing_in_train_or_test"] = missing
    if missing:
        log.warning("Split is missing classes in train or test: %s (metrics exclude them)", missing)
    return a
