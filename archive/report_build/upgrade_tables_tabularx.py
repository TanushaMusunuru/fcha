# -*- coding: utf-8 -*-
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Table 2 (Table 3.1): NF-ToN-IoT Ground-Truth Class Distribution
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{NF-ToN-IoT Ground-Truth Class Distribution and 5-Fold Signature-Grouped Split Support (Seed 42).}" + "\n" + r"\label{tab:dataset_distribution}" + "\n" + r"\small" + "\n" + r"\begin{tabular}{lrrrr}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{NF-ToN-IoT Ground-Truth Class Distribution and 5-Fold Signature-Grouped Split Support (Seed 42).}" + "\n" + r"\label{tab:dataset_distribution}" + "\n" + r"\small" + "\n" + r"\begin{tabularx}{\textwidth}{Xrrrr}"
)
text = text.replace(
    r"\textbf{Total Benchmark} & $\mathbf{1,377,837}$ & $\mathbf{100.00\%}$ & $\mathbf{1,102,269}$ & $\mathbf{275,568}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}",
    r"\textbf{Total Benchmark} & $\mathbf{1,377,837}$ & $\mathbf{100.00\%}$ & $\mathbf{1,102,269}$ & $\mathbf{275,568}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabularx}"
)

# 2. Table 3 (Table 3.2): NF-UNSW-NB15 Benchmark Class Distribution
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{NF-UNSW-NB15 Benchmark Class Distribution across 5-Fold Signature-Grouped Split.}" + "\n" + r"\label{tab:unsw_distribution}" + "\n" + r"\small" + "\n" + r"\begin{tabular}{lrrrr}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{NF-UNSW-NB15 Benchmark Class Distribution across 5-Fold Signature-Grouped Split.}" + "\n" + r"\label{tab:unsw_distribution}" + "\n" + r"\small" + "\n" + r"\begin{tabularx}{\textwidth}{Xrrrr}"
)
text = text.replace(
    r"\textbf{Total Benchmark} & $\mathbf{1,623,118}$ & $\mathbf{100.00\%}$ & $\mathbf{1,298,819}$ & $\mathbf{324,299}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}",
    r"\textbf{Total Benchmark} & $\mathbf{1,623,118}$ & $\mathbf{100.00\%}$ & $\mathbf{1,298,819}$ & $\mathbf{324,299}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabularx}"
)

# 3. Table 8 (Table 5.2): Headline Results
old_t8 = r"""\begin{table}[H]
\centering
\caption{Headline Multi-Seed Performance Comparison on NF-ToN-IoT across Seeds 42, 43, 44.}
\label{tab:headline_results}
\small
\begin{tabular}{l c c c c c c}
\toprule
\textbf{Model Architecture} & \textbf{Accuracy (\%)} & \textbf{BalAcc (\%)} & \textbf{Macro F1 (\%)} & \textbf{Macro FNR (\%)} & \textbf{Backdoor Rec} & \textbf{Scanning Rec} \\"""

new_t8 = r"""\begin{table}[H]
\centering
\caption{Headline Multi-Seed Performance Comparison on NF-ToN-IoT across Seeds 42, 43, 44.}
\label{tab:headline_results}
\footnotesize
\setlength{\tabcolsep}{3pt}
\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X c c c c c c}
\toprule
\textbf{Model Architecture} & \textbf{Acc (\%)} & \textbf{BalAcc (\%)} & \textbf{F1 (\%)} & \textbf{FNR (\%)} & \textbf{Backdoor} & \textbf{Scanning} \\"""

text = text.replace(old_t8, new_t8)
# Replace matching end
text = text.replace(
    r"$\mu = 0.5$ (SupCon + CB-Focal) & $91.49 \pm 0.47$ & $86.04 \pm 3.06$ & $88.75 \pm 3.53$ & $13.96 \pm 3.06$ & $99.08 \pm 0.40\%$ & $91.03 \pm 12.40\%$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}",
    r"$\mu = 0.5$ (SupCon + CB-Focal) & $91.49 \pm 0.47$ & $86.04 \pm 3.06$ & $88.75 \pm 3.53$ & $13.96 \pm 3.06$ & $99.08 \pm 0.40\%$ & $91.03 \pm 12.40\%$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabularx}"
)

# 4. Table 9 (Table 5.3): Gain decomposition
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Mathematical Decomposition of Balanced Accuracy Gain from $\mu=0.0$ to $\mu=0.1$.}" + "\n" + r"\label{tab:gain_decomposition}" + "\n" + r"\small" + "\n" + r"\begin{tabular}{lrrrrr}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Mathematical Decomposition of Balanced Accuracy Gain from $\mu=0.0$ to $\mu=0.1$.}" + "\n" + r"\label{tab:gain_decomposition}" + "\n" + r"\small" + "\n" + r"\begin{tabularx}{\textwidth}{Xrrrrr}"
)
text = text.replace(
    r"\textbf{Total Sum} & & & & $\mathbf{+13.59\%}$ & $\mathbf{100.00\%}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}",
    r"\textbf{Total Sum} & & & & $\mathbf{+13.59\%}$ & $\mathbf{100.00\%}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabularx}"
)

# 5. Table 10 (Table 5.4): Ablation Progression
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Cumulative Component Ablation Progression across Seeds 42, 43, 44.}" + "\n" + r"\label{tab:ablation_progression}" + "\n" + r"\small" + "\n" + r"\begin{tabular}{l c c c c c p{4cm}}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Cumulative Component Ablation Progression across Seeds 42, 43, 44.}" + "\n" + r"\label{tab:ablation_progression}" + "\n" + r"\footnotesize" + "\n" + r"\setlength{\tabcolsep}{3pt}" + "\n" + r"\begin{tabularx}{\textwidth}{l c c c c c X}"
)
text = text.replace(
    r"\textbf{(d) + SupCon ($\mu=0.1$)} & $\mathbf{93.96 \pm 0.94}$ & $\mathbf{94.28 \pm 1.47}$ & $\mathbf{95.61 \pm 1.15}$ & $\mathbf{5.72 \pm 1.47}$ & $\mathbf{99.57 \pm 0.20\%}$ & \textbf{Statistically Validated} \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}",
    r"\textbf{(d) + SupCon ($\mu=0.1$)} & $\mathbf{93.96 \pm 0.94}$ & $\mathbf{94.28 \pm 1.47}$ & $\mathbf{95.61 \pm 1.15}$ & $\mathbf{5.72 \pm 1.47}$ & $\mathbf{99.57 \pm 0.20\%}$ & \textbf{Statistically Validated} \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabularx}"
)

# 6. Table 11 (Table 5.5): Node-averaging test
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Controlled Node-Averaging Mechanism Test across Graph vs. Edge-Only Pipelines.}" + "\n" + r"\label{tab:node_averaging_test}" + "\n" + r"\small" + "\n" + r"\begin{tabular}{l c c c c c}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Controlled Node-Averaging Mechanism Test across Graph vs. Edge-Only Pipelines.}" + "\n" + r"\label{tab:node_averaging_test}" + "\n" + r"\small" + "\n" + r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X c c c c c}"
)
text = text.replace(
    r"\textbf{Proposed Full Model ($\mu=0.1$)} & \textbf{Enabled (GNN Graph)} & $\mathbf{94.28 \pm 1.47\%}$ & $\mathbf{95.61 \pm 1.15\%}$ & $\mathbf{99.57 \pm 0.20\%}$ & $\mathbf{97.98 \pm 3.38\%}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}",
    r"\textbf{Proposed Full Model ($\mu=0.1$)} & \textbf{Enabled (GNN Graph)} & $\mathbf{94.28 \pm 1.47\%}$ & $\mathbf{95.61 \pm 1.15\%}$ & $\mathbf{99.57 \pm 0.20\%}$ & $\mathbf{97.98 \pm 3.38\%}$ \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabularx}"
)

# 7. Table 12 (Table 5.7): Cross-Dataset Evaluation
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Cross-Dataset Evaluation on NF-UNSW-NB15 Benchmark across 5 Random Seeds (42 to 46).}" + "\n" + r"\label{tab:unsw_results}" + "\n" + r"\small" + "\n" + r"\begin{tabular}{l c c c c c}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Cross-Dataset Evaluation on NF-UNSW-NB15 Benchmark across 5 Random Seeds (42 to 46).}" + "\n" + r"\label{tab:unsw_results}" + "\n" + r"\small" + "\n" + r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X c c c c c}"
)
text = text.replace(
    r"\textbf{Proposed ($\mu = 0.1$)} & \textbf{5 Seeds (42--46)} & $\mathbf{94.12 \pm 0.31\%}$ & $\mathbf{94.88 \pm 0.28\%}$ & $\mathbf{5.88 \pm 0.31\%}$ & \textbf{0 / 5 Seeds (Robust)} \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}",
    r"\textbf{Proposed ($\mu = 0.1$)} & \textbf{5 Seeds (42--46)} & $\mathbf{94.12 \pm 0.31\%}$ & $\mathbf{94.88 \pm 0.28\%}$ & $\mathbf{5.88 \pm 0.31\%}$ & \textbf{0 / 5 Seeds (Robust)} \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabularx}"
)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("All tables successfully upgraded to native tabularx!")
