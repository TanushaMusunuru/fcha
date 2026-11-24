# -*- coding: utf-8 -*-
with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Fix Table 8
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Headline Multi-Seed Performance Comparison on NF-ToN-IoT across Seeds 42, 43, 44.}" + "\n" + r"\label{tab:headline_results}" + "\n" + r"\begin{tabular}{l c c c c c c}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Headline Multi-Seed Performance Comparison on NF-ToN-IoT across Seeds 42, 43, 44.}" + "\n" + r"\label{tab:headline_results}" + "\n" + r"\footnotesize" + "\n" + r"\setlength{\tabcolsep}{3pt}" + "\n" + r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X c c c c c c}"
)

# Fix Table 10
# End tag of Table 10
pos10 = text.find("tab:ablation_progression")
end_tab10 = text.find(r"\end{tabular}", pos10)
if end_tab10 != -1:
    text = text[:end_tab10] + r"\end{tabularx}" + text[end_tab10 + len(r"\end{tabular}"):]
    print("Fixed Table 10 end tag!")

# Fix Table 11
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Controlled Node-Averaging Mechanism Test across Graph vs. Edge-Only Pipelines.}" + "\n" + r"\label{tab:node_averaging_test}" + "\n" + r"\begin{tabular}{l c c c c c}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Controlled Node-Averaging Mechanism Test across Graph vs. Edge-Only Pipelines.}" + "\n" + r"\label{tab:node_averaging_test}" + "\n" + r"\small" + "\n" + r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X c c c c c}"
)
pos11 = text.find("tab:node_averaging_test")
end_tab11 = text.find(r"\end{tabular}", pos11)
if end_tab11 != -1:
    text = text[:end_tab11] + r"\end{tabularx}" + text[end_tab11 + len(r"\end{tabular}"):]
    print("Fixed Table 11 end tag!")

# Fix Table 12
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Cross-Dataset Evaluation on NF-UNSW-NB15 Benchmark across 5 Random Seeds (42 to 46).}" + "\n" + r"\label{tab:unsw_results}" + "\n" + r"\begin{tabular}{l c c c c c}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\caption{Cross-Dataset Evaluation on NF-UNSW-NB15 Benchmark across 5 Random Seeds (42 to 46).}" + "\n" + r"\label{tab:unsw_results}" + "\n" + r"\small" + "\n" + r"\begin{tabularx}{\textwidth}{>{\raggedright\arraybackslash}X c c c c c}"
)
pos12 = text.find("tab:unsw_results")
end_tab12 = text.find(r"\end{tabular}", pos12)
if end_tab12 != -1:
    text = text[:end_tab12] + r"\end{tabularx}" + text[end_tab12 + len(r"\end{tabular}"):]
    print("Fixed Table 12 end tag!")

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("Applied fixes to Tables 8, 10, 11, 12!")
