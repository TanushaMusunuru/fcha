"""FedFlow tests on synthetic data.  Run:  python -m unittest tests.test_fedflow -v"""
import json
import logging
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from fedflow.config import load_config, set_by_path
from fedflow.data import FeatureBuilder, load_dataset
from fedflow.graph import FlowGraph
from fedflow.models import EdgeClassifier
from fedflow.partition import partition
from fedflow.run import run_grid
from fedflow.splits import iter_splits
from fedflow.synthetic import make_flows

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs" / "fedflow" / "nf_ton_iot.yaml"
logging.getLogger("fedflow").setLevel(logging.WARNING)


def quick_cfg(tmp, models, extra=()):
    over = ["federated.rounds=4", "federated.max_steps_per_epoch=25", "federated.num_clients=3",
            "federated.batch_size=128", "federated.early_stopping_patience=0",
            "experiment.seeds=[0]", "experiment.folds=[0]", f"experiment.results_dir={tmp}",
            "experiment.sanity_permuted_labels=false", "dataset.drop_classes=[]",
            "splits=[{type: signature, n_folds: 4, seed: 0}]",
            "partitions=[{name: iid, type: iid}]", "dataset.lowercase_labels=true"]
    cfg = load_config(CFG, list(over) + list(extra))
    cfg["models"] = {k: cfg["models"][k] for k in models}
    return cfg


class TestLeakage(unittest.TestCase):
    def test_noise_scores_chance(self):
        """Features carry no information: every model must stay near chance (5 classes -> 20%)."""
        df = make_flows("noise", n_per_class=300, seed=1)
        with tempfile.TemporaryDirectory() as tmp:
            recs = run_grid(quick_cfg(tmp, ["fcha", "random_forest"]), frame=df)
        for r in recs:
            self.assertLess(r["metrics"]["balanced_accuracy"], 0.35, r["model"])

    def test_binary_label_column_is_rejected(self):
        df = make_flows("noise", n_per_class=100, seed=2)
        cfg = load_config(CFG, ["dataset.drop_columns=[]", "dataset.drop_classes=[]"])
        ds = load_dataset(cfg["dataset"], df)
        with self.assertRaises(AssertionError):
            FeatureBuilder(cfg["features"], ds).fit(ds.frame, ds.y)

    def test_identity_columns_never_features(self):
        df = make_flows("mixed_host", n_per_class=100, seed=3)
        cfg = load_config(CFG, ["dataset.drop_classes=[]"])
        ds = load_dataset(cfg["dataset"], df)
        fb = FeatureBuilder(cfg["features"], ds).fit(ds.frame, ds.y)
        joined = " ".join(fb.names)
        for col in ("Attack", "Label", "IPV4_SRC_ADDR", "IPV4_DST_ADDR", "_y"):
            self.assertNotIn(col, joined)

    def test_permuted_labels_score_chance(self):
        df = make_flows("mixed_host", n_per_class=300, seed=4)
        with tempfile.TemporaryDirectory() as tmp:
            cfg = quick_cfg(tmp, ["fcha"], ["experiment.sanity_permuted_labels=true"])
            recs = run_grid(cfg, frame=df)
        perm = [r for r in recs if r["permuted_labels"]]
        self.assertEqual(len(perm), 1)
        self.assertLess(perm[0]["metrics"]["balanced_accuracy"], 0.35)


class TestSplitsAndPartitions(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config(CFG, ["dataset.drop_classes=[]"])
        self.ds = load_dataset(self.cfg["dataset"], make_flows("mixed_host", n_per_class=200, seed=5))

    def test_signature_split_no_overlap(self):
        scfg = {"type": "signature", "n_folds": 4, "seed": 0, "signature": self.cfg["signature"]}
        for sp in iter_splits(self.ds, scfg):
            self.assertEqual(sp.audit["signature_overlap"], 0)
            self.assertEqual(len(np.intersect1d(sp.train_idx, sp.test_idx)), 0)

    def test_host_splits(self):
        for mode in ("source", "endpoints"):
            for sp in iter_splits(self.ds, {"type": "host", "host_mode": mode, "n_folds": 4, "seed": 0}):
                self.assertEqual(sp.audit["shared_src_hosts"], 0)
                if mode == "endpoints":
                    self.assertEqual(sp.audit["shared_any_hosts"], 0)

    def test_attacker_split_holds_out_attackers(self):
        scfg = {"type": "attacker", "n_folds": 5, "seed": 0, "min_attack_flows": 5}
        b = self.ds.classes.index(self.ds.benign_class)
        splits = list(iter_splits(self.ds, scfg))
        self.assertGreaterEqual(len(splits), 2)
        held = []
        for sp in splits:
            self.assertEqual(sp.audit["shared_src_hosts"], 0)
            self.assertTrue((self.ds.y[sp.test_idx] != b).any())          # every fold tests attacks
            self.assertTrue(sp.audit["test_attackers"])
            held += sp.audit["test_attackers"]
        self.assertEqual(len(held), len(set(held)))                       # each attacker held out once

    def test_partitions_cover_each_flow_once(self):
        y, src = self.ds.y, self.ds.src
        for p in ({"type": "iid"}, {"type": "dirichlet", "alpha": 0.3, "min_client_size": 10}, {"type": "host"}):
            parts = partition(y, src, p, 4, 0)
            allidx = np.concatenate(parts)
            self.assertEqual(len(allidx), len(y))
            self.assertEqual(len(np.unique(allidx)), len(y), p)
        host_parts = partition(y, src, {"type": "host"}, 4, 0)
        owners = [set(src[p]) for p in host_parts]
        for i in range(4):
            for j in range(i + 1, 4):
                self.assertFalse(owners[i] & owners[j])


class TestModel(unittest.TestCase):
    def test_sampler_excludes_self_and_respects_hosts(self):
        src = np.array([0, 0, 0, 1, 2])
        dst = np.array([1, 2, 1, 2, 0])
        g = FlowGraph(src, dst)
        flows = torch.arange(5)
        nbr, role, valid = g.sample(flows, 0, 8)
        for e in range(5):
            got = set(nbr[e][valid[e]].tolist())
            expect = {f for f in range(5) if f != e and g.src[e].item() in (g.src[f].item(), g.dst[f].item())}
            self.assertEqual(got, expect)

    def test_all_aggregators_forward(self):
        g = FlowGraph(np.array([0, 0, 1, 2]), np.array([1, 2, 2, 0]))
        X = torch.randn(4, 7)
        for agg, use_self in (("attention", True), ("mean", True), ("mean", False), ("none", True)):
            m = EdgeClassifier(7, 3, hidden=16, heads=4, neighbors=4, aggregator=agg, use_self=use_self)
            logits, z = m(X, g, torch.arange(4))
            self.assertEqual(tuple(logits.shape), (4, 3))
            self.assertTrue(torch.isfinite(logits).all())

    def test_learns_planted_signal_and_reports_attention(self):
        df = make_flows("mixed_host", n_per_class=400, seed=6)
        with tempfile.TemporaryDirectory() as tmp:
            recs = run_grid(quick_cfg(tmp, ["fcha", "flow_mlp"], ["federated.rounds=8"]), frame=df)
        fcha = next(r for r in recs if r["model"] == "fcha")
        self.assertGreater(fcha["metrics"]["balanced_accuracy"], 0.6)
        self.assertIn("per_class", fcha["attention"])
        self.assertGreater(fcha["comm_bytes"], 0)


class TestClassCap(unittest.TestCase):
    def test_class_cap_csv_and_parquet(self):
        from fedflow.data import read_table
        df = make_flows("mixed_host", n_per_class=300, seed=7)
        with tempfile.TemporaryDirectory() as tmp:
            for suffix in (".csv", ".parquet"):
                p = Path(tmp) / f"flows{suffix}"
                df.to_csv(p, index=False) if suffix == ".csv" else df.to_parquet(p, index=False)
                out = read_table(p, {"class_cap": 120, "read_chunk_rows": 257}, "Attack")
                counts = out["Attack"].value_counts()
                self.assertTrue((counts <= 120).all(), suffix)
                rare = df["Attack"].value_counts().min()
                self.assertEqual(counts.min(), min(rare, 120), suffix)   # rare class kept whole
                self.assertEqual(list(out.columns), list(df.columns))


class TestPaperPipeline(unittest.TestCase):
    def test_protocol_grid_and_report(self):
        """Paper protocol (duplicate cap, model filters, sanity seeds) end to end, then the report."""
        from fedflow.paper_report import build
        df = make_flows("mixed_host", n_per_class=200, seed=8)
        df = pd.concat([df, df.iloc[:300]], ignore_index=True)        # add exact duplicates
        with tempfile.TemporaryDirectory() as tmp:
            cfgfile = Path(tmp) / "paper.yaml"
            cfgfile.write_text(f"extends: [{(CFG).as_posix()}, {(ROOT / 'configs/fedflow/paper/protocol.yaml').as_posix()}]\n")
            res = Path(tmp) / "results" / "synthetic"
            cfg = load_config(cfgfile, [
                "dataset.drop_classes=[]", "dataset.max_duplicates=1", f"experiment.results_dir={res.as_posix()}",
                "experiment.seeds=[0, 1]", "experiment.sanity_seeds=[0]", "experiment.folds=[0, 1]", "federated.rounds=2",
                "federated.max_steps_per_epoch=10", "federated.num_clients=3", "federated.batch_size=128",
                "federated.early_stopping_patience=0",
                "splits=[{type: signature, n_folds: 3, seed: 0}, {type: host, host_mode: source, n_folds: 3, seed: 0}]",
                "partitions=[{name: iid, type: iid}, {name: dirichlet_a0.5, type: dirichlet, alpha: 0.5, min_client_size: 20}]"])
            cfg["models"] = {k: cfg["models"][k] for k in ("fcha", "host_mean_only", "flow_mlp", "random_forest", "fcha_supcon")}
            recs = run_grid(cfg, frame=df)
            dedup = json.loads((res / "dedup_report.json").read_text())
            self.assertEqual(dedup["flows_after"], len(df) - 300)               # duplicates removed
            got = {(r["split"].split("-")[0], r["model"], r["partition"]) for r in recs}
            self.assertIn(("signature", "fcha_supcon", "iid"), got)             # ablation: signature only
            self.assertNotIn(("host", "fcha_supcon", "iid"), got)
            self.assertNotIn(("signature", "host_mean_only", "dirichlet_a0.5"), got)  # baseline: IID only
            self.assertIn(("signature", "fcha", "dirichlet_a0.5"), got)
            perm = [r for r in recs if r["permuted_labels"]]
            self.assertTrue(perm)
            self.assertEqual({r["seed"] for r in perm}, {0})                    # sanity only on sanity_seeds
            out = Path(tmp) / "report"
            build(["synthetic"], out, results_root=Path(tmp) / "results")
            text = (out / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("T1", text)
            self.assertIn("T3", text)
            self.assertTrue((out / "tables.tex").exists())
            self.assertTrue(any(out.glob("F1_main_*.png")))


class TestConfig(unittest.TestCase):
    def test_overrides_and_inheritance(self):
        cfg = load_config(ROOT / "configs" / "fedflow" / "nf_unsw_nb15.yaml", ["federated.rounds=7"])
        self.assertEqual(cfg["dataset"]["name"], "NF-UNSW-NB15")
        self.assertEqual(cfg["dataset"]["columns"]["label"], "Attack")   # inherited
        self.assertEqual(cfg["federated"]["rounds"], 7)
        d = {}
        set_by_path(d, "a.b=[1, 2]")
        self.assertEqual(d, {"a": {"b": [1, 2]}})


if __name__ == "__main__":
    unittest.main()
