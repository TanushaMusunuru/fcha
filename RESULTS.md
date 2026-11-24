# FedFlow / FCHA: results

*Status: 24 Nov 2026, 21:45 IST. Paper protocol (`configs/fedflow/paper/protocol.yaml`).
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
| Seeds | 42, 43, 44 (signature split); attacker split: 42 on every fold, 43–44 on some (see §3) |
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

### 2.2 ToN-IoT Train_Test_Network (complete: 5 folds × 3 seeds)

| Model | Clients | Runs | Bal. acc | Accuracy | Macro-F1 | FPR |
|---|---|---|---|---|---|---|
| **FCHA** | IID | 15 | **99.1 ± 0.1** | 99.0 ± 0.1 | 99.1 ± 0.1 | 0.05 |
| **FCHA** | Dir(0.5) | 15 | 99.0 ± 0.2 | 98.9 ± 0.2 | 98.9 ± 0.1 | 0.06 |
| FCHA centralised † | – | 15 | 99.2 ± 0.1 | 99.2 ± 0.1 | 99.2 ± 0.1 | 0.06 |
| FCHA + SupCon | IID | 15 | 99.1 ± 0.1 | 99.0 ± 0.1 | 99.1 ± 0.1 | 0.06 |
| E-GraphSAGE-mean | IID | 15 | 99.1 ± 0.1 | 99.0 ± 0.1 | 99.0 ± 0.1 | 0.06 |
| Host-mean (FedGATSage-style) | IID | 15 | 77.2 ± 0.4 | 74.5 ± 0.4 | 76.9 ± 0.4 | 0.17 |
| Flow-MLP | IID | 15 | 97.8 ± 0.1 | 97.7 ± 0.1 | 97.4 ± 0.1 | 0.73 |
| Flow-MLP | Dir(0.5) | 15 | 97.6 ± 0.2 | 97.5 ± 0.1 | 97.2 ± 0.2 | 0.89 |
| Random Forest † | – | 15 | 98.3 ± 0.1 | 98.5 ± 0.1 | 98.3 ± 0.1 | 0.28 |
| XGBoost † | – | 15 | 98.6 ± 0.1 | 98.7 ± 0.1 | 98.6 ± 0.1 | 0.35 |
| Shuffled-label check | IID | 5 | 12.5 ± 0.0 (chance) | 21.0 | 4.3 | – |

### 2.3 NF-CSE-CIC-IDS2018-v2 (complete: 5 folds × 3 seeds)

| Model | Clients | Runs | Bal. acc | Accuracy | Macro-F1 | FPR | Attack detection |
|---|---|---|---|---|---|---|---|
| **FCHA** | IID | 15 | **95.6 ± 1.1** | 98.1 ± 0.1 | **90.2 ± 0.4** | 2.90 | 99.8 |
| **FCHA** | Dir(0.5) | 15 | 93.6 ± 2.4 | 97.8 ± 0.6 | 89.9 ± 0.7 | 5.76 | 99.8 |
| FCHA centralised † | – | 15 | 95.6 ± 1.1 | 98.1 ± 0.1 | 90.2 ± 0.5 | 2.76 | 99.8 |
| FCHA + SupCon | IID | 15 | 95.6 ± 1.1 | 98.1 ± 0.1 | 90.2 ± 0.4 | 2.94 | 99.8 |
| E-GraphSAGE-mean | IID | 15 | 94.5 ± 1.1 | 98.1 ± 0.2 | 90.2 ± 0.4 | 3.05 | 99.7 |
| Host-mean (FedGATSage-style) | IID | 15 | 93.9 ± 1.2 | 97.7 ± 0.2 | 89.4 ± 0.4 | 4.85 | 99.8 |
| Flow-MLP | IID | 15 | 83.5 ± 0.6 | 94.3 ± 0.3 | 85.2 ± 0.6 | 11.13 | 96.0 |
| Flow-MLP | Dir(0.5) | 15 | 83.0 ± 0.8 | 93.7 ± 0.7 | 84.4 ± 1.1 | 17.72 | 96.6 |
| Random Forest † | – | 15 | 83.9 ± 0.6 | 94.2 ± 0.3 | 83.8 ± 0.5 | 10.43 | 96.2 |
| XGBoost † | – | 15 | 83.9 ± 0.5 | 94.9 ± 0.3 | 86.1 ± 0.6 | 6.49 | 95.7 |
| Shuffled-label check | IID | 5 | 14.3 ± 0.0 (chance, 7 classes) | 49.6 | 9.5 | – | – |

On CIC-IDS2018 the graph is worth 11–12 points over every flow-only model, and even host-mean is
close to FCHA: here each attacker machine runs one attack, so host context alone identifies it.

---

## 3. Unseen attackers: leave-attacker-out split

### 3.1 ToN-IoT-Network (all 5 folds; baselines 3 seeds, graph models 3 seeds on F0 and F2, seed 42 elsewhere)

Each fold holds out different attacker machines; the models never see any flow they sent.
Balanced accuracy over supported classes (%), averaged over the seeds available per fold; the last
column is the mean of the fold means.

| Model | F0 (.30) | F1 (.31) | F2 (.32) | F3 (.193) | F4 (minor) | Mean |
|---|---|---|---|---|---|---|
| **FCHA** (IID) | **91.6** | 93.3 | **90.6** | 41.7 | **74.2** | **78.3** |
| **FCHA** (Dir 0.5) | **92.0** | 92.4 | 88.2 | 44.2 | **75.0** | **78.3** |
| E-GraphSAGE-mean | 85.6 | 94.2 | 81.8 | 36.2 | 73.8 | 74.3 |
| Host-mean (FedGATSage-style) | 49.5 | 59.9 | 61.9 | 31.0 | 52.5 | 51.0 |
| Flow-MLP (IID) | 86.1 | 94.0 | 70.8 | 49.3 | 69.7 | 74.0 |
| Flow-MLP (Dir 0.5) | 86.3 | 94.4 | 69.7 | 49.4 | 71.8 | 74.3 |
| Random Forest † | 80.8 | **96.2** | 66.0 | 42.4 | 71.4 | 71.4 |
| XGBoost † | **94.8** | **96.5** | 67.7 | 28.2 | 72.5 | 71.9 |
| Shuffled-label check | 16.7 | 16.7 | 33.2 | 3.2 | 12.6 | 16.5 (chance) |

FCHA beats E-GraphSAGE-mean on 4 of 5 folds (+4.0 on the mean) and every flow-only model by 4–7
points; its largest gain is F2 (XSS from an unseen machine: 90.6 vs 70.8 for Flow-MLP). F3 (an
unseen Backdoor machine, with only 143 Backdoor training flows from elsewhere) defeats every model.
With seed 42 alone (5 matched folds) the paired Wilcoxon p-value cannot go below 0.0625, so the
remaining seeds are needed for a significance claim.

### 3.2 Other datasets (partial)

| Dataset | Model | Folds done | Bal. acc (supported) |
|---|---|---|---|
| NF-ToN-IoT-v2 | **FCHA** IID / Dir(0.5) | F1 × 3 seeds | **80.2** / **81.6** |
| NF-ToN-IoT-v2 | E-GraphSAGE-mean | F1 × 3 seeds | 76.1 |
| NF-ToN-IoT-v2 | Host-mean | F1 × 3 seeds | 41.8 |
| NF-ToN-IoT-v2 | Flow-MLP / RF † / XGBoost † | F1 × 3 seeds | 79.0 / 75.9 / 76.3 |
| NF-ToN-IoT-v2 | Flow-MLP / RF † / XGBoost † | all 5 × 3 seeds | 73.4 / 80.3 / 76.2 |
| CIC-IDS2018-v2 | Flow-MLP / RF † / XGBoost † | all 5 × 3 seeds | 68.8 / 73.3 / 73.3 |
| CIC-IDS2018-v2 | graph models | – | not run |

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

### NF-CSE-CIC-IDS2018-v2 (15 runs each)

| Class | FCHA | E-GraphSAGE-mean | Host-mean | Flow-MLP | Random Forest † | XGBoost † |
|---|---|---|---|---|---|---|
| Benign | **97.1** | 96.9 | 95.2 | 88.9 | 89.6 | 93.5 |
| Bot | 100.0 | 100.0 | 100.0 | 99.1 | 99.1 | 100.0 |
| Brute force | 100.0 | 100.0 | 100.0 | 100.0 | 99.9 | 99.9 |
| DDoS | 92.8 | 94.0 | 93.3 | 99.9 | 97.1 | 99.9 |
| DoS | 99.9 | 99.9 | 99.9 | 99.9 | 100.0 | 100.0 |
| Infiltration | **98.6** | 98.0 | 98.0 | 68.0 | 69.9 | 66.0 |
| Web | **80.4** | 72.8 | 70.6 | 28.6 | 31.4 | 27.6 |

---

## 5. Findings

1. **FCHA is the best federated model on all three datasets** (signature split): 94.2 (ToN-v2),
   99.1 (ToN-Net), 95.6 (CIC-IDS2018), and it beats the centralised trees on all three
   (XGBoost 91.4 / 98.6 / 83.9). On CIC-IDS2018 the gap to every flow-only model is 11–12 points,
   from Infiltration (98.6 vs ≤ 70) and Web (80.4 vs ≤ 31) recall.
2. **Attention beats mean aggregation where it matters.** On the signature split they are close
   (94.2 vs 94.1; 99.1 vs 99.1; 95.6 vs 94.5, with Web recall 80.4 vs 72.8 on CIC). On unseen
   attackers (ToN-IoT-Network) FCHA leads on 4 of 5 folds, 78.3 vs 74.3, with the biggest gains on
   F0 (DoS recall 91 vs 47, seed 42) and F2. NF-ToN-IoT-v2 F1 agrees (80.2 vs 76.1).
3. **Host-level averaging fails when hosts mix traffic.** Host-mean is 16–22 points below on the
   ToN datasets (78.0, 77.2), flags 31% of benign flows on NF-ToN-IoT-v2, and collapses to 51.0 on
   unseen attackers. On CIC-IDS2018, where each attacker machine runs a single attack, it is close
   (93.9), which is consistent with the paper's argument: averaging only hurts on mixed hosts.
4. **Federation costs little:** federated vs centralised FCHA −0.3, −0.1, 0.0;
   Dirichlet(0.5) clients −1.1, −0.1, −2.0.
5. **SupCon adds nothing** on any dataset. Report it as a negative ablation.
6. **No leakage:** every shuffled-label run scores chance (12.5% for 8 classes, 14.3% for 7,
   about 16.7% for 6).
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

| Dataset | Split | Complete | Not yet run |
|---|---|---|---|
| NF-ToN-IoT-v2 | signature | **all models, 5 folds × 3 seeds** | – |
| NF-ToN-IoT-v2 | attacker | baselines 5 folds × 3 seeds; graph models F1 × 3 seeds | graph models F0, F2–F4 |
| ToN-IoT-Network | signature | **all models, 5 folds × 3 seeds** | – |
| ToN-IoT-Network | attacker | baselines 5 × 3; graph models 5 folds (seed 42), F0 and F2 × 3 seeds | graph models F1, F3, F4 seeds 43–44 |
| CIC-IDS2018-v2 | signature | **all models, 5 folds × 3 seeds** | – |
| CIC-IDS2018-v2 | attacker | baselines 5 × 3 | graph models |

## 9. Caveats

1. The unseen-attacker split is incomplete for the graph models (§8); significance tests on it need
   the remaining seeds.
2. Significance tests (Holm-corrected Wilcoxon) are not in this file yet: `py -3 -m fedflow.paper_report`.
3. NF-ToN-IoT-v2 and ToN-IoT-Network come from the same testbed (same attacker machines);
   CIC-IDS2018-v2 is the only independent network.
4. Clients are simulated partitions of one dataset.
5. ToN-IoT-Network is easy on the signature split (all flow-level models ≥ 97.6).
6. A run done both on Kaggle (GPU) and on the laptop (CPU) keeps the Kaggle copy; the two differ
   by up to about 0.5 points from GPU/CPU nondeterminism.

## 10. Where the raw results are

| What | Path |
|---|---|
| Merged per-dataset results (Kaggle + local) | `results/paper/<dataset>/results.jsonl` (rebuild with `py -3 -m fedflow.kaggle_grid collect`) |
| Laptop runs | `results/paper/<dataset>/local*/results.jsonl` |
| Kaggle notebook outputs | `results/paper/<dataset>/kaggle/<notebook>/` |
| Duplicate reports | `results/paper/<dataset>/dedup_report.json` |
| Earlier exploratory runs | `results/archive/`, `results/fedflow/`, `RESULTS_exploratory_fold0.md` |
