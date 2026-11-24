"""Flow graph: hosts are nodes, flows are edges. Stores, for every host, the list of flows incident
to it (CSR), and samples up to ``k`` incident flows per query flow and endpoint.

Only a client's own flows go into its graph; the test graph contains only test flows (unlabelled
traffic observed at inference time). Labels are never stored here.
"""
from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
import torch


class FlowGraph:
    def __init__(self, src: np.ndarray, dst: np.ndarray, device: torch.device | str = "cpu"):
        ids, inv = np.unique(np.concatenate([src, dst]), return_inverse=True)
        e = len(src)
        lsrc, ldst = inv[:e], inv[e:]
        host = np.concatenate([lsrc, ldst])
        flow = np.concatenate([np.arange(e), np.arange(e)])
        role = np.concatenate([np.zeros(e, dtype=np.int64), np.ones(e, dtype=np.int64)])
        order = np.argsort(host, kind="stable")
        deg = np.bincount(host, minlength=len(ids))
        rowptr = np.zeros(len(ids) + 1, dtype=np.int64)
        rowptr[1:] = np.cumsum(deg)
        t = lambda a: torch.as_tensor(np.ascontiguousarray(a), dtype=torch.long, device=device)  # noqa: E731
        self.num_flows = e
        self.num_hosts = len(ids)
        self.host_ids = ids                      # global host id of each local host
        self.src, self.dst = t(lsrc), t(ldst)    # local host index of each flow's endpoints
        self.inc_flow = t(flow[order])           # incident flow ids grouped by host
        self.inc_role = t(role[order])           # 0: host is the sender of that flow, 1: receiver
        self.rowptr, self.deg = t(rowptr), t(deg)
        self.device = device

    def sample(self, flows: torch.Tensor, side: int, k: int,
               gen: Optional[torch.Generator] = None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """For each query flow, up to ``k`` other flows incident to its sender (side 0) or receiver
        (side 1). Hosts with at most ``k`` flows are enumerated exactly; larger ones are sampled
        uniformly with replacement. Returns (neighbour flow ids, host role in them, validity mask)."""
        host = self.src[flows] if side == 0 else self.dst[flows]
        start, deg = self.rowptr[host], self.deg[host]
        b = flows.shape[0]
        ar = torch.arange(k, device=flows.device).expand(b, k)
        r = torch.rand((b, k), generator=gen).to(flows.device)
        rand_off = (r * deg.unsqueeze(1).clamp(min=1)).long()
        small = (deg <= k).unsqueeze(1)
        off = torch.where(small, ar, rand_off)
        valid = (~small) | (ar < deg.unsqueeze(1))
        pos = (start.unsqueeze(1) + off).clamp(max=max(self.inc_flow.numel() - 1, 0))
        nbr = self.inc_flow[pos]
        role = self.inc_role[pos]
        valid = valid & (nbr != flows.unsqueeze(1))
        return nbr, role, valid
