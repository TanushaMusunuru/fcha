"""Synthetic NetFlow-v1-shaped data for tests and smoke runs (never used for reported results).

* ``noise``: features independent of the label. Any leak-free pipeline must score ~chance.
* ``mixed_host``: class-dependent traffic plus "mixed" hosts that send a majority class and a
  hidden minority class, mimicking the Backdoor-on-an-Injection-host situation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

COLUMNS = dict(src_ip="IPV4_SRC_ADDR", dst_ip="IPV4_DST_ADDR", src_port="L4_SRC_PORT",
               dst_port="L4_DST_PORT", protocol="PROTOCOL", in_bytes="IN_BYTES", out_bytes="OUT_BYTES",
               in_pkts="IN_PKTS", out_pkts="OUT_PKTS", duration="FLOW_DURATION_MILLISECONDS", label="Attack")


def make_flows(mode: str = "mixed_host", n_per_class: int = 400, n_classes: int = 5, n_hosts: int = 60,
               seed: int = 0) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    names = ["benign"] + [f"attack_{i}" for i in range(1, n_classes)]
    rows = []
    for c, name in enumerate(names):
        n = n_per_class if c < n_classes - 1 else max(20, n_per_class // 8)   # last class is rare
        if mode == "noise":
            shift, port = 0.0, rng.choice([22, 80, 443, 53, 8080], size=n)
            src = rng.randint(n_hosts, size=n)
        else:
            shift = 0.6 * c
            port = np.where(rng.rand(n) < 0.6, [22, 80, 443, 53, 8080, 21, 25][c % 7],
                            rng.choice([22, 80, 443, 53, 8080], size=n))
            # Each class has its own sender pool; the rare class shares host 0 with class 1.
            pool = np.arange(c * 3, c * 3 + 3) % n_hosts
            src = rng.choice(pool, size=n)
            if c == n_classes - 1:
                src = np.zeros(n, dtype=int)
            if c == 1:
                src = np.where(rng.rand(n) < 0.5, 0, src)
        in_b = np.exp(rng.normal(6 + shift, 1.0, n)).astype(int)
        out_b = np.exp(rng.normal(5 + 0.5 * shift, 1.0, n)).astype(int)
        rows.append(pd.DataFrame({
            "IPV4_SRC_ADDR": [f"10.0.{h // 250}.{h % 250}" for h in src],
            "L4_SRC_PORT": rng.randint(1024, 65535, size=n),
            "IPV4_DST_ADDR": [f"10.1.0.{h}" for h in rng.randint(n_hosts // 2, size=n)],
            "L4_DST_PORT": port,
            "PROTOCOL": rng.choice([6, 17], size=n),
            "L7_PROTO": rng.choice([0.0, 7.0, 91.0], size=n),
            "IN_BYTES": in_b, "OUT_BYTES": out_b,
            "IN_PKTS": np.maximum(1, in_b // rng.randint(40, 1500, size=n)),
            "OUT_PKTS": np.maximum(0, out_b // rng.randint(40, 1500, size=n)),
            "TCP_FLAGS": rng.randint(0, 64, size=n),
            "FLOW_DURATION_MILLISECONDS": rng.randint(0, 5000, size=n),
            "Label": int(c != 0), "Attack": name,
        }))
    return pd.concat(rows, ignore_index=True).sample(frac=1.0, random_state=seed).reset_index(drop=True)
