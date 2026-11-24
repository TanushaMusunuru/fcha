"""Fully federated training of an edge classifier (no centrally trained stage).

What leaves a client: model weights (FedAvg/FedProx), feature moments (count, sum, sum of squares)
for standardisation, and per-round validation confusion counts for model selection. Raw flows,
labels of individual flows and host identities never leave a client.
"""
from __future__ import annotations

import copy
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np
import torch
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import StratifiedGroupKFold

from .data import combine_moments, moments
from .graph import FlowGraph
from .models import build_model, class_weights, classification_loss, supcon_loss

log = logging.getLogger("fedflow")


@dataclass
class Client:
    X: torch.Tensor          # standardised features of all local flows
    y: torch.Tensor          # labels (used only on train_idx for training, val_idx for selection)
    graph: FlowGraph
    train_idx: torch.Tensor
    val_idx: torch.Tensor


def local_val_split(y: np.ndarray, groups: Optional[np.ndarray], frac: float, seed: int):
    """Hold out ``frac`` of a client's flows for validation, grouped by flow signature when given."""
    n_splits = max(2, int(round(1.0 / frac)))
    g = groups if groups is not None else np.arange(len(y))
    counts = np.bincount(y)
    if len(y) < n_splits or counts[counts > 0].min() < n_splits:
        # Too few flows of some class for grouped folds: per-class random hold-out instead.
        rng = np.random.RandomState(seed)
        va = []
        for c in np.unique(y):
            idx = rng.permutation(np.where(y == c)[0])
            va.extend(idx[: int(len(idx) * frac)].tolist())
        va = np.sort(np.asarray(va, dtype=np.int64))
        return np.setdiff1d(np.arange(len(y)), va), va
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    tr, va = next(sgkf.split(np.zeros(len(y)), y, groups=g))
    return tr, va


def make_clients(X_parts: List[np.ndarray], y_parts: List[np.ndarray], src_parts, dst_parts,
                 groups_parts, tcfg: Dict[str, Any], seed: int, device) -> tuple[List[Client], np.ndarray, np.ndarray]:
    """Builds clients; standardisation statistics come only from clients' training rows."""
    splits = [local_val_split(y, g, float(tcfg.get("val_fraction", 0.1)), seed + i)
              for i, (y, g) in enumerate(zip(y_parts, groups_parts))]
    mean, std = combine_moments([moments(X[tr]) for X, (tr, _) in zip(X_parts, splits)])
    clients = []
    for X, y, s, d, (tr, va) in zip(X_parts, y_parts, src_parts, dst_parts, splits):
        Xs = torch.as_tensor((X - mean) / std, dtype=torch.float32, device=device)
        clients.append(Client(Xs, torch.as_tensor(y, device=device), FlowGraph(s, d, device),
                              torch.as_tensor(tr, device=device), torch.as_tensor(va, device=device)))
    return clients, mean, std


def _batches(idx: torch.Tensor, y: torch.Tensor, batch_size: int, balanced: bool,
             gen: torch.Generator, max_steps: Optional[int]):
    n = idx.numel()
    if balanced:
        yl = y[idx]
        counts = torch.bincount(yl).float()
        w = (1.0 / counts.clamp(min=1))[yl]
        order = idx[torch.multinomial(w.cpu(), n, replacement=True, generator=gen).to(idx.device)]
    else:
        order = idx[torch.randperm(n, generator=gen).to(idx.device)]
    steps = 0
    for s in range(0, n, batch_size):
        if max_steps and steps >= max_steps:
            break
        yield order[s:s + batch_size]
        steps += 1


@torch.no_grad()
def predict(model, X: torch.Tensor, graph: FlowGraph, idx: torch.Tensor, batch_size: int,
            seed: int, samples: int = 1) -> np.ndarray:
    """Class probabilities; neighbour sampling is seeded, and can be averaged over ``samples`` draws."""
    model.eval()
    gen = torch.Generator().manual_seed(seed)
    out = []
    for s in range(0, idx.numel(), batch_size):
        b = idx[s:s + batch_size]
        p = sum(torch.softmax(model(X, graph, b, gen)[0], dim=1) for _ in range(samples)) / samples
        out.append(p.cpu())
    return torch.cat(out).numpy() if out else np.zeros((0, 0))


def param_bytes(model) -> int:
    return sum(p.numel() * p.element_size() for p in model.state_dict().values())


def train_federated(clients: List[Client], mcfg: Dict[str, Any], tcfg: Dict[str, Any],
                    in_dim: int, n_classes: int, seed: int, device) -> Dict[str, Any]:
    torch.manual_seed(seed)
    np.random.seed(seed)
    gen = torch.Generator().manual_seed(seed)
    global_model = build_model(mcfg, in_dim, n_classes).to(device)
    rounds = int(tcfg.get("rounds", 20))
    local_epochs = int(tcfg.get("local_epochs", 1))
    bs = int(tcfg.get("batch_size", 512))
    max_steps = tcfg.get("max_steps_per_epoch")
    frac = float(tcfg.get("client_fraction", 1.0))
    prox_mu = float(tcfg.get("fedprox_mu", 0.0))
    loss_cfg = mcfg.get("loss", {}) or {}
    supcon_w = float(loss_cfg.get("supcon_weight", 0.0))
    patience = int(tcfg.get("early_stopping_patience", 0) or 0)

    best = {"score": -1.0, "round": -1, "state": copy.deepcopy(global_model.state_dict())}
    history, comm, t0 = [], 0, time.time()
    pbytes = param_bytes(global_model)
    rng = np.random.RandomState(seed)
    for r in range(rounds):
        m = max(1, int(round(frac * len(clients))))
        chosen = sorted(rng.choice(len(clients), size=m, replace=False).tolist())
        states, sizes, losses = [], [], []
        for ci in chosen:
            c = clients[ci]
            local = copy.deepcopy(global_model)
            local.train()
            opt = torch.optim.AdamW(local.parameters(), lr=float(tcfg.get("lr", 1e-3)),
                                    weight_decay=float(tcfg.get("weight_decay", 1e-4)))
            counts = torch.bincount(c.y[c.train_idx], minlength=n_classes)
            w = class_weights(counts, loss_cfg.get("class_weights", "none"), float(loss_cfg.get("cb_beta", 0.9999)))
            w = w.to(device) if w is not None else None
            ref = [p.detach().clone() for p in global_model.parameters()] if prox_mu > 0 else None
            for _ in range(local_epochs):
                for b in _batches(c.train_idx, c.y, bs, bool(tcfg.get("balanced_sampling", False)), gen, max_steps):
                    logits, z = local(c.X, c.graph, b, gen)
                    yb = c.y[b]
                    loss = classification_loss(logits, yb, w, float(loss_cfg.get("focal_gamma", 0.0)))
                    if supcon_w > 0:
                        loss = loss + supcon_w * supcon_loss(z, yb, float(loss_cfg.get("supcon_temperature", 0.1)))
                    if ref is not None:
                        loss = loss + prox_mu / 2 * sum(((p - q) ** 2).sum() for p, q in zip(local.parameters(), ref))
                    opt.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(local.parameters(), float(tcfg.get("grad_clip", 5.0)))
                    opt.step()
                    losses.append(float(loss.detach()))
            states.append(local.state_dict())
            sizes.append(int(c.train_idx.numel()))
        total = float(sum(sizes))
        global_model.load_state_dict({k: sum(s[k].float() * (n / total) for s, n in zip(states, sizes)).to(states[0][k].dtype)
                                      for k in states[0]})
        comm += 2 * pbytes * len(chosen)

        # Server-side model selection from pooled client validation predictions (clients would
        # send confusion counts; balanced accuracy is computed from them).
        ys, ps = [], []
        for ci, c in enumerate(clients):
            if c.val_idx.numel() == 0:
                continue
            p = predict(global_model, c.X, c.graph, c.val_idx, int(tcfg.get("eval_batch_size", 4096)), seed + 1000 + ci)
            ys.append(c.y[c.val_idx].cpu().numpy())
            ps.append(p.argmax(1))
        score = float(balanced_accuracy_score(np.concatenate(ys), np.concatenate(ps))) if ys else float(r)
        history.append({"round": r + 1, "train_loss": float(np.mean(losses)) if losses else None, "val_bal_acc": score})
        log.info("round %d/%d  loss=%.4f  val_bal_acc=%.4f", r + 1, rounds, history[-1]["train_loss"] or 0, score)
        if score > best["score"]:
            best = {"score": score, "round": r + 1, "state": copy.deepcopy(global_model.state_dict())}
        elif patience and r + 1 - best["round"] >= patience:
            log.info("early stopping at round %d (best %d)", r + 1, best["round"])
            break
    global_model.load_state_dict(best["state"])
    return {"model": global_model, "best_round": best["round"], "best_val_bal_acc": best["score"],
            "history": history, "comm_bytes": int(comm), "param_bytes": int(pbytes),
            "train_seconds": time.time() - t0}
