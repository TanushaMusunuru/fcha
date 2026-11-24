# FedFlow: Flow-Conditioned Host Attention for federated IoT intrusion detection

FedFlow is a federated, flow-level intrusion detector for NetFlow and Zeek data, plus a
leak-free evaluation protocol for it.

**FCHA (Flow-Conditioned Host Attention)** classifies every flow (graph edge) from its own features
and from two context vectors, one for its sender and one for its receiver. Each context vector is
built by multi-head attention in which the flow being classified is the query and the host's other
flows are keys and values. Training is fully federated: FedAvg or FedProx for the weights,
federated feature standardisation from client moments, and model selection on client validation.

## Contents

| Path | What it is |
|---|---|
| `fedflow/` | The package: data loading, leak guards, splits, client partitions, models, federated training, baselines, metrics, reports |
| `configs/fedflow/` | One YAML per dataset, inheriting `base.yaml`; nothing about a dataset is hard-coded |
| `configs/fedflow/paper/` | The paper protocol (`protocol.yaml`), one config per paper dataset, and the Kaggle grid settings |
| `tests/test_fedflow.py` | 14 unit tests on synthetic data (leakage, splits, partitions, models, pipeline, report) |
| `kaggle/fedflow_kaggle.py` | Single-notebook Kaggle entry point |
| `papers/` | Paper sources (LaTeX) and reference material |
| `archive/` | Earlier code and report tooling, kept for reference (see `archive/README.md`) |
| `data/`, `results/` | Datasets and run outputs (not in git) |
| `FEDFLOW.md` | Method, evaluation protocol and usage in detail |
| `Q1_PLAN.md` | Paper claims, protocol, compute budget and outline |
| `RESULTS.md` | Results so far |

### Modules

| Module | Role |
|---|---|
| `config.py` | YAML loading with `extends` inheritance and `--set a.b=value` overrides |
| `data.py` | Dataset loading (CSV/Parquet, per-class caps), duplicate capping, feature building, leak scan |
| `splits.py` | Signature-grouped, host and leave-attacker-out splits, each with an overlap audit |
| `partition.py` | IID, Dirichlet label-skew and per-host client partitions |
| `graph.py` | Flow graph with fixed-size neighbour sampling |
| `models.py` | `EdgeClassifier` (attention / mean / none aggregators), losses, class weights |
| `federated.py` | Clients, FedAvg/FedProx training, validation-based round selection |
| `baselines.py` | Random Forest, XGBoost, HistGradientBoosting, logistic regression |
| `metrics.py` | Balanced accuracy, macro-F1, per-class scores, FPR, supported-class metrics |
| `analysis.py` | Attention lift on mixed-traffic hosts |
| `run.py` | Grid runner (`python -m fedflow.run`); resumable `results.jsonl` |
| `summarize.py`, `compare.py`, `paper_report.py` | Summary tables, cross-dataset comparison, paper tables / LaTeX / figures |
| `kaggle_grid.py` | Upload, push, queue and collect the paper grid on Kaggle |
| `synthetic.py` | Synthetic flow generators for the tests |

## Setup

```powershell
py -3 -m pip install -r requirements-fedflow.txt
```

```powershell
py -3 -m unittest tests.test_fedflow -v
```

## Data

Datasets are not included. Put each one under `data/<dataset>/` (the configs search there):

| Config | Dataset | File |
|---|---|---|
| `nf_ton_iot_v2.yaml` | NF-ToN-IoT-v2 | `data/nf_ton_iot_v2/*.parquet` or `*.csv` |
| `nf_cse_cic_ids2018_v2.yaml` | NF-CSE-CIC-IDS2018-v2 | `data/nf_cse_cic_ids2018_v2/*.parquet` or `*.csv` |
| `ton_iot_network.yaml` | ToN-IoT Train_Test_Network | `data/ton_iot_network/train_test_network.csv` |
| `nf_ton_iot.yaml`, `nf_unsw_nb15*.yaml` | NF-ToN-IoT (v1), NF-UNSW-NB15 (v1/v2) | see each config |

The NetFlow datasets come from the University of Queensland NIDS collection, and ToN-IoT from UNSW
Canberra. The IP address columns must be kept: they are used to build the host graph (never as
features).

## Running

One dataset, the full paper protocol:

```powershell
py -3 -m fedflow.run --config configs/fedflow/paper/ton_iot_network.yaml
```

A subset of models and folds:

```powershell
py -3 -m fedflow.run --config configs/fedflow/paper/ton_iot_network.yaml --models fcha,flow_mlp --folds 0
```

Paper tables, LaTeX and figures from the results:

```powershell
py -3 -m fedflow.paper_report
```

Results go to `results/paper/<dataset>/` (`results.jsonl`, `summary.md`, `run.log`). Reruns skip
finished runs. The Kaggle launcher and all other options are described in `FEDFLOW.md`.

## Evaluation protocol (summary)

- At most 10 copies of each identical flow, before any split.
- **Signature split:** 5 folds grouped by flow signature (0% overlap). **Leave-attacker-out split:**
  attacker hosts found from the data, so test attackers are never seen in training.
- 5 clients (IID and Dirichlet α = 0.5), 3 seeds, mean ± sample SD, Holm-corrected paired Wilcoxon tests.
- Label and identity columns are excluded, a scan rejects any column that determines the label,
  and a shuffled-label run must score at chance.
