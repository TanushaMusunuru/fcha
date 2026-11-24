"""Run the experiment grid described by a config.

    python -m fedflow.run --config configs/fedflow/nf_ton_iot.yaml
    python -m fedflow.run --config configs/fedflow/nf_ton_iot.yaml --set federated.rounds=5 --models fcha,rf --folds 0

Grid: split type x fold x client partition x seed x model. Each finished run is appended to
``<results_dir>/results.jsonl``; reruns skip finished runs, so a killed job can be resumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import torch

from .analysis import attention_lift
from .baselines import fit_predict_classical
from .config import deep_merge, load_config
from .data import FeatureBuilder, FlowDataset, cap_duplicates, flow_signatures, load_dataset
from .federated import make_clients, predict, train_federated
from .graph import FlowGraph
from .metrics import evaluate
from .partition import partition
from .splits import iter_splits

log = logging.getLogger("fedflow")


def pick_device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(name)


# Settings that say where or how a grid is launched, not what a run computes. They are left out of
# the run key, so a run done on Kaggle and the same run done locally get the same key.
_LOCATION_KEYS = {"experiment": ("results_dir", "device", "sanity_permuted_labels", "sanity_seeds", "seeds", "folds", "also_done"),
                  "dataset": ("path", "search")}


def run_key(cfg: Dict[str, Any], scfg: Dict[str, Any], mcfg: Dict[str, Any], dataset: str, split: str,
            fold: int, partition: str, seed: int, tag: str) -> str:
    """Identity of one run: everything that changes its result, nothing about where it ran."""
    stable = {k: v for k, v in cfg.items() if k not in ("splits", "models")}
    for section, keys in _LOCATION_KEYS.items():
        stable[section] = {k: v for k, v in (cfg.get(section) or {}).items() if k not in keys}
    stable["split"], stable["model"] = scfg, mcfg
    h = hashlib.sha1(json.dumps(stable, sort_keys=True, default=str).encode()).hexdigest()[:10]
    return f"{dataset}|{split}|{fold}|{partition}|{seed}|{tag}|{h}"


def record_key(rec: Dict[str, Any]) -> str:
    return rec.get("run_key") or rec["run_id"]


def _done_ids(*paths: Path) -> set:
    done = set()
    for path in paths:
        if Path(path).exists():
            with open(path, encoding="utf-8") as fh:
                done |= {record_key(json.loads(line)) for line in fh if line.strip()}
    return done


def _append(path: Path, rec: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")


def run_grid(cfg: Dict[str, Any], models: Optional[List[str]] = None, folds: Optional[List[int]] = None,
             frame: Optional[pd.DataFrame] = None) -> List[Dict[str, Any]]:
    exp = cfg.get("experiment", {})
    out_dir = Path(exp.get("results_dir", "results/fedflow"))
    out_dir.mkdir(parents=True, exist_ok=True)
    results_path = out_dir / "results.jsonl"
    with open(out_dir / "config_used.json", "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)
    cfg_hash = hashlib.sha1(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:10]
    # Runs already finished elsewhere (e.g. merged Kaggle results) are skipped too.
    done = _done_ids(results_path, *exp.get("also_done", []) or [])
    device = pick_device(exp.get("device", "auto"))
    log.info("device=%s results=%s", device, results_path)

    ds = load_dataset(cfg["dataset"], frame)
    sig_cfg = cfg.get("signature", {}) or {}
    dedup_report = None
    if cfg["dataset"].get("max_duplicates"):
        ds, dedup_report = cap_duplicates(ds, sig_cfg, int(cfg["dataset"]["max_duplicates"]),
                                          int(cfg["dataset"].get("subsample_seed", 0)))
        with open(out_dir / "dedup_report.json", "w", encoding="utf-8") as fh:
            json.dump(dedup_report, fh, indent=2)
    groups = flow_signatures(ds, sig_cfg) if sig_cfg.get("columns") else None
    model_cfgs = {k: v for k, v in cfg["models"].items() if models is None or k in models}
    if not model_cfgs:
        raise ValueError(f"No models selected; available: {list(cfg['models'])}")
    seeds = exp.get("seeds", [42])
    folds = folds if folds is not None else exp.get("folds")
    records = []

    for scfg in cfg["splits"]:
        scfg = deep_merge({"signature": sig_cfg}, scfg)
        for sp in iter_splits(ds, scfg, folds):
            log.info("=== split=%s fold=%d audit=%s", sp.name, sp.fold,
                     {k: v for k, v in sp.audit.items() if "support" not in k})
            n_train_classes = len(np.unique(ds.y[sp.train_idx])) if len(sp.train_idx) else 0
            if len(sp.test_idx) == 0 or n_train_classes < 2:
                log.error("Skipping split=%s fold=%d: %d train flows with %d classes, %d test flows",
                          sp.name, sp.fold, len(sp.train_idx), n_train_classes, len(sp.test_idx))
                continue
            tr_frame = ds.frame.iloc[sp.train_idx]
            te_frame = ds.frame.iloc[sp.test_idx]
            y_tr, y_te = ds.y[sp.train_idx], ds.y[sp.test_idx]
            # Vocabularies = summed per-client value counts, identical to fitting on pooled train rows.
            fb = FeatureBuilder(cfg.get("features", {}), ds).fit(tr_frame, y_tr)
            X_tr, X_te = fb.transform(tr_frame), fb.transform(te_frame)
            src_tr, dst_tr = ds.src[sp.train_idx], ds.dst[sp.train_idx]
            g_tr = groups[sp.train_idx] if groups is not None else None
            test_graph = FlowGraph(ds.src[sp.test_idx], ds.dst[sp.test_idx], device)
            base = {"dataset": ds.name, "split": sp.name, "fold": sp.fold, "config_hash": cfg_hash,
                    "classes": ds.classes, "n_features": X_tr.shape[1], "split_audit": sp.audit,
                    "max_duplicates": cfg["dataset"].get("max_duplicates")}

            for seed in seeds:
                jobs = []
                for mname, mcfg in model_cfgs.items():
                    # Optional per-model restrictions keep the grid within a compute budget.
                    if mcfg.get("splits") and scfg["type"] not in mcfg["splits"]:
                        continue
                    if mcfg.get("kind", "federated") == "classical":
                        jobs.append((mname, mcfg, {"name": "centralised"}, False))
                    else:
                        fed = deep_merge(cfg.get("federated", {}), mcfg.get("federated", {}) or {})
                        parts = [{"name": "centralised"}] if int(fed.get("num_clients", 5)) == 1 else cfg["partitions"]
                        for pcfg in parts:
                            if mcfg.get("partitions") and pcfg["name"] not in mcfg["partitions"]:
                                continue
                            jobs.append((mname, mcfg, pcfg, False))
                sanity_seeds = exp.get("sanity_seeds")
                if exp.get("sanity_permuted_labels") and (not sanity_seeds or seed in sanity_seeds):
                    sm = exp.get("sanity_model") or next(k for k, v in model_cfgs.items() if v.get("kind", "federated") != "classical")
                    jobs.append((sm, model_cfgs[sm], cfg["partitions"][0], True))

                for mname, mcfg, pcfg, permuted in jobs:
                    tag = mname + ("+permuted_labels" if permuted else "")
                    run_id = f"{ds.name}|{sp.name}|{sp.fold}|{pcfg['name']}|{seed}|{tag}|{cfg_hash}"
                    key = run_key(cfg, scfg, mcfg, ds.name, sp.name, sp.fold, pcfg["name"], seed, tag)
                    if run_id in done or key in done:
                        log.info("skip finished %s", key)
                        continue
                    t0 = time.time()
                    y_fit = y_tr.copy()
                    if permuted:
                        y_fit = np.random.RandomState(seed).permutation(y_fit)
                    rec = dict(base, run_id=run_id, run_key=key, model=tag, partition=pcfg["name"], seed=seed,
                               kind=mcfg.get("kind", "federated"), permuted_labels=permuted)
                    if mcfg.get("kind", "federated") == "classical":
                        y_pred = fit_predict_classical(mcfg, X_tr, y_fit, X_te, seed)
                    else:
                        fed = deep_merge(cfg.get("federated", {}), mcfg.get("federated", {}) or {})
                        n_clients = int(fed.get("num_clients", 5))
                        parts_idx = partition(y_fit, src_tr, pcfg, n_clients, seed)
                        clients, mean, std = make_clients(
                            [X_tr[p] for p in parts_idx], [y_fit[p] for p in parts_idx],
                            [src_tr[p] for p in parts_idx], [dst_tr[p] for p in parts_idx],
                            [g_tr[p] if g_tr is not None else None for p in parts_idx], fed, seed, device)
                        rec["client_sizes"] = [int(len(p)) for p in parts_idx]
                        rec["client_class_counts"] = [np.bincount(y_fit[p], minlength=len(ds.classes)).tolist()
                                                      for p in parts_idx]
                        out = train_federated(clients, mcfg, fed, X_tr.shape[1], len(ds.classes), seed, device)
                        Xt = torch.as_tensor((X_te - mean) / std, dtype=torch.float32, device=device)
                        idx = torch.arange(len(y_te), device=device)
                        bs = int(fed.get("eval_batch_size", 4096))
                        probs = predict(out["model"], Xt, test_graph, idx, bs, seed + 7,
                                        int(exp.get("eval_samples", 1)))
                        y_pred = probs.argmax(1)
                        rec.update({k: out[k] for k in ("best_round", "best_val_bal_acc", "history",
                                                        "comm_bytes", "param_bytes", "train_seconds")})
                        if exp.get("attention_analysis", True) and not permuted:
                            rec["attention"] = attention_lift(out["model"], Xt, test_graph, y_te, ds.classes, bs, seed)
                    rec["metrics"] = evaluate(y_te, np.asarray(y_pred), ds.classes, ds.benign_class,
                                              np.unique(y_tr).tolist(), int(scfg.get("min_class_support", 0)))
                    rec["seconds"] = time.time() - t0
                    log.info("RESULT %-28s %-16s fold=%d seed=%d bal_acc=%.4f macro_f1=%.4f", tag, pcfg["name"],
                             sp.fold, seed, rec["metrics"]["balanced_accuracy"], rec["metrics"]["macro_f1"])
                    _append(results_path, rec)
                    records.append(rec)
    return records


def main(argv: Optional[List[str]] = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True)
    ap.add_argument("--set", action="append", default=[], help="override, e.g. federated.rounds=5")
    ap.add_argument("--models", help="comma-separated subset of model names")
    ap.add_argument("--folds", help="comma-separated fold indices")
    ap.add_argument("--no-summary", action="store_true")
    args = ap.parse_args(argv)
    cfg = load_config(args.config, args.set)
    out_dir = Path(cfg.get("experiment", {}).get("results_dir", "results/fedflow"))
    out_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout),
                                  logging.FileHandler(out_dir / "run.log", encoding="utf-8")])
    run_grid(cfg, args.models.split(",") if args.models else None,
             [int(f) for f in args.folds.split(",")] if args.folds else None)
    if not args.no_summary:
        from .summarize import summarize
        summarize(out_dir / "results.jsonl", out_dir, cfg.get("summary", {}))


if __name__ == "__main__":
    main()
