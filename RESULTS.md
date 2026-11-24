# FedFlow / FCHA: results

*Status: 24 Nov 2026, 10:45 IST. Paper protocol (`configs/fedflow/paper/protocol.yaml`).
Numbers are mean ± sample SD over (fold × seed) on the test folds. Runs still in progress are
marked; everything here is regenerated from `results/paper/*/results.jsonl`.
The earlier single-fold exploratory results (before duplicate capping) are kept in
`RESULTS_exploratory_fold0.md`; they are superseded and should not be reported.*

† = centralised reference (not federated). **Bold** = proposed model.

---

## 1. Protocol

| Item | Setting |
|---|---|
| Duplicate cap | At most 10 copies of each identical flow (exact signature) before splitting |
| Splits | **Signature**: StratifiedGroupKFold over flow signatures, 5 folds, 0% signature overlap. **Attacker** (leave-attacker-out): attacker hosts found from the data and spread over 5 folds; all other hosts random. |
| Seeds | 42, 43, 44 (signature split); 42 so far (attacker split) |
| Federated training | 5 clients, FedAvg, ≤ 30 rounds, 1 local epoch (≤ 600 steps), batch 512, AdamW lr 3e-4, square-root inverse class weights, early stopping (patience 10) on client validation |
| Clients | IID and Dirichlet(α = 0.5) label skew |
| Model selection | Best round by client validation; the test set is never used |
| Features | All flow columns except label, binary attack flag, IP addresses (graph only) and IDs; leak scan rejects any column that determines the label |
| Sanity check | FCHA trained on shuffled labels, once per fold (must score at chance) |
| Attacker-split metric | Balanced accuracy over classes with ≥ 50 test flows that also occur in training (a stray 1–4 flows of a class would otherwise weigh as much as a whole class) |

**Models** (all neural models share one code path; they differ only in the aggregator)

| Model | Input to the classifier |
|---|---|
| **FCHA** | the flow's own features + attention over the sender's and receiver's other flows (the flow is the query) |
| FCHA centralised † | same model, one client |
| FCHA + SupCon | FCHA + supervised contrastive loss |
| E-GraphSAGE-mean | the flow's own features + **mean** of the sender's and receiver's flows |
| Host-mean | sender and receiver host averages only (the FedGATSage-style aggregation) |
| Flow-MLP | the flow's own features only |
| Random Forest †, XGBoost † | the flow's own features, centralised |

**Datasets after duplicate capping**

| Dataset | Flows before → after cap | Classes | Note |
|---|---|---|---|
| NF-ToN-IoT-v2 | 1,066,809 → 396,551 (≤ 150k per class read from 16.9M) | 8 | Ransomware, MITM dropped (as in the base paper) |
| NF-CSE-CIC-IDS2018-v2 | 833,872 → 280,632 (≤ 150k per class read from 18.9M) | 7 | 15 raw labels merged into 7 families |
| ToN-IoT Train_Test_Network | 190,000 → 130,248 | 8 | Zeek format with HTTP/DNS/SSL fields; Ransomware, MITM dropped |

---

## 2. Main results: signature split (unseen flow patterns)

### 2.1 NF-ToN-IoT-v2 (complete: 5 folds × 3 seeds)

| Model | Clients | Runs | Bal. acc | Accuracy | Macro-F1 | FPR | Attack detection |
|---|---|---|---|---|---|---|---|
| **FCHA** | IID | 15 | **94.2 ± 0.9** | 94.4 ± 0.1 | **92.2 ± 1.5** | 4.57 ± 0.35 | 99.6 |
| **FCHA** | Dir(0.5) | 15 | 93.1 ± 0.9 | 94.0 ± 0.4 | 91.6 ± 1.6 | 5.65 ± 1.60 | 99.7 |
| FCHA centralised † | – | 15 | 94.5 ± 0.8 | 94.6 ± 0.2 | 91.9 ± 1.9 | 4.63 ± 1.23 | 99.6 |
| FCHA + SupCon | IID | 15 | 94.0 ± 0.9 | 94.4 ± 0.1 | 91.9 ± 1.6 | 4.50 ± 0.51 | 99.6 |
| E-GraphSAGE-mean | IID | 15 | 94.1 ± 0.9 | 94.4 ± 0.1 | 92.0 ± 1.7 | 4.45 ± 0.42 | 99.6 |
| Host-mean (FedGATSage-style) | IID | 15 | 78.0 ± 0.5 | 77.5 ± 0.2 | 74.9 ± 1.5 | 30.99 ± 1.02 | 98.0 |
| Flow-MLP | IID | 15 | 90.1 ± 0.9 | 91.4 ± 0.1 | 87.2 ± 2.2 | 6.65 ± 0.82 | 99.4 |
| Flow-MLP | Dir(0.5) | 15 | 89.6 ± 1.3 | 91.0 ± 0.3 | 87.2 ± 1.6 | 8.04 ± 2.32 | 99.5 |
| Random Forest † | – | 15 | 90.5 ± 0.8 | 92.6 ± 0.2 | 91.1 ± 0.8 | 3.47 ± 0.29 | 99.4 |
| XGBoost † | – | 15 | 91.4 ± 0.9 | 93.2 ± 0.1 | 91.7 ± 0.8 | 4.83 ± 0.43 | 99.5 |
| Shuffled-label check | IID | 5 | 12.5 ± 0.0 (chance) | 29.1 | 5.6 | – | – |

### 2.2 ToN-IoT Train_Test_Network (graph models: 3 folds so far; baselines: 5 folds)

| Model | Clients | Runs | Bal. acc | Accuracy | Macro-F1 | FPR |
|---|---|---|---|---|---|---|
| **FCHA** | IID | 7 | **99.1 ± 0.0** | 99.0 ± 0.0 | 99.1 ± 0.0 | 0.04 |
| **FCHA** | Dir(0.5) | 7 | 98.9 ± 0.2 | 98.9 ± 0.2 | 98.9 ± 0.2 | 0.05 |
| FCHA centralised † | – | 6 | 99.2 ± 0.0 | 99.2 ± 0.0 | 99.2 ± 0.0 | 0.01 |
| FCHA + SupCon | IID | 7 | 99.1 ± 0.0 | 99.0 ± 0.0 | 99.1 ± 0.0 | 0.05 |
| E-GraphSAGE-mean | IID | 7 | 99.1 ± 0.0 | 99.0 ± 0.1 | 99.0 ± 0.0 | 0.06 |
| Host-mean (FedGATSage-style) | IID | 7 | 76.9 ± 0.1 | 74.3 ± 0.2 | 76.7 ± 0.1 | 0.18 |
| Flow-MLP | IID | 15 | 97.8 ± 0.1 | 97.7 ± 0.1 | 97.4 ± 0.1 | 0.73 |
| Flow-MLP | Dir(0.5) | 15 | 97.6 ± 0.2 | 97.5 ± 0.1 | 97.2 ± 0.2 | 0.89 |
| Random Forest † | – | 15 | 98.3 ± 0.1 | 98.5 ± 0.1 | 98.3 ± 0.1 | 0.28 |
| XGBoost † | – | 15 | 98.6 ± 0.1 | 98.7 ± 0.1 | 98.6 ± 0.1 | 0.35 |
| Shuffled-label check | IID | 2 | 12.5 ± 0.0 (chance) | 20.9 | 4.3 | – |

### 2.3 NF-CSE-CIC-IDS2018-v2 (baselines complete; graph models running on Kaggle, folds 0–1)

| Model | Clients | Runs | Bal. acc | Accuracy | Macro-F1 | FPR |
|---|---|---|---|---|---|---|
| **FCHA and other graph models** | | – | *running* | | | |
| Flow-MLP | IID | 15 | 83.5 ± 0.6 | 94.3 ± 0.3 | 85.2 ± 0.6 | 11.13 |
| Flow-MLP | Dir(0.5) | 15 | 83.0 ± 0.8 | 93.7 ± 0.7 | 84.4 ± 1.1 | 17.72 |
| Random Forest † | – | 15 | 83.9 ± 0.6 | 94.2 ± 0.3 | 83.8 ± 0.5 | 10.43 |
| XGBoost † | – | 15 | 83.9 ± 0.5 | 94.9 ± 0.3 | 86.1 ± 0.6 | 6.49 |

---

## 3. Unseen attackers: leave-attacker-out split (ToN-IoT-Network, seed 42)

Each fold holds out different attacker machines; the models never see any flow they sent.
Balanced accuracy over supported classes (%):

| Model | F0 (.30) | F1 (.31) | F2 (.32) | F3 (.193) | F4 (minor) | Mean |
|---|---|---|---|---|---|---|
| **FCHA** (IID) | **95.8** | 93.3 | *running* | | | 94.5 (2 folds) |
| **FCHA** (Dir 0.5) | **96.6** | *running* | | | | |
| E-GraphSAGE-mean | 87.7 | *running* | | | | |
| Host-mean (FedGATSage-style) | 48.8 | *running* | | | | |
| Flow-MLP (IID) | 95.5 | 94.3 | 70.5 | 27.6 | 71.0 | 71.8 ± 27.5 |
| Flow-MLP (Dir 0.5) | 95.6 | 94.3 | 63.9 | 49.1 | 69.8 | 74.5 ± 20.1 |
| Random Forest † | 81.0 | 95.9 | 67.2 | 49.5 | 69.8 | 72.7 ± 17.2 |
| XGBoost † | 94.8 | 96.5 | 67.7 | 28.2 | 72.5 | 71.9 ± 27.7 |
| Shuffled-label check | 16.7 (chance, 6 classes) | | | | | |

**What each fold tests** (test flows, with training flows of the same class from other machines in brackets):

| Fold | Held-out attacker(s) | Attack classes tested |
|---|---|---|
| F0 | 192.168.1.30 | DDoS 14,215 (2,647), DoS 18,578 (1,296), injection 7,813 (12,081), password 8,609 (9,124), scanning 5,910 (6,862) |
| F1 | 192.168.1.31 | DDoS 2,643 (14,219), DoS 603 (19,271), injection 12,080 (7,814), password 9,124 (8,609), scanning 1,974 (10,798) |
| F2 | 192.168.1.32 | scanning 4,888 (7,884), **XSS 8,275 (537)** |
| F3 | 192.168.1.193 | **Backdoor 6,817 (143)** |
| F4 | .33, .36, .37, .39 | Backdoor 143 (6,817), DoS 692 (19,182), XSS 537 (8,275) |

**Fold 0 per-class recall (%)**: the clearest view of the mechanism.

| Model | DDoS | DoS | Injection | Normal | Password | Scanning |
|---|---|---|---|---|---|---|
| **FCHA** | 97 | **91** | 93 | 99 | 98 | 97 |
| E-GraphSAGE-mean | 97 | **47** | 88 | 99 | 98 | 97 |
| Host-mean | 31 | 19 | 50 | 99 | 12 | 81 |
| Flow-MLP | 96 | 89 | 91 | 100 | 99 | 98 |
| XGBoost † | 88 | 89 | 93 | 100 | 100 | 99 |
| Random Forest † | 90 | 5 | 93 | 100 | 100 | 99 |

---

## 4. Per-class recall, signature split (%)

### NF-ToN-IoT-v2 (15 runs each)

| Class | FCHA | E-GraphSAGE-mean | Host-mean | Flow-MLP | Random Forest † | XGBoost † |
|---|---|---|---|---|---|---|
| Backdoor | 92.8 | 92.2 | 98.1 | 81.2 | 77.3 | 80.0 |
| Benign | 95.4 | 95.5 | **69.0** | 93.3 | 96.5 | 95.2 |
| DDoS | 96.8 | 97.1 | 87.4 | 95.5 | 95.2 | 96.0 |
| DoS | 99.8 | 99.8 | **51.8** | 98.4 | 98.0 | 98.6 |
| Injection | 86.7 | 86.7 | 70.5 | 77.0 | 84.8 | 85.0 |
| Password | 89.5 | 89.4 | 77.4 | 87.4 | 84.7 | 87.6 |
| Scanning | 98.8 | 98.7 | 80.7 | 98.4 | 98.7 | 98.8 |
| XSS | **93.9** | 93.5 | 89.1 | 89.7 | 88.4 | 89.8 |

### ToN-IoT-Network

| Class | FCHA | E-GraphSAGE-mean | Host-mean | Flow-MLP | Random Forest † | XGBoost † |
|---|---|---|---|---|---|---|
| Backdoor | 100.0 | 100.0 | 100.0 | 99.8 | 99.9 | 99.9 |
| DDoS | 98.1 | 98.1 | 79.7 | 96.2 | 98.3 | 98.5 |
| DoS | 98.6 | 98.5 | 57.8 | 97.7 | 98.8 | 98.7 |
| Injection | 98.4 | 98.3 | 53.8 | 94.8 | 97.2 | 97.3 |
| Normal | 100.0 | 99.9 | 99.8 | 99.3 | 99.7 | 99.6 |
| Password | 99.1 | 99.1 | 43.5 | 98.7 | 99.3 | 99.4 |
| Scanning | 98.6 | 98.7 | 80.9 | 98.2 | 98.1 | 98.8 |
| XSS | 100.0 | 99.9 | 100.0 | 97.6 | 95.0 | 97.0 |

### NF-CSE-CIC-IDS2018-v2 (baselines)

| Class | Flow-MLP | Random Forest † | XGBoost † |
|---|---|---|---|
| Benign | 88.9 | 89.6 | 93.5 |
| Bot | 99.1 | 99.1 | 100.0 |
| Brute force | 100.0 | 99.9 | 99.9 |
| DDoS | 99.9 | 97.1 | 99.9 |
| DoS | 99.9 | 100.0 | 100.0 |
| Infiltration | 68.0 | 69.9 | 66.0 |
| Web | 28.6 | 31.4 | 27.6 |

---

## 5. Findings

1. **Host-level averaging fails.** Host-mean is 16–22 points below every flow-level model on the
   signature split (78.0 vs 94.2; 76.9 vs 99.1), and collapses to 48.8 on an unseen attacker.
   On NF-ToN-IoT-v2 it flags 31% of benign flows as attacks (FCHA: 4.6%).
2. **FCHA is the best federated model and beats the centralised trees** on NF-ToN-IoT-v2
   (94.2 vs XGBoost 91.4, RF 90.5) and ToN-IoT-Network (99.1 vs 98.6, 98.3).
3. **Attention vs. mean aggregation.** A tie on the signature split (94.2 vs 94.1; 99.1 vs 99.1),
   but on the first unseen-attacker fold FCHA leads by 8 points (95.8 vs 87.7), entirely from
   DoS recall (91 vs 47). Needs confirming on folds 1–4.
4. **Federation costs little:** federated vs centralised FCHA −0.3 (ToN-v2) and −0.1 (ToN-Net);
   Dirichlet(0.5) clients −1.1 and −0.2.
5. **SupCon adds nothing** (94.0 vs 94.2; 99.1 vs 99.1). Report it as a negative ablation.
6. **No leakage:** every shuffled-label run scores exactly chance (12.5% for 8 classes, 16.7% for 6).
7. **Duplicates dominate some benchmarks** (§6.1) and **these benchmarks have too few attackers for a
   plain host-disjoint split** (§6.2). Both are evaluation findings for the paper.

---

## 6. Analyses

### 6.1 Duplicate flows (cap of 10 copies per identical flow)

| Dataset | Class | Flows before → after | Distinct share |
|---|---|---|---|
| NF-ToN-IoT-v2 | Backdoor | 16,809 → 239 | 1.4% |
| NF-ToN-IoT-v2 | DoS | 150,000 → 23,067 | 15% |
| NF-ToN-IoT-v2 | all | 1,066,809 → 396,551 | 37% |
| CIC-IDS2018-v2 | Bot | 143,097 → 997 | 0.7% |
| CIC-IDS2018-v2 | Brute force | 120,912 → 16,924 | 14% |
| CIC-IDS2018-v2 | all | 833,872 → 280,632 | 34% |
| ToN-IoT-Network | all | 190,000 → 130,248 | 69% |

Without the cap, folds were badly skewed (a CIC-IDS2018 test fold was 66% Bot with 9 brute-force
flows) and XSS recall on NF-ToN-IoT-v2 was 14.7%; with it, every class has 19.7–20.1% of its flows
in each test fold and FCHA's XSS recall is 93.9%.

### 6.2 Why a plain host split does not work

| Dataset | Attacker machines | Example |
|---|---|---|
| ToN-IoT-Network | 4 main (.30, .31, .32, .193) + 4 minor | Backdoor from one machine; 97% of XSS from one |
| NF-ToN-IoT-v2 | about 10 (192.168.1.30–39) + .193 | Backdoor: 99% from one machine |
| CIC-IDS2018-v2 | 1 machine each for 8 of 14 raw attack labels | all DoS variants, FTP/SSH brute force, SQL injection |

A 5-fold split over all source hosts gave NF-ToN-IoT-v2 test folds of 11, 4 and 865 flows with no
attacks, and one fold whose training set had no DDoS, DoS, injection or backdoor. Those results are
discarded. The leave-attacker-out split (§3) replaces it.

### 6.3 Attention lift (FCHA, signature split)

Attention a flow puts on same-class flows on mixed-traffic hosts, divided by uniform averaging
(> 1: attention picks out same-class traffic).

| Class | NF-ToN-IoT-v2 (15 runs) | ToN-IoT-Network (7 runs) |
|---|---|---|
| DoS | **1.89** | **1.67** |
| Password | 1.08 | 1.33 |
| DDoS | 1.28 | 0.78 |
| Scanning | 1.18 | 1.02 |
| Injection | 1.07 | 0.83 |
| Benign / normal | 0.90 | 0.89 |
| XSS | 0.79 | 0.96 |
| Backdoor | 0.99 | 0.58 |

DoS has the highest lift on both datasets, matching the unseen-attacker result in §3 (DoS is where
attention beats the mean). The lift is not above 1 for every class, so the paper should describe it
per class rather than as a general property.

### 6.4 Communication and runtime (signature split, per run, mean)

| Model | Uplink+downlink (MB), ToN-v2 / ToN-Net | Wall-clock (s), ToN-v2 / ToN-Net |
|---|---|---|
| **FCHA** | 202.5 / 204.1 | 316 / 337 |
| E-GraphSAGE-mean | 145.8 / 144.6 | 270 / 263 |
| Host-mean | 126.2 / 125.0 | 266 / 248 |
| Flow-MLP | 86.1 / 84.8 | 330 / 119 |
| Random Forest † | – | 59 / 11 |
| XGBoost † | – | 159 / 49 |

Totals over the whole run (about 28 rounds × 5 clients). Wall-clock times mix Kaggle GPU and laptop
CPU runs, so compare them only within a column.

---

## 7. Comparison with the base paper (FedGATSage, Sci. Reports 2025)

| | Bal. acc | F1 | Data / split |
|---|---|---|---|
| FedGATSage (reported) | 78.5 | 61.9 | NF-ToN-IoT v1; split not described |
| Our host-mean (their aggregation, our protocol) | 78.0 | 74.9 | NF-ToN-IoT-v2, signature split |
| **Our FCHA** | **94.2** | **92.2** | NF-ToN-IoT-v2, signature split |

Not a like-for-like comparison (dataset version and split differ). Their XSS/Injection confusion is
mirrored in our earlier exploratory runs; their Tables 2–3 repeat identical values for different
settings; MITM and Ransomware are dropped without comment (we drop them too, for comparability).

---

## 8. Run inventory

| Dataset | Split | Complete | Running / pending |
|---|---|---|---|
| NF-ToN-IoT-v2 | signature | **all models, 5 folds × 3 seeds** (228 runs incl. discarded host runs) | – |
| NF-ToN-IoT-v2 | attacker | – | not started |
| ToN-IoT-Network | signature | baselines 5 folds; graph models folds 0–1, part of 2 | graph models folds 2–4 (laptop) |
| ToN-IoT-Network | attacker | baselines 5 folds (seed 42); graph models fold 0, FCHA fold 1 | graph models folds 1–4 (laptop) |
| CIC-IDS2018-v2 | signature | baselines 5 folds × 3 seeds | graph models folds 0–1 (Kaggle) |
| CIC-IDS2018-v2 | attacker | – | not started |

## 9. Caveats

1. ToN-IoT-Network graph models and CIC-IDS2018 are incomplete; the unseen-attacker split has one seed.
2. Significance tests (Holm-corrected Wilcoxon) are not run yet: `py -3 -m fedflow.paper_report`.
3. NF-ToN-IoT-v2 and ToN-IoT-Network come from the same testbed (same attacker machines);
   CIC-IDS2018-v2 is the only independent network.
4. Clients are simulated partitions of one dataset.
5. ToN-IoT-Network is easy on the signature split (all flow-level models ≥ 97.6).

## 10. Where the raw results are

| What | Path |
|---|---|
| Merged per-dataset results (Kaggle + local) | `results/paper/<dataset>/results.jsonl` (rebuild with `py -3 -m fedflow.kaggle_grid collect`) |
| Laptop runs | `results/paper/<dataset>/local*/results.jsonl` |
| Kaggle notebook outputs | `results/paper/<dataset>/kaggle/<notebook>/` |
| Duplicate reports | `results/paper/<dataset>/dedup_report.json` |
| Earlier exploratory runs | `results/archive/`, `results/fedflow/`, `RESULTS_exploratory_fold0.md` |
