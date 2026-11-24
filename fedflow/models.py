"""Edge (flow) classifiers sharing one code path, so baselines and the proposed model differ only in
the context aggregator.

* ``aggregator: attention`` + ``use_self: true``  -> FCHA, the proposed Flow-Conditioned Host
  Attention model. The flow being classified is the attention *query* over the other flows of
  its sender and of its receiver, so on a host that mixes traffic classes the context is built
  mainly from flows that resemble the query instead of being averaged over all of them.
* ``aggregator: mean``      + ``use_self: true``  -> E-GraphSAGE-style host mean + own features.
* ``aggregator: mean``      + ``use_self: false`` -> host-mean only (the aggregation that hides
  minority classes in the original GAT pipeline).
* ``aggregator: none``                            -> flow-only MLP (true edge-only baseline).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

from .graph import FlowGraph


class FlowEncoder(nn.Module):
    def __init__(self, in_dim: int, hidden: int, dropout: float):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.LayerNorm(hidden), nn.GELU(),
                                 nn.Dropout(dropout), nn.Linear(hidden, hidden))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class EdgeClassifier(nn.Module):
    def __init__(self, in_dim: int, n_classes: int, hidden: int = 128, heads: int = 4,
                 neighbors: int = 16, aggregator: str = "attention", use_self: bool = True,
                 dropout: float = 0.1):
        super().__init__()
        if aggregator not in ("attention", "mean", "none"):
            raise ValueError(f"aggregator must be attention, mean or none, got {aggregator!r}")
        if aggregator == "none" and not use_self:
            raise ValueError("aggregator 'none' needs use_self: true")
        if aggregator == "attention" and hidden % heads:
            raise ValueError("hidden must be divisible by heads")
        self.aggregator, self.use_self = aggregator, use_self
        self.k, self.heads, self.hidden = neighbors, heads, hidden
        self.enc = FlowEncoder(in_dim, hidden, dropout)
        n_parts = int(use_self)
        if aggregator != "none":
            self.role = nn.Embedding(2, hidden)    # is the host the sender or receiver of the neighbour flow
            self.side = nn.Embedding(2, hidden)    # are we looking at the query's sender or receiver
            self.ctx_out = nn.Linear(hidden, hidden)
            n_parts += 2
            if aggregator == "attention":
                self.q = nn.Linear(hidden, hidden)
                self.kv = nn.Linear(hidden, 2 * hidden)
        self.head = nn.Sequential(nn.Linear(n_parts * hidden, hidden), nn.LayerNorm(hidden), nn.GELU(),
                                  nn.Dropout(dropout), nn.Linear(hidden, hidden))
        self.cls = nn.Linear(hidden, n_classes)

    def _context(self, h_q, X, graph: FlowGraph, flows, side: int, gen):
        nbr, role, valid = graph.sample(flows, side, self.k, gen)
        b, k = nbr.shape
        h_n = self.enc(X[nbr.reshape(-1)]).view(b, k, -1) + self.role(role)
        side_vec = self.side.weight[side]
        if self.aggregator == "mean":
            w = valid.float()
            ctx = (h_n * w.unsqueeze(-1)).sum(1) / w.sum(1, keepdim=True).clamp(min=1.0)
            attn = w / w.sum(1, keepdim=True).clamp(min=1.0)
        else:
            dh = self.hidden // self.heads
            q = self.q(h_q + side_vec).view(b, self.heads, dh)
            kk, vv = self.kv(h_n + side_vec).view(b, k, 2, self.heads, dh).unbind(2)
            scores = torch.einsum("bhd,bkhd->bhk", q, kk) / math.sqrt(dh)
            scores = scores.masked_fill(~valid.unsqueeze(1), float("-inf"))
            attn_h = torch.softmax(scores, dim=-1)
            attn_h = torch.nan_to_num(attn_h, nan=0.0)          # hosts with no other flow
            ctx = torch.einsum("bhk,bkhd->bhd", attn_h, vv).reshape(b, -1)
            attn = attn_h.mean(1)
        return self.ctx_out(ctx), attn, nbr, valid

    def forward(self, X: torch.Tensor, graph: FlowGraph, flows: torch.Tensor,
                gen: Optional[torch.Generator] = None, return_attention: bool = False):
        h = self.enc(X[flows])
        parts: List[torch.Tensor] = [h] if self.use_self else []
        extras: Dict[str, Any] = {}
        if self.aggregator != "none":
            for side in (0, 1):
                ctx, attn, nbr, valid = self._context(h, X, graph, flows, side, gen)
                parts.append(ctx)
                if return_attention:
                    extras[side] = (attn.detach(), nbr, valid)
        z = self.head(torch.cat(parts, dim=1))
        logits = self.cls(z)
        return (logits, z, extras) if return_attention else (logits, z)


def build_model(mcfg: Dict[str, Any], in_dim: int, n_classes: int) -> EdgeClassifier:
    return EdgeClassifier(in_dim=in_dim, n_classes=n_classes,
                          hidden=int(mcfg.get("hidden", 128)), heads=int(mcfg.get("heads", 4)),
                          neighbors=int(mcfg.get("neighbors", 16)),
                          aggregator=mcfg.get("aggregator", "attention"),
                          use_self=bool(mcfg.get("use_self", True)),
                          dropout=float(mcfg.get("dropout", 0.1)))


# --------------------------------------------------------------------------- losses

def class_weights(counts: torch.Tensor, scheme: str, beta: float = 0.9999) -> Optional[torch.Tensor]:
    """Per-class weights from *local* counts (each client uses only its own label counts)."""
    if scheme in (None, "none"):
        return None
    c = counts.float().clamp(min=1)
    if scheme == "inverse":
        w = 1.0 / c
    elif scheme == "sqrt_inverse":          # milder: a 100x rarer class gets 10x the weight
        w = 1.0 / c.sqrt()
    elif scheme == "effective_number":
        w = (1 - beta) / (1 - beta ** c)
    else:
        raise ValueError(f"Unknown class weight scheme {scheme!r}")
    w = w * (counts > 0).float()
    return w / w[counts > 0].sum() * (counts > 0).sum()


def classification_loss(logits, y, weights=None, focal_gamma: float = 0.0) -> torch.Tensor:
    ce = F.cross_entropy(logits, y, weight=weights, reduction="none")
    if focal_gamma > 0:
        pt = torch.exp(-F.cross_entropy(logits, y, reduction="none"))   # unweighted p_t
        ce = (1 - pt) ** focal_gamma * ce
    if weights is not None:
        return ce.sum() / weights[y].sum().clamp(min=1e-8)
    return ce.mean()


def supcon_loss(z: torch.Tensor, y: torch.Tensor, temperature: float = 0.1) -> torch.Tensor:
    """Supervised contrastive loss (Khosla et al., 2020), averaged over anchors with positives."""
    z = F.normalize(z, dim=1)
    sim = z @ z.T / temperature
    n = z.shape[0]
    eye = torch.eye(n, dtype=torch.bool, device=z.device)
    sim = sim.masked_fill(eye, float("-inf"))
    log_prob = sim - torch.logsumexp(sim, dim=1, keepdim=True)
    pos = (y.unsqueeze(0) == y.unsqueeze(1)) & ~eye
    n_pos = pos.sum(1)
    ok = n_pos > 0
    if not ok.any():
        return z.sum() * 0.0
    per = -(log_prob.masked_fill(~pos, 0.0)).sum(1)[ok] / n_pos[ok]
    return per.mean()
