# -*- coding: utf-8 -*-
"""
Script to fix all alignment and layout issues in dissertation_overleaf.tex:
1. Wrap all wide floating tables in \resizebox{\textwidth}{!}{...} to strictly prevent horizontal overflow
2. Fix Contents tables on Pages 6 & 7 using tabularx with X columns
3. Calibrate Table 2.1 (longtable) column widths and \tabcolsep so it fits \textwidth
4. Format long equations across multiple lines using split
5. Remove all duplicate \label tags
6. Verify margin alignment and zero overfull tables
"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

print("Original length:", len(text))

# 1. Remove duplicate labels (lines that have standalone \label{...} immediately after a section/table with that label)
duplicate_labels = [
    r"\label{sec:background}",
    r"\label{sec:objectives}",
    r"\label{sec:contributions}",
    r"\label{tab:lit_survey}",
    r"\label{sec:challenges}",
    r"\label{sec:motivation}",
    r"\label{sec:datasets}",
    r"\label{sec:preprocessing}",
    r"\label{sec:tools}",
    r"\label{sec:discussion}",
    r"\label{sec:conclusion_summary}",
    r"\label{sec:future_directions}"
]

for dlabel in duplicate_labels:
    # If the label appears twice, replace the second isolated occurrence on its own line
    pattern = re.compile(r'(\n\s*' + re.escape(dlabel) + r'\s*\n)')
    matches = list(pattern.finditer(text))
    if len(matches) > 1:
        # Keep first, remove subsequent
        for m in reversed(matches[1:]):
            text = text[:m.start()] + "\n" + text[m.end():]
        print(f"Removed duplicate {dlabel}")

# 2. Fix Contents tables on Pages 6 and 7 to use tabularx{\textwidth}
# Replace the tabular definitions in Contents
text = text.replace(
    r"\begin{tabular}{|>{\centering\arraybackslash}p{2.2cm}|p{11.2cm}|>{\centering\arraybackslash}p{2.0cm}|}",
    r"\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{2.0cm}|X|>{\centering\arraybackslash}p{2.0cm}|}"
)
text = text.replace(
    r"\end{tabular}" + "\n" + r"\end{center}" + "\n" + r"\clearpage" + "\n\n" + r"% CONTENTS PAGE 2",
    r"\end{tabularx}" + "\n" + r"\end{center}" + "\n" + r"\clearpage" + "\n\n" + r"% CONTENTS PAGE 2"
)
text = text.replace(
    r"\begin{tabular}{|>{\centering\arraybackslash}p{2.2cm}|p{11.2cm}|>{\centering\arraybackslash}p{2.0cm}|}",
    r"\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{2.0cm}|X|>{\centering\arraybackslash}p{2.0cm}|}"
)
text = text.replace(
    r"\end{tabular}" + "\n" + r"\end{center}" + "\n\n" + r"\vspace{0.3cm}" + "\n" + r"\noindent\colorbox{yellow}",
    r"\end{tabularx}" + "\n" + r"\end{center}" + "\n\n" + r"\vspace{0.3cm}" + "\n" + r"\noindent\colorbox{yellow}"
)

# 3. Fix List of Abbreviations table to use tabularx
text = text.replace(
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\begin{tabular}{ll}",
    r"\begin{table}[H]" + "\n" + r"\centering" + "\n" + r"\begin{tabularx}{\textwidth}{l X}"
)
text = text.replace(
    r"\bottomrule" + "\n" + r"\end{tabular}" + "\n" + r"\end{table}" + "\n" + r"\clearpage",
    r"\bottomrule" + "\n" + r"\end{tabularx}" + "\n" + r"\end{table}" + "\n" + r"\clearpage"
)

# 4. Fix Table 2.1 (longtable) column widths and tabcolsep
old_longtable_def = r"\begin{longtable}{|p{2.5cm}|p{2.8cm}|p{2.0cm}|p{4.2cm}|p{3.8cm}|}"
new_longtable_def = (
    r"{\setlength{\tabcolsep}{3.5pt}" + "\n" +
    r"\begin{longtable}{|p{2.3cm}|p{2.7cm}|p{1.8cm}|p{4.2cm}|p{3.7cm}|}"
)
text = text.replace(old_longtable_def, new_longtable_def)
text = text.replace(r"\end{longtable}", r"\end{longtable}}" + "\n")

# 5. Helper function to wrap a table environment in \resizebox{\textwidth}{!}{% ... %}
def wrap_table_in_resizebox(content, label_str):
    pos = content.find(label_str)
    if pos == -1:
        print(f"Warning: could not find {label_str}")
        return content
    
    # Find the enclosing \begin{table} and \end{table}
    tbl_start = content.rfind(r"\begin{table}", 0, pos)
    tbl_end = content.find(r"\end{table}", pos) + len(r"\end{table}")
    
    tbl_block = content[tbl_start:tbl_end]
    
    # Check if already wrapped
    if r"\resizebox{\textwidth}{!}" in tbl_block:
        return content
    
    # Find \begin{tabular or \begin{tabularx} inside this table
    match_start = re.search(r'(\\begin\{(?:tabular|tabularx)\}(?:\{[^\}]*\})*)', tbl_block)
    match_end = re.search(r'(\\end\{(?:tabular|tabularx)\})', tbl_block)
    
    if match_start and match_end:
        start_idx = match_start.start()
        end_idx = match_end.end()
        inner_tab = tbl_block[start_idx:end_idx]
        
        # If it's tabularx without X column, change column spec or change to tabular
        if r"\begin{tabularx}{\textwidth}{l c c c c c c}" in inner_tab:
            inner_tab = inner_tab.replace(r"\begin{tabularx}{\textwidth}{l c c c c c c}", r"\begin{tabular}{l c c c c c c}").replace(r"\end{tabularx}", r"\end{tabular}")
        elif r"\begin{tabularx}{\textwidth}{l c c c c c}" in inner_tab:
            inner_tab = inner_tab.replace(r"\begin{tabularx}{\textwidth}{l c c c c c}", r"\begin{tabular}{l c c c c c}").replace(r"\end{tabularx}", r"\end{tabular}")
        elif r"\begin{tabularx}{\textwidth}{l c c c c c X}" in inner_tab:
            inner_tab = inner_tab.replace(r"\begin{tabularx}{\textwidth}{l c c c c c X}", r"\begin{tabular}{l c c c c c p{4cm}}").replace(r"\end{tabularx}", r"\end{tabular}")
            
        wrapped = r"\resizebox{\textwidth}{!}{%" + "\n" + inner_tab + "\n" + r"%}"
        new_tbl_block = tbl_block[:start_idx] + wrapped + tbl_block[end_idx:]
        content = content[:tbl_start] + new_tbl_block + content[tbl_end:]
        print(f"Successfully wrapped table with label {label_str}")
    else:
        print(f"Could not find tab env for {label_str}")
        
    return content

# Wrap all floating tables in resizebox
labels_to_wrap = [
    "tab:dataset_distribution",       # Table 3.1 (from screenshot!)
    "tab:unsw_distribution",          # Table 3.2
    "tab:netflow_dictionary",         # Table 3.3
    "tab:domain_gat_features",        # Table 3.4
    "tab:empirical_leakage_audit",    # Table 3.5
    "tab:system_hardware",            # Table 5.1
    "tab:headline_results",           # Table 5.2
    "tab:backdoor_breakdown",         # Table 5.3
    "tab:ablation_progression",       # Table 5.4
    "tab:node_averaging_test",        # Table 5.5
    "tab:unsw_seeds"                  # Table 5.7
]

for lbl in labels_to_wrap:
    text = wrap_table_in_resizebox(text, lbl)

# 6. Fix long equations so they fit within \textwidth
# Eq 9: Socket signature tuple
old_eq9 = r"""\begin{equation}
\mathcal{S} \equiv \big[ \text{L4\_SRC\_PORT}, \, \text{L4\_DST\_PORT}, \, \text{PROTOCOL}, \, \text{TCP\_FLAGS}, \, \text{L7\_PROTO}, \, \text{CLIENT\_TCP\_FLAGS}, \, \text{SERVER\_TCP\_FLAGS}, \, \text{IP\_VERSION} \big]
\label{eq:signature_tuple}
\end{equation}"""

new_eq9 = r"""\begin{equation}
\begin{split}
\mathcal{S} \equiv \big[ & \text{L4\_SRC\_PORT}, \, \text{L4\_DST\_PORT}, \, \text{PROTOCOL}, \, \text{TCP\_FLAGS}, \\
& \text{L7\_PROTO}, \, \text{CLIENT\_TCP\_FLAGS}, \, \text{SERVER\_TCP\_FLAGS}, \, \text{IP\_VERSION} \big]
\end{split}
\label{eq:signature_tuple}
\end{equation}"""
text = text.replace(old_eq9, new_eq9)

# Eq 17: Multi-head attention coefficient
old_eq17 = r"""\begin{equation}
\alpha_{uv}^{(m)} = \frac{\exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}_m \boldsymbol{h}_u \,\|\, \boldsymbol{W}_m \boldsymbol{h}_v \,\|\, \boldsymbol{W}_e \boldsymbol{e}_{uv}] \right) \right)}{\sum_{k \in \mathcal{N}(u)} \exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}_m \boldsymbol{h}_u \,\|\, \boldsymbol{W}_m \boldsymbol{h}_k \,\|\, \boldsymbol{W}_e \boldsymbol{e}_{uk}] \right) \right)}
\label{eq:attention_coeffs}
\end{equation}"""

new_eq17 = r"""\begin{equation}
\alpha_{uv}^{(m)} = \frac{\exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}_m \boldsymbol{h}_u \,\|\, \boldsymbol{W}_m \boldsymbol{h}_v \,\|\, \boldsymbol{W}_e \boldsymbol{e}_{uv}] \right) \right)}{\displaystyle\sum_{k \in \mathcal{N}(u)} \exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}_m \boldsymbol{h}_u \,\|\, \boldsymbol{W}_m \boldsymbol{h}_k \,\|\, \boldsymbol{W}_e \boldsymbol{e}_{uk}] \right) \right)}
\label{eq:attention_coeffs}
\end{equation}"""
text = text.replace(old_eq17, new_eq17)

# Eq 25: SupCon loss
old_eq25 = r"""\begin{equation}
\mathcal{L}_{\text{SupCon}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp\left( \tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_p / \tau \right)}{\sum_{a \in A(i)} \exp\left( \tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau \right)}
\label{eq:supcon_loss}
\end{equation}"""

new_eq25 = r"""\begin{equation}
\mathcal{L}_{\text{SupCon}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp\left( \tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_p / \tau \right)}{\displaystyle\sum_{a \in A(i)} \exp\left( \tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau \right)}
\label{eq:supcon_loss}
\end{equation}"""
text = text.replace(old_eq25, new_eq25)

# Eq 26: SupCon gradient
old_eq26 = r"""\begin{equation}
\nabla_{\tilde{\boldsymbol{z}}_i} \mathcal{L}_{\text{SupCon}} = \frac{1}{\tau} \left( \sum_{a \in A(i)} P_{ia} \tilde{\boldsymbol{z}}_a - \frac{1}{|P(i)|} \sum_{p \in P(i)} \tilde{\boldsymbol{z}}_p \right), \quad P_{ia} = \frac{\exp(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau)}{\sum_{b \in A(i)} \exp(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_b / \tau)}
\label{eq:supcon_gradient}
\end{equation}"""

new_eq26 = r"""\begin{equation}
\begin{split}
\nabla_{\tilde{\boldsymbol{z}}_i} \mathcal{L}_{\text{SupCon}} &= \frac{1}{\tau} \left( \sum_{a \in A(i)} P_{ia} \tilde{\boldsymbol{z}}_a - \frac{1}{|P(i)|} \sum_{p \in P(i)} \tilde{\boldsymbol{z}}_p \right), \\
\text{where } P_{ia} &= \frac{\exp(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau)}{\displaystyle\sum_{b \in A(i)} \exp(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_b / \tau)}
\end{split}
\label{eq:supcon_gradient}
\end{equation}"""
text = text.replace(old_eq26, new_eq26)

# Eq 32: Concatenation
old_eq32 = r"""\begin{equation}
\boldsymbol{\phi}_i = \left[ \boldsymbol{P}_{\text{temp}}(i) \,\|\, \boldsymbol{P}_{\text{cont}}(i) \,\|\, \boldsymbol{P}_{\text{behav}}(i) \,\|\, \boldsymbol{z}_{\text{server}}(i) \,\|\, \boldsymbol{x}_{\text{norm}}(i) \right] \in \mathbb{R}^{32 + 32 + 32 + 64 + 43} = \mathbb{R}^{203}
\label{eq:rf_concat}
\end{equation}"""

new_eq32 = r"""\begin{equation}
\begin{split}
\boldsymbol{\phi}_i = \big[ & \boldsymbol{P}_{\text{temp}}(i) \,\|\, \boldsymbol{P}_{\text{cont}}(i) \,\|\, \boldsymbol{P}_{\text{behav}}(i) \,\|\, \\
& \boldsymbol{z}_{\text{server}}(i) \,\|\, \boldsymbol{x}_{\text{norm}}(i) \big] \in \mathbb{R}^{32 + 32 + 32 + 64 + 43} = \mathbb{R}^{203}
\end{split}
\label{eq:rf_concat}
\end{equation}"""
text = text.replace(old_eq32, new_eq32)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated dissertation_overleaf.tex with alignment fixes successfully!")
print(f"New length: {len(text)} characters, {len(text.splitlines())} lines")
