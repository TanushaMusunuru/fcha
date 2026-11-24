# FedFlow results so far

*Status: 23 Nov 2026. All numbers are **fold 0, seed 42**, on the test set, from a single local run on a laptop CPU.
They are a first look, not final paper results: the journal version needs 5 folds × 3 seeds per dataset.*

---

## 1. Setup

| Item | Setting |
|---|---|
| Split | Signature-grouped 5-fold (StratifiedGroupKFold), fold 0. Signature = dst port, protocol, log2-binned in/out bytes, in/out packets, duration. **0% signature overlap** between train and test. |
| Federated training | 5 clients, IID (class-stratified) partition, FedAvg, 30 rounds, 1 local epoch (≤ 600 steps), batch 512 |
| Optimiser (v2 runs) | AdamW, lr 3e-4, weight decay 1e-4, square-root inverse class weights, early stopping (patience 10) on client validation |
| Optimiser (v1 run) | lr 1e-3, effective-number class weights, 300 steps, patience 8 (older settings, so v1 is not directly comparable with v2) |
| Model selection | Best round by pooled client validation balanced accuracy; the test set is never used for selection |
| Features | All NetFlow columns except the label (`Attack`), the binary attack flag (`Label`), IP addresses (used only to build the host graph) and `DNS_QUERY_ID`. v1: about 60 inputs; ToN-IoT-v2: 161; CIC-IDS2018-v2: 149. |

**Models**

| Model | What it is | Training |
|---|---|---|
| **FCHA** (proposed) | Flow-Conditioned Host Attention: each flow attends over the other flows of its sender and of its receiver, plus its own features | Federated |
| FCHA centralised | Same model, one client (the cost-of-federation reference) | Centralised |
| Flow-MLP | Flow's own features only, no graph (true edge-only baseline) | Federated |
| Random Forest | 200 trees, balanced class weights, flow features | Centralised |

**Datasets**

| Dataset | Flows used | Hosts | Classes | Notes |
|---|---|---|---|---|
| NF-ToN-IoT (v1) | 1,377,837 | 1,436 | 8 | Ransomware and MITM dropped, as in the base paper |
| NF-ToN-IoT-v2 | 1,066,809 (≤150k per class from 16.9M) | 1,956 | 8 | Ransomware and MITM dropped |
| NF-CSE-CIC-IDS2018-v2 | 833,872 (≤150k per class from 18.9M) | 18,476 | 7 | 15 raw labels merged into 7 families |
| NF-UNSW-NB15-v2 | 245,053 | 41 | 10 | Run stopped before a test result (see §6) |
| ToN-IoT Train_Test_Network | 190,000 | 690 | 8 | Balanced Zeek-format subset; Ransomware and MITM dropped |

---

## 2. Main results (%)

| Model | Training | ToN-IoT-v2 Acc. | ToN-IoT-v2 Bal. acc. | ToN-IoT-v2 Macro-F1 | CIC-2018-v2 Acc. | CIC-2018-v2 Bal. acc. | CIC-2018-v2 Macro-F1 |
|---|---|---|---|---|---|---|---|
| **FCHA (proposed)** | Federated | 70.9 | 79.6 | 75.6 | 92.5 | 68.6 | 57.9 |
| FCHA | Centralised | 71.0 | 76.9 | 74.7 | *stopped* | *stopped* | *stopped* |
| Flow-MLP | Federated | 67.6 | 75.8 | 71.9 | 93.3 | 73.2 | 68.5 |
| Random Forest | Centralised | **91.3** | **89.7** | **82.1** | **94.1** | **87.0** | **89.2** |

**False-positive rate** (share of benign flows flagged as attacks), %:

| Model | ToN-IoT-v2 | CIC-2018-v2 |
|---|---|---|
| FCHA (federated) | 3.95 | **0.29** |
| FCHA (centralised) | **3.68** | *stopped* |
| Flow-MLP | 9.83 | 3.87 |
| Random Forest | 4.29 | 3.57 |

**ToN-IoT Train_Test_Network** (balanced Zeek-format subset: 20,000 flows per attack class, 50,000 normal; 190,000 flows after dropping Ransomware and MITM; 154 features incl. HTTP/DNS/SSL fields):

| Model | Training | Accuracy | Bal. acc. | Macro-F1 | FPR |
|---|---|---|---|---|---|
| **FCHA (proposed)** | Federated | **99.59** | **99.51** | **99.52** | **0.00** |
| Flow-MLP | Federated | 98.89 | 98.48 | 98.12 | 0.04 |
| Random Forest | Centralised | 98.53 | 95.76 | 96.87 | 0.01 |

Per-class recall / F1 (%):

| Class | Test flows | FCHA | Flow-MLP | Random Forest |
|---|---|---|---|---|
| Backdoor | **12** | 100.0 / 100.0 | 100.0 / 96.0 | 83.3 / 90.9 |
| DDoS | 2,997 | 99.1 / 98.4 | 95.6 / 97.0 | 96.4 / 96.0 |
| DoS | 4,000 | 99.8 / 99.7 | 99.8 / 99.8 | 99.9 / 99.8 |
| Injection | 4,000 | 98.1 / 98.7 | 98.8 / 98.2 | 99.2 / 99.0 |
| Normal | 11,248 | 100.0 / 100.0 | 100.0 / 99.4 | 100.0 / 99.9 |
| Password | 4,244 | 99.9 / 99.8 | 99.9 / 99.9 | 96.4 / 97.5 |
| Scanning | 4,000 | 99.9 / 99.9 | 98.0 / 99.0 | 99.9 / 98.1 |
| XSS | 1,909 | 99.2 / 99.6 | 95.8 / 95.5 | 91.0 / 93.8 |

This subset is known to be easy (scores near 99% are common in the literature), and its Backdoor test count is tiny. Part of the Random Forest's lower balanced accuracy comes from Backdoor (10 of 12 caught), so treat this as a secondary benchmark.

**NF-ToN-IoT v1** (older training settings):

| Model | Accuracy | Bal. acc. | Macro-F1 |
|---|---|---|---|
| FCHA (federated) | 68.8 | **61.6** | **51.4** |
| Flow-MLP (federated) | **74.4** | 57.4 | 43.4 |
| Random Forest | 63.6 | 60.3 | 49.4 |

---

## 3. Per-class results, recall / F1 (%)

### NF-ToN-IoT-v2

| Class | Test flows | FCHA (fed.) | FCHA (central.) | Flow-MLP | Random Forest |
|---|---|---|---|---|---|
| Backdoor | 106 | 87.7 / 93.5 | 80.2 / 89.0 | 87.7 / 93.5 | 87.7 / 24.1 |
| Benign | 26,758 | 96.0 / 84.1 | 96.3 / 88.9 | 90.2 / 61.2 | 95.7 / 94.4 |
| DDoS | 29,645 | 91.1 / 91.3 | 87.8 / 91.8 | 88.7 / 92.2 | 92.1 / 93.5 |
| DoS | 113,135 | 85.4 / 91.4 | 90.4 / 94.3 | 93.2 / 75.0 | 92.3 / 94.1 |
| Injection | 29,945 | 92.9 / 41.7 | 93.4 / 40.4 | 74.0 / 76.6 | 77.1 / 78.8 |
| Password | 29,978 | 87.6 / 92.3 | 74.0 / 84.0 | 85.5 / 90.8 | 95.6 / 97.0 |
| Scanning | 7,299 | 81.5 / 85.2 | 79.1 / 84.2 | 87.0 / 85.9 | 84.5 / 86.5 |
| **XSS** | 73,973 | **14.7** / 25.4 | **14.2** / 24.7 | **0.1** / 0.2 | 92.4 / 88.6 |

### NF-CSE-CIC-IDS2018-v2

| Class | Test flows | FCHA (fed.) | Flow-MLP | Random Forest |
|---|---|---|---|---|
| Benign | 28,712 | 99.7 / 79.6 | 96.1 / 80.6 | 96.4 / 82.5 |
| Bot | 132,571 | 100.0 / 100.0 | 100.0 / 100.0 | 100.0 / 100.0 |
| Brute force | **9** | 100.0 / 5.7 | 100.0 / 46.2 | 100.0 / 100.0 |
| DDoS | 2,604 | 47.5 / 64.4 | 60.8 / 75.6 | 60.8 / 75.6 |
| DoS | 15,028 | 89.8 / 94.6 | 99.8 / 99.9 | 99.6 / 99.8 |
| Infiltration | 20,513 | 42.5 / 59.5 | 46.5 / 61.2 | 53.2 / 67.2 |
| **Web** | 164 | **0.6** / 1.2 | 9.1 / 16.2 | 98.8 / 99.4 |

---

## 4. Analyses

### 4.1 XSS accounts for almost all of the gap to the Random Forest (ToN-IoT-v2)

Balanced accuracy and accuracy recomputed with XSS test flows left out of scoring (models unchanged):

| Model | Bal. acc. (all classes) | Bal. acc. (without XSS) | Accuracy (without XSS) |
|---|---|---|---|
| FCHA (federated) | 79.6 | **88.9** | 88.4 |
| FCHA (centralised) | 76.9 | 85.9 | 88.7 |
| Flow-MLP | 75.8 | 86.6 | 88.7 |
| Random Forest | 89.7 | **89.3** | 90.9 |

This is an analysis only. Dropping XSS from the main results would be cherry-picking.

### 4.2 Cost of federation

On ToN-IoT-v2, federated FCHA (79.6) scored *above* centralised FCHA (76.9) on the test set, even though centralised FCHA had the higher validation peak (92.1 vs 85.9). So the gap to the Random Forest is **not** caused by federation. Centralised FCHA overfits the training signatures more.

### 4.3 Attention mechanism (FCHA)

Attention lift = attention a flow puts on same-class flows on **mixed-traffic hosts**, divided by what uniform averaging would give (> 1 means attention picks out same-class traffic).

| Class | ToN-IoT v1 | ToN-IoT-v2 (fed.) | ToN-IoT-v2 (central.) | CIC-2018-v2 (fed.) |
|---|---|---|---|---|
| Backdoor | **3.18** | **4.02** | **3.17** | — |
| Scanning | 0.81 | 1.37 | 1.42 | — |
| Benign | 1.02 | 1.21 | 1.22 | 1.00 |
| Injection | 0.97 | 1.11 | 1.11 | — |
| DDoS | 1.02 | 1.07 | 1.11 | 0.98 |
| DoS | 0.55 | 0.58 | 0.57 | 1.04 |
| Web / XSS | 1.02 (XSS) | 0.96 (XSS) | 0.95 (XSS) | 0.75 (web) |
| Mixed hosts | 25 | 31 | 31 | 526 |

The Backdoor lift (3–4×) is the mechanism the method is designed for. Backdoor test counts are small (61–106 flows), so this needs confirming over more folds.

### 4.4 Effect of NetFlow v2 features (NF-ToN-IoT, FCHA)

| | v1 (14 columns) | v2 (45 columns) |
|---|---|---|
| Balanced accuracy | 61.6 | 79.6 |
| Password recall | 18.2 | 87.6 |
| Scanning recall | 0.0 | 81.5 |

The v1 and v2 runs used different training settings, so this shows the direction of the effect, not its exact size.

---

## 5. Comparison with the base paper (FedGATSage, Sci. Reports 2025)

| | Accuracy | Bal. acc. | F1 | Data / split |
|---|---|---|---|---|
| FedGATSage (reported) | 60.7 | 78.5 | 61.9 | NF-ToN-IoT v1; train/test split not described |
| Our FCHA, v1 | 68.8 | 61.6 | 51.4 | v1, signature-grouped (0% overlap) |
| Our FCHA, v2 | 70.9 | 79.6 | 75.6 | v2, signature-grouped (0% overlap) |

Not a like-for-like comparison (different dataset version and split). Observations from their tables:

- **The same XSS / Injection confusion, mirrored.** FedGATSage: XSS recall 0.999 with precision 0.42; Injection recall 0.341. Ours: Injection recall 92.9 with precision 26.9; XSS recall 14.7. This points to a property of NF-ToN-IoT, not of one model.
- Their Table 2 lists identical DDoS and DoS values for NF-ToN-IoT and CIC-ToN-IoT. Their Table 3 lists identical values for two pairs of configurations. Their Table 1 gives only plain accuracy, not balanced accuracy, for the centralised models.

---

## 6. Run inventory

| Dataset | Finished (test result) | Stopped / incomplete | Running |
|---|---|---|---|
| NF-ToN-IoT v1 | FCHA, Flow-MLP, Random Forest | Shuffled-label check | — |
| NF-ToN-IoT-v2 | FCHA, Flow-MLP, Random Forest, FCHA centralised | FCHA + SupCon (round 9, matched FCHA on validation) | — |
| NF-UNSW-NB15-v2 | — | FCHA (round 21, best validation 73.4) | — |
| NF-CSE-CIC-IDS2018-v2 | FCHA, Flow-MLP, Random Forest | FCHA centralised (round 20, best validation 99.2) | — |
| ToN-IoT Train_Test_Network | FCHA, Flow-MLP, Random Forest | — | — |

**13 finished runs, 4 stopped, none running.**

---

## 7. Caveats

1. **Single fold, single seed.** No standard deviations or significance tests yet.
2. **The CIC-IDS2018-v2 fold is badly skewed:** 66% of test flows are Bot, with only 9 brute-force and 164 web flows. Its balanced accuracy is unreliable until the signature grouping is made finer.
3. **Validation and test diverge.** Validation comes from the training signature groups, so it overstates test performance (e.g. CIC FCHA: 98.9 validation vs 68.6 test).
4. **Only IID clients** and only the signature split. Label-skewed and per-host partitions, and the unseen-attacker (host-disjoint) split, have not been run on v2.
5. The shuffled-label sanity check has not been completed on real data (it passed on synthetic data).

## 8. Where the raw results are

| What | Path |
|---|---|
| ToN-IoT v1 and v2 (read-only archive) | `results/archive/2026-11-22_nf_ton_iot/` |
| ToN-IoT-v2 (live, includes FCHA centralised) | `results/fedflow/nf_ton_iot_v2_fold0_local/` |
| CIC-IDS2018-v2 | `results/fedflow/nf_cse_cic_ids2018_v2_fold0_local/` |
| ToN-IoT Train_Test_Network | `results/fedflow/ton_iot_network_fold0_local/` |
| UNSW-NB15-v2 (partial log) | `results/archive/2026-11-22_nf_unsw_nb15_v2/` |
| Cross-dataset table and chart | `results/comparison/v2_fold0/` |

Each `results.jsonl` holds the full metrics, confusion matrix, split audit, training curve and attention analysis for every run.
