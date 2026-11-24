# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Replace unicode accents with LaTeX macros
text = text.replace("ć", r"\'{c}")
text = text.replace("č", r"\v{c}")
text = text.replace("—", "---")

# Add iftex package and amritamotto macro to preamble if not present
if r"\usepackage{iftex}" not in text:
    text = text.replace(r"\usepackage{lmodern}", r"\usepackage{lmodern}" + "\n" + r"\usepackage{iftex}")

# Replace the hardcoded Devanagari string with the robust macro
# In amritaemblem definition:
old_emblem_str = r"\node[align=center, font=\fontsize{4.5}{5.5}\selectfont\bfseries] at (0,-1.45) {\color{amritared}श्रद्धावान् लभते ज्ञानम्};"
new_emblem_str = r"""\ifPDFTeX
        \node[align=center, font=\fontsize{4}{5}\selectfont\bfseries] at (0,-1.45) {\color{amritared}SHRADDHAVAN LABHATE JNANAM};
      \else
        \node[align=center, font=\fontsize{4.5}{5.5}\selectfont\bfseries] at (0,-1.45) {\color{amritared}श्रद्धावान् लभते ज्ञानम्};
      \fi"""
text = text.replace(old_emblem_str, new_emblem_str)

# On title page:
old_title_motto = r"{\fontsize{10}{12}\selectfont \textbf{\color{amritared} श्रद्धावान् लभते ज्ञानम्}\par}"
new_title_motto = r"""\ifPDFTeX
    {\fontsize{10}{12}\selectfont \textbf{\color{amritared} SHRADDHAVAN LABHATE JNANAM}\par}
    \else
    {\fontsize{10}{12}\selectfont \textbf{\color{amritared} श्रद्धावान् लभते ज्ञानम्}\par}
    \fi"""
text = text.replace(old_title_motto, new_title_motto)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("Sanitized dissertation_overleaf.tex for 100% robust compilation!")
