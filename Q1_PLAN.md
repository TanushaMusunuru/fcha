# Q1 plan: FedFlow / FCHA

What has to be true for a Q1 submission, what is already built, and what is left. All commands
run from the repository root.

---

## 1. The paper's claims

The paper should make only claims the planned experiments can support.

| # | Claim | Evidence that supports it |
|---|---|---|
| C1 | **Evaluation matters.** Random splits and repeated flows inflate NetFlow IDS results; the base paper's protocol overlaps 46.88% of signatures between train and test, and some benchmarks are mostly duplicates. | Leakage audit; duplicate report (T6); old 94% vs leak-free results |
| C2 | **Host-mean aggregation hides minority attacks on mixed hosts; flow-conditioned attention recovers them.** | FCHA vs Host-mean (FedGATSage-style) and E-GraphSAGE-style, same code path (T1, T3); attention lift (T5) |
| C3 | **FCHA is the strongest privacy-preserving (federated) model.** | FCHA vs every federated baseline across 3 datasets × 2 splits, Holm-corrected Wilcoxon (T1) |
| C4 | **Federation costs little.** | FCHA federated vs centralised (T3) |
| C5 | **It holds under client heterogeneity and for unseen attackers.** | Dirichlet clients (T2); leave-attacker-out split (T1) |

Centralised Random Forest and XGBoost are reported as an **upper reference**, marked †. The paper
must not claim FCHA beats them everywhere; on NetFlow-v2 it currently does not.

---

## 2. Evaluation protocol (`configs/fedflow/paper/protocol.yaml`)

- **Duplicate cap:** at most 10 copies of each identical flow (exact signature). This is what made
  the folds usable: before it, a CIC-IDS2018 test fold was 66% Bot with 9 brute-force flows; after
  it, every class gets 19.7–20.1% of its flows in every test fold, on all three datasets.
- **Splits:** signature-grouped 5-fold (unseen flow patterns) and leave-attacker-out (unseen attackers; attacker hosts found from the data, spread over 5 folds). A plain host K-fold was dropped: with 4–10 attacker machines most of its test folds held no attack (RESULTS.md §6.2).
- **Seeds:** 42, 43, 44. **Clients:** 5, IID and Dirichlet(α = 0.5).
- **Model selection:** best round by client validation; the test set is never used for selection.
- **Statistics:** mean ± sample SD over folds × seeds; paired Wilcoxon vs FCHA, Holm-corrected.
- **Sanity:** one shuffled-label FCHA run per split and fold (must score at chance).

### Datasets

| Dataset | Why it is in the paper | Kaggle source |
|---|---|---|
| NF-ToN-IoT-v2 | Main IoT dataset; same network as the base paper | `gyandeep2/nf-ton-iot-v2` |
| NF-CSE-CIC-IDS2018-v2 | Large enterprise network (18k hosts); tests generality | `bhuvanshbehal/nf-cse-cic-ids2018-v2` |
| ToN-IoT Train_Test_Network | Balanced, rich (HTTP/DNS/SSL) features; isolates the feature-format effect | `arnobbhowmik/ton-iot-network-dataset` |

### Models

| Model | Role | Runs on |
|---|---|---|
| `fcha` | Proposed | all splits, IID + Dirichlet |
| `egraphsage_mean` | Mean host context + own features | all splits, IID |
| `host_mean_only` | Host averages only (≈ FedGATSage aggregation) | all splits, IID |
| `flow_mlp` | Flow features only, no graph | all splits, IID + Dirichlet |
| `random_forest`, `xgboost` | Centralised reference † | all splits |
| `fcha_supcon` | Ablation: + SupCon | signature, IID |
| `fcha_centralised` | Ablation: cost of federation | signature |

---

## 3. Running it

### 3.1 Compute budget

| Per dataset | Runs |
|---|---|
| Signature split: 5 folds × 3 seeds × 10 model/partition combos | 150 |
| Attacker split: 5 folds × 3 seeds × 8 combos | 120 |
| Shuffled-label checks | 10 |
| **Total** | **≈ 280** (≈ 160 need a GPU) |

All three datasets: ≈ 480 GPU runs ≈ 16–24 GPU-hours, which fits one week of Kaggle GPU quota. Flow-MLP, Random Forest and XGBoost run in CPU kernels, which use no GPU quota.

### 3.2 Commands

```powershell
py -3 -m unittest tests.test_fedflow
py -3 -m fedflow.kaggle_grid upload-code -m "paper protocol"
py -3 -m fedflow.kaggle_grid push --dry-run
py -3 -m fedflow.kaggle_grid push --datasets ton_iot_network --folds 0
py -3 -m fedflow.kaggle_grid status
py -3 -m fedflow.kaggle_grid collect
py -3 -m fedflow.paper_report
```

Order:
1. Push one small kernel first (`ton_iot_network`, fold 0) and check it finishes.
2. Push the remaining kernels.
3. `collect` downloads every kernel's output into `results/paper/<dataset>/` and merges them
   (duplicate runs are skipped).
4. `paper_report` writes `results/paper/report/REPORT.md`, `tables.tex` and the figures.

Kernels resume: rerunning a kernel skips runs already in its `results.jsonl`. The 60 kernels are:
3 datasets × 2 splits × 5 folds × {GPU graph group, CPU flat group}.

---

## 4. Work left besides compute

| Task | Why | Status |
|---|---|---|
| Literature check: line-graph GNNs, edge-attention IDS, E-GraphSAGE / E-ResGAT, FedGNN-IDS 2023–2026 | Your fork found the attention idea overlaps with line-graph GAT; the contribution must be positioned as flow-conditioned attention for federated IDS, with evidence | Not started |
| XSS / web-attack error analysis | Main gap to trees on NetFlow-v2; ToN-IoT-Network shows HTTP fields fix it, so frame it as a NetFlow feature limit | Data in hand; write-up needed |
| Duplicate analysis section | ToN-IoT-v2 Backdoor: 16,809 → 239 distinct flows; CIC-IDS2018 is mostly repeats. A strong, citable finding (C1) | Data in hand |
| Base-paper comparison paragraph | Their split isn't described; their tables repeat values; same XSS/Injection confusion mirrored | Data in hand |
| Communication cost and runtime table | Federated papers are expected to report them | Logged per run |
| Ethics / reproducibility statement, code release | Expected by Q1 venues | Code is ready |

---

## 5. Paper outline

1. **Introduction:** federated IDS for IoT; two problems: evaluation leakage and host-mean
   aggregation; contributions C1–C5.
2. **Related work:** graph IDS (E-GraphSAGE, E-ResGAT, line-graph models), federated IDS,
   FedGATSage, evaluation pitfalls (duplicates, leakage).
3. **Evaluation pitfalls:** signature overlap, duplicate flows, label leakage found in the earlier
   code (93% on random noise). Protocol in §2.
4. **Method:** FCHA (flow as query, attention over sender and receiver flows, role embeddings,
   neighbour sampling); fully federated training (FedAvg, federated standardisation,
   validation-based selection).
5. **Experiments:** T1–T6, F1–F3 from `paper_report`.
6. **Analysis:** attention lift on mixed hosts; XSS/web error analysis; duplicates; federation cost.
7. **Limitations:** tree models remain stronger on NetFlow-v2; simulated clients; datasets are
   benchmarks, not live traffic.

---

## 6. Decision points after the grid

| Outcome | What to do |
|---|---|
| FCHA beats all federated baselines significantly on ≥ 2 of 3 datasets | Submit to a Q1 venue (e.g. *Computers & Security*, *Computer Networks*, *IEEE Internet of Things Journal*; check current quartiles on SJR) |
| FCHA ≈ Flow-MLP / E-GraphSAGE (no significant gain) | Lead with C1 (evaluation pitfalls) as the main contribution; FCHA as a secondary result; target strong Q2 |
| Shuffled-label check not at chance | Stop: there is a leak. Investigate before anything else |
| Attacker-split collapse for all models | Report it honestly as a limitation of NetFlow-based detection (C5 becomes a negative result) |

---

## 7. Timeline (about 3–4 weeks)

| Week | Work |
|---|---|
| 1 | Upload code; run `ton_iot_network` first, then NF-ToN-IoT-v2 and CIC-IDS2018-v2 on Kaggle. In parallel: literature check |
| 2 | Collect, `paper_report`, error and duplicate analyses; decide per §6 |
| 3 | Write the paper around §5 |
| 4 | Internal review: every number in the paper traced to `results/paper/*/results.jsonl` |
