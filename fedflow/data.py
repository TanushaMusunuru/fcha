"""Dataset loading, schema mapping and leak-safe feature construction.

Nothing here knows about a particular dataset: column roles, classes to keep and feature
options all come from the ``dataset`` and ``features`` sections of the config.
"""
from __future__ import annotations

import glob
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

log = logging.getLogger("fedflow")

ROLE_KEYS = ("src_ip", "dst_ip", "label")


@dataclass
class FlowDataset:
    """Flows with integer labels and integer host ids. ``frame`` keeps the raw feature columns."""

    frame: pd.DataFrame
    classes: List[str]
    roles: Dict[str, str]
    name: str
    benign_class: Optional[str] = None
    hosts: List[str] = field(default_factory=list)

    @property
    def y(self) -> np.ndarray:
        return self.frame["_y"].to_numpy()

    @property
    def src(self) -> np.ndarray:
        return self.frame["_src"].to_numpy()

    @property
    def dst(self) -> np.ndarray:
        return self.frame["_dst"].to_numpy()

    def subset(self, idx: np.ndarray) -> "FlowDataset":
        return FlowDataset(self.frame.iloc[idx].reset_index(drop=True), self.classes, self.roles,
                           self.name, self.benign_class, self.hosts)

    def __len__(self) -> int:
        return len(self.frame)


def locate_file(dcfg: Dict[str, Any]) -> Path:
    if dcfg.get("path"):
        p = Path(dcfg["path"])
        if not p.exists():
            raise FileNotFoundError(f"dataset.path does not exist: {p}")
        return p
    for pattern in dcfg.get("search", []) or []:
        hits = sorted(glob.glob(pattern, recursive=True))
        if hits:
            return Path(hits[0])
    raise FileNotFoundError(
        f"Dataset '{dcfg.get('name')}' not found. Set dataset.path or add a matching dataset.search glob.")


def _label_key(series: pd.Series, dcfg: Dict[str, Any]) -> pd.Series:
    """Normalised class label. ``dataset.class_map`` (raw label -> class name, from the config)
    merges fine-grained labels into families; unmapped labels keep their own name."""
    s = series.astype(str).str.strip()
    lower = dcfg.get("lowercase_labels", True)
    if lower:
        s = s.str.lower()
    cmap = dcfg.get("class_map") or {}
    if cmap:
        cmap = {(k.strip().lower() if lower else k.strip()): (v.lower() if lower else v) for k, v in cmap.items()}
        s = s.map(lambda v: cmap.get(v, v))
    return s


def read_table(path: Path, dcfg: Dict[str, Any], label_col: str) -> pd.DataFrame:
    """Read a CSV or Parquet file. With ``dataset.class_cap`` set, keep at most that many randomly
    chosen flows per class: pass 1 reads only the label column, pass 2 streams the file in chunks
    and keeps only the chosen rows, so the full file never has to fit in memory."""
    is_parquet = path.suffix.lower() == ".parquet"
    cap = dcfg.get("class_cap")
    if not cap:
        return pd.read_parquet(path) if is_parquet else pd.read_csv(path, low_memory=False)

    if is_parquet:
        labels = pd.read_parquet(path, columns=[label_col])[label_col]
    else:
        labels = pd.read_csv(path, usecols=[label_col])[label_col]
    key = _label_key(labels, dcfg).to_numpy()
    rng = np.random.RandomState(int(dcfg.get("subsample_seed", 0)))
    keep = np.zeros(len(key), dtype=bool)
    for c in np.unique(key):
        idx = np.where(key == c)[0]
        if len(idx) > int(cap):
            idx = rng.choice(idx, size=int(cap), replace=False)
        keep[idx] = True
    log.warning("dataset.class_cap=%s: keeping %d of %d flows (per class: at most %s, chosen at random)",
                cap, int(keep.sum()), len(keep), cap)

    parts, offset = [], 0
    chunk = int(dcfg.get("read_chunk_rows", 1_000_000))
    if is_parquet:
        import pyarrow.parquet as pq
        for batch in pq.ParquetFile(path).iter_batches(batch_size=chunk):
            m = keep[offset: offset + batch.num_rows]
            if m.any():
                parts.append(batch.to_pandas()[m])
            offset += batch.num_rows
    else:
        for df in pd.read_csv(path, chunksize=chunk, low_memory=False):
            m = keep[offset: offset + len(df)]
            if m.any():
                parts.append(df[m])
            offset += len(df)
    return pd.concat(parts, ignore_index=True)


def load_dataset(dcfg: Dict[str, Any], frame: Optional[pd.DataFrame] = None) -> FlowDataset:
    """Load the CSV (or use ``frame``), map roles, filter classes, encode labels and hosts."""
    roles = dict(dcfg["columns"])
    for key in ROLE_KEYS:
        if key not in roles:
            raise KeyError(f"dataset.columns must define '{key}'")
    if frame is None:
        path = locate_file(dcfg)
        log.info("Loading %s from %s", dcfg.get("name"), path)
        frame = read_table(path, dcfg, roles["label"])
    df = frame.copy()
    missing = [c for k, c in roles.items() if c not in df.columns]
    if missing:
        raise KeyError(f"Columns named in dataset.columns are missing from the data: {missing}")

    drop = [c for c in dcfg.get("drop_columns", []) or [] if c in df.columns]
    df = df.drop(columns=drop)

    df["_label"] = _label_key(df[roles["label"]], dcfg)

    include = dcfg.get("include_classes")
    if include:
        keep = {c.lower() if dcfg.get("lowercase_labels", True) else c for c in include}
        df = df[df["_label"].isin(keep)]
    for c in dcfg.get("drop_classes", []) or []:
        c = c.lower() if dcfg.get("lowercase_labels", True) else c
        df = df[df["_label"] != c]
    min_count = int(dcfg.get("min_class_count", 0) or 0)
    if min_count:
        counts = df["_label"].value_counts()
        rare = counts[counts < min_count].index.tolist()
        if rare:
            log.warning("Dropping classes with fewer than %d flows: %s", min_count, rare)
            df = df[~df["_label"].isin(rare)]

    max_rows = dcfg.get("max_rows")
    if max_rows and len(df) > int(max_rows):
        # Stratified subsample, only for quick runs; logged so it is never silent.
        frac = int(max_rows) / len(df)
        df = df.groupby("_label", group_keys=False).sample(frac=frac, random_state=int(dcfg.get("subsample_seed", 0)))
        log.warning("Subsampled to %d rows (dataset.max_rows)", len(df))

    df = df.reset_index(drop=True)
    classes = sorted(df["_label"].unique().tolist())
    df["_y"] = df["_label"].map({c: i for i, c in enumerate(classes)}).astype(np.int64)

    ips = pd.concat([df[roles["src_ip"]].astype(str), df[roles["dst_ip"]].astype(str)])
    codes, uniques = pd.factorize(ips)
    df["_src"] = codes[: len(df)].astype(np.int64)
    df["_dst"] = codes[len(df):].astype(np.int64)

    benign = dcfg.get("benign_class")
    if benign and dcfg.get("lowercase_labels", True):
        benign = benign.lower()
    if benign not in classes:
        benign = None
    log.info("Dataset %s: %d flows, %d hosts, classes=%s", dcfg.get("name"), len(df), len(uniques), classes)
    return FlowDataset(df, classes, roles, dcfg.get("name", "dataset"), benign, list(map(str, uniques)))


# --------------------------------------------------------------------------- signatures

def flow_signatures(ds: FlowDataset, scfg: Dict[str, Any]) -> np.ndarray:
    """Integer id per flow signature. ``binning: log2`` merges near-identical numeric values so the
    grouped split also separates near-duplicates, not only exact duplicates."""
    cols = scfg.get("columns") or []
    cols = [ds.roles.get(c, c) for c in cols]
    missing = [c for c in cols if c not in ds.frame.columns]
    if missing:
        raise KeyError(f"signature.columns not in data: {missing}")
    parts = []
    binned = set(ds.roles.get(c, c) for c in scfg.get("binned_columns", []) or [])
    for c in cols:
        v = ds.frame[c]
        if scfg.get("binning", "none") == "log2" and c in binned and pd.api.types.is_numeric_dtype(v):
            v = np.floor(np.log2(np.maximum(v.to_numpy(dtype=float), 0) + 1)).astype(np.int64)
            v = pd.Series(v)
        parts.append(pd.Series(v).astype(str).reset_index(drop=True))
    key = parts[0].str.cat(parts[1:], sep="|") if len(parts) > 1 else parts[0]
    return pd.factorize(key)[0].astype(np.int64)


def cap_duplicates(ds: FlowDataset, scfg: Dict[str, Any], max_copies: int, seed: int = 0) -> Tuple[FlowDataset, Dict[str, Any]]:
    """Keep at most ``max_copies`` randomly chosen flows per identical flow signature.

    NetFlow benchmarks repeat the same flow thousands of times (one attack tool, one signature).
    Such groups cannot be divided across folds, which skews class shares per fold, and they
    inflate scores. Returns the reduced dataset and a per-class before/after report."""
    groups = flow_signatures(ds, scfg)
    order = np.random.RandomState(seed).permutation(len(groups))
    keep = pd.DataFrame({"g": groups[order], "i": order}).groupby("g", sort=False).head(int(max_copies))["i"].to_numpy()
    keep = np.sort(keep)
    before = np.bincount(ds.y, minlength=len(ds.classes))
    out = ds.subset(keep)
    after = np.bincount(out.y, minlength=len(ds.classes))
    report = {"max_copies": int(max_copies), "flows_before": int(len(ds)), "flows_after": int(len(out)),
              "per_class": {c: {"before": int(b), "after": int(a)} for c, b, a in zip(ds.classes, before, after)}}
    log.warning("Duplicate cap %d: %d -> %d flows; per class %s", max_copies, len(ds), len(out),
                {c: f"{b}->{a}" for c, b, a in zip(ds.classes, before, after)})
    return out, report


# --------------------------------------------------------------------------- features

class FeatureBuilder:
    """Turns raw flow columns into a numeric matrix. Category vocabularies are learned with
    :meth:`fit` on training data only; identity and label columns are never features."""

    def __init__(self, fcfg: Dict[str, Any], ds: FlowDataset):
        self.cfg = fcfg
        self.roles = ds.roles
        self.forbidden = {ds.roles["label"], ds.roles["src_ip"], ds.roles["dst_ip"],
                          "_label", "_y", "_src", "_dst"}
        self.forbidden |= set(fcfg.get("exclude_columns", []) or [])
        self.categorical = [self._col(c) for c in fcfg.get("categorical_columns", []) or []]
        self.ports = [self._col(c) for c in fcfg.get("port_columns", []) or []]
        self.bitmasks = {self._col(k): int(v) for k, v in (fcfg.get("bitmask_columns") or {}).items()}
        self.vocab: Dict[str, List[Any]] = {}
        self.numeric: List[str] = []
        self.names: List[str] = []

    def _col(self, c: str) -> str:
        return self.roles.get(c, c)

    def fit(self, frame: pd.DataFrame, y: Optional[np.ndarray] = None) -> "FeatureBuilder":
        special = set(self.categorical) | set(self.ports) | set(self.bitmasks)
        self.numeric = [c for c in frame.columns
                        if c not in self.forbidden and c not in special and not c.startswith("_")
                        and pd.api.types.is_numeric_dtype(frame[c])]
        top_k = int(self.cfg.get("categorical_top_k", 16))
        for c in self.categorical:
            self.vocab[c] = frame[c].value_counts().head(top_k).index.tolist()
        self.names = self._names()
        self.assert_no_leak()
        if y is not None and self.cfg.get("leak_scan", "error") != "off":
            self.leak_scan(frame, y)
        return self

    def leak_scan(self, frame: pd.DataFrame, y: np.ndarray) -> None:
        """Reject any low-cardinality input column that is (almost) a deterministic function of the
        label, e.g. a forgotten binary attack flag. H(col | y) ~ 0 while H(col) > 0 means the column
        only restates the label."""
        n_classes = len(np.unique(y))
        suspects = []
        for c in self.numeric + self.categorical + list(self.bitmasks):
            v = frame[c].to_numpy()
            uniq = pd.unique(v)
            if len(uniq) < 2 or len(uniq) > 2 * n_classes:
                continue
            joint = pd.crosstab(pd.Series(y, name="y"), pd.Series(v, name="v")).to_numpy().astype(float)
            p = joint / joint.sum()
            pv = p.sum(0)
            py = p.sum(1, keepdims=True)
            h_v = -np.sum(pv[pv > 0] * np.log(pv[pv > 0]))
            cond = p / np.maximum(py, 1e-12)
            h_v_given_y = -np.sum(p[p > 0] * np.log(cond[p > 0]))
            if h_v > 0 and h_v_given_y < 0.01 * h_v:
                suspects.append(c)
        if suspects:
            msg = (f"Columns {suspects} are deterministic functions of the label (label leakage). "
                   "Add them to dataset.drop_columns, or set features.leak_scan to 'warn' if intended.")
            if self.cfg.get("leak_scan", "error") == "error":
                raise AssertionError(msg)
            log.warning(msg)

    def _names(self) -> List[str]:
        names = [f"num:{c}" for c in self.numeric]
        for c in self.ports:
            names += [f"port:{c}:{b}" for b in ("wellknown", "registered", "ephemeral")]
        for c, bits in self.bitmasks.items():
            names += [f"bit:{c}:{i}" for i in range(bits)]
        for c in self.categorical:
            names += [f"cat:{c}={v}" for v in self.vocab[c]] + [f"cat:{c}=other"]
        if self.cfg.get("derived", True):
            names += [f"derived:{n}" for n in self._derived_names()]
        return names

    def _derived_names(self) -> List[str]:
        r = self.roles
        out = []
        if "in_bytes" in r and "out_bytes" in r:
            out.append("byte_asymmetry")
        if "in_pkts" in r and "out_pkts" in r:
            out.append("pkt_asymmetry")
        if all(k in r for k in ("in_bytes", "out_bytes", "in_pkts", "out_pkts")):
            out.append("log_bytes_per_pkt")
        if all(k in r for k in ("in_bytes", "out_bytes", "duration")):
            out.append("log_byte_rate")
        return out

    def assert_no_leak(self) -> None:
        bad = [n for n in self.names if any(n.split(":", 1)[1].split(":")[0].split("=")[0] == f
                                            for f in self.forbidden)]
        if bad:
            raise AssertionError(f"Label/identity columns leaked into features: {bad}")

    def transform(self, frame: pd.DataFrame) -> np.ndarray:
        cols = []
        if self.numeric:
            x = frame[self.numeric].to_numpy(dtype=np.float64)
            x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
            if self.cfg.get("log_transform", True):
                x = np.sign(x) * np.log1p(np.abs(x))
            cols.append(x)
        bounds = self.cfg.get("port_bounds", [1024, 49152])
        for c in self.ports:
            p = frame[c].to_numpy(dtype=np.float64)
            cols.append(np.stack([p < bounds[0], (p >= bounds[0]) & (p < bounds[1]), p >= bounds[1]], 1))
        for c, bits in self.bitmasks.items():
            v = np.nan_to_num(frame[c].to_numpy(dtype=np.float64)).astype(np.int64)
            cols.append(np.stack([(v >> i) & 1 for i in range(bits)], 1))
        for c in self.categorical:
            v = frame[c].to_numpy()
            vocab = self.vocab[c]
            oh = np.zeros((len(frame), len(vocab) + 1))
            hit = np.zeros(len(frame), dtype=bool)
            for j, val in enumerate(vocab):
                m = v == val
                oh[m, j] = 1
                hit |= m
            oh[~hit, -1] = 1
            cols.append(oh)
        if self.cfg.get("derived", True):
            cols.append(self._derived(frame))
        X = np.concatenate([np.asarray(c, dtype=np.float64).reshape(len(frame), -1) for c in cols], axis=1)
        return X.astype(np.float32)

    def _derived(self, frame: pd.DataFrame) -> np.ndarray:
        r = self.roles
        g = lambda k: np.nan_to_num(frame[r[k]].to_numpy(dtype=np.float64))  # noqa: E731
        out = []
        names = self._derived_names()
        if "byte_asymmetry" in names:
            a, b = g("in_bytes"), g("out_bytes")
            out.append((a - b) / (a + b + 1.0))
        if "pkt_asymmetry" in names:
            a, b = g("in_pkts"), g("out_pkts")
            out.append((a - b) / (a + b + 1.0))
        if "log_bytes_per_pkt" in names:
            out.append(np.log1p((g("in_bytes") + g("out_bytes")) / (g("in_pkts") + g("out_pkts") + 1.0)))
        if "log_byte_rate" in names:
            scale = float(self.cfg.get("duration_to_seconds", 1e-3))
            out.append(np.log1p((g("in_bytes") + g("out_bytes")) / (g("duration") * scale + 1e-3)))
        return np.stack(out, 1) if out else np.zeros((len(frame), 0))


# --------------------------------------------------------------------------- moments

def moments(X: np.ndarray) -> Tuple[int, np.ndarray, np.ndarray]:
    """Sufficient statistics a client can share for federated standardisation."""
    X = X.astype(np.float64)
    return len(X), X.sum(0), (X ** 2).sum(0)


def combine_moments(stats: Sequence[Tuple[int, np.ndarray, np.ndarray]]) -> Tuple[np.ndarray, np.ndarray]:
    n = sum(s[0] for s in stats)
    s1 = sum(s[1] for s in stats)
    s2 = sum(s[2] for s in stats)
    mean = s1 / max(n, 1)
    var = np.maximum(s2 / max(n, 1) - mean ** 2, 0.0)
    return mean.astype(np.float32), (np.sqrt(var) + 1e-6).astype(np.float32)
