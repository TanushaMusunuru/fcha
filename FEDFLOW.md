# FedFlow: Flow-Conditioned Host Attention for federated IoT intrusion detection

FedFlow replaces the earlier experiment scripts (now legacy and not part of this repository, see
the last section). It fixes the problems found in the code review and adds the new model.

## The idea

Averaging all of a host's flows into one node vector hides a minority attack when it shares a host
with much larger traffic classes. In NF-ToN-IoT, over 98% of Backdoor flows come from one host
that also sends Benign and Injection traffic, and the averaged host features look like Injection.

**FCHA (Flow-Conditioned Host Attention)** classifies each flow (graph edge) from:

1. the flow's own features, and
2. two context vectors, one for its sender and one for its receiver. Each is built by
   multi-head attention in which **the flow being classified is the query** and the other flows
   of that host are keys and values. Each neighbour flow is tagged with whether the host sent or
   received it.

So on a mixed host, a Backdoor flow builds its context mostly from flows that look like it,
instead of from the host-wide average. Neighbours are sampled (at most `neighbors` per endpoint),
so the cost per flow is fixed, whatever the host's degree.

The whole pipeline is federated: model weights through FedAvg (or FedProx), feature
standardisation from client moments (count, sum, sum of squares), and model selection from
client validation results. There is no centrally trained stage, unlike the legacy Random Forest.

`fedflow.analysis.attention_lift` measures the mechanism directly. On hosts that mix classes, it
reports how much attention a class's flows put on same-class flows, compared with uniform
averaging (`lift` > 1 means the attention picks out same-class traffic).

## Models (all in `configs/fedflow/base.yaml`)

| name | what it is |
|---|---|
| `fcha` | proposed model |
| `fcha_supcon` | proposed + supervised contrastive loss |
| `fcha_centralised` | same model with one client (the cost of federation) |
| `egraphsage_mean` | E-GraphSAGE-style: host mean context + own features |
| `host_mean_only` | host averages only: the aggregation of the legacy GAT pipeline |
| `flow_mlp` | real edge-only baseline: the flow's own features, no graph |
| `random_forest`, `hist_gradient_boosting` (+ optional `xgboost`) | centralised references |

All neural models share one code path and one loss, so they differ only in the aggregator.

## Evaluation protocol

* **Splits:**
  * `signature`: StratifiedGroupKFold over flow signatures. The default signature leaves out the
    ephemeral source port and log2-bins volumes, so near-duplicates are grouped too.
  * `attacker` (leave-attacker-out): attacker hosts (sources of at least `min_attack_flows`
    attack flows) are found from the data and spread over the folds, heaviest first; all other
    source hosts are assigned at random. Test attackers are never seen in training. Metrics add
    `balanced_accuracy_supported`, which leaves out classes with fewer than `min_class_support`
    test flows or none in training.
  * `host`: plain K-fold over all source hosts. Kept for reference only: these benchmarks have
    4–10 attacker machines, so most of its test folds contain no attack.
  * `host_mode: endpoints` (for `attacker` and `host`) also removes training flows that touch any
    test host (victims too); the audit reports what that drops.
* **All folds × several seeds.** Tables report mean ± sample SD over (fold, seed), plus a paired
  Wilcoxon test against `fcha` when there are at least 5 matched pairs.
* **Client partitions:** `iid`, `dirichlet` label skew, and `host` (each source host belongs to
  one client).
* **Metrics:** balanced accuracy, macro-F1, accuracy, and per-class precision, recall and F1.
  Also confusion matrix, false-positive rate, attack detection rate, communication bytes, the
  best round and the training curve.
* **Leakage guards (automatic):**
  * label and identity columns can never be features;
  * a scan rejects any column that is a deterministic function of the label (for example the
    binary `Label`);
  * the test graph and standardisation use only training statistics;
  * every split is audited for signature and host overlap.
* **Sanity check:** `experiment.sanity_permuted_labels` trains `fcha` on shuffled labels, which
  must score at chance.

Nothing about the dataset is hard-coded. File locations, column roles, classes to keep and drop,
feature options, splits, partitions, models and the grid all live in YAML.

## Running

```powershell
py -3 -m pip install -r requirements-fedflow.txt
```

```powershell
py -3 -m unittest tests.test_fedflow -v
```

```powershell
py -3 -m fedflow.run --config configs/fedflow/nf_ton_iot.yaml --set dataset.path=data/NF-ToN-IoT.csv
```

Useful options:
* `--models fcha,flow_mlp,random_forest` runs a subset of models.
* `--folds 0` runs only that fold.
* `--set federated.rounds=10` overrides any config value.
* Runs resume: finished runs in `results.jsonl` are skipped.
* `py -3 -m fedflow.summarize <results.jsonl> --reference fcha` rebuilds the tables.

Outputs go to `results/fedflow/<dataset>/`:
* `results.jsonl`: one record per run, with the full metrics and split audit.
* `summary.md` / `summary.csv`
* `per_class_recall.csv`
* `run.log`
* `config_used.json`

**Kaggle.** Upload this repository as a Kaggle dataset, attach it together with the NetFlow CSV,
and run `kaggle/fedflow_kaggle.py`. Choose what runs with the environment variables
`FEDFLOW_CONFIG`, `FEDFLOW_SET`, `FEDFLOW_MODELS` and `FEDFLOW_FOLDS` (described in the file).

**Compute.** The full default grid is 2 splits × 5 folds × 3 seeds × (5 federated models ×
3 partitions + centralised + 2 classical + sanity). That is more than one Kaggle session. Run it
in pieces, by fold or by model; the results file resumes. Start with `--folds 0` and the
baselines `flow_mlp,random_forest`: if a plain Random Forest on flow features matches FCHA on
unseen hosts, the paper's claim has to change.

## Paper pipeline

`Q1_PLAN.md` describes the full evaluation used for the paper:
- **Protocol:** `configs/fedflow/paper/protocol.yaml`, with duplicate capping, signature and host
  splits, IID and Dirichlet clients, 3 seeds and Holm-corrected tests.
- **Kaggle launcher:** `python -m fedflow.kaggle_grid` runs the grid on Kaggle.
- **Report:** `python -m fedflow.paper_report` produces the tables, LaTeX and figures.

## What was fixed relative to the legacy scripts

| Problem in legacy code | Status |
|---|---|
| `label_idx` used as a feature (scored 93% balanced accuracy on random-noise data) | Fixed in legacy scripts; impossible in FedFlow (exclusion + leak scan + test) |
| Test graph standardised with its own statistics | Fixed in legacy; FedFlow uses federated training statistics |
| Interpolation averaged ports/protocol and invented host pairs | Fixed in legacy; FedFlow has no interpolation |
| "5 local epochs" were 5 mini-batch steps | Documented in legacy; FedFlow uses real epochs (optional step cap) |
| "Edge-only" variant still used averaged host features | FedFlow `flow_mlp` is truly edge-only |
| Final Random Forest trained centrally on in-sample GAT outputs | FedFlow is fully federated |
| IP-disjoint split used hand-picked IPs and only separated sources | FedFlow host folds are data-driven, with an optional both-endpoints mode |
| Signature included the ephemeral source port and exact values | Configurable signature with log2 binning |
| One fold, population SD in summaries | All folds, sample SD, paired tests |

## Legacy code

The earlier pipeline produced the numbers in the first paper draft. Those numbers should not be
reported: the label leak was present in that code. The legacy scripts are kept outside this
repository, for reference only.
