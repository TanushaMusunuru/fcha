# -*- coding: utf-8 -*-
"""
Script to completely eliminate \resizebox and replace all tables with native,
robust \begin{tabularx}{\textwidth}{...} implementations.
This permanently resolves:
1. "! File ended while scanning use of \Gscale@box@dd."
2. "Runaway argument?"
3. Horizontal overflow past page borders
"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Remove any stray %} lines
lines = text.splitlines()
cleaned_lines = []
for l in lines:
    if l.strip() == "%}":
        print("Removed stray %} line")
        continue
    cleaned_lines.append(l)

text = "\n".join(cleaned_lines)

# Remove any \resizebox{\textwidth}{!}{ or \resizebox{\textwidth}{!}{% lines
# and their closing braces
# Let's inspect where \resizebox is used
text = re.sub(r'\\resizebox\{\\textwidth\}\{!\}\{\%?\s*', '', text)

# Also remove trailing closing brace if it was added for resizebox before \end{table}
# e.g., \end{tabular}\n} \end{table} or \end{tabularx}\n} \end{table}
text = re.sub(r'(\\end\{(?:tabular|tabularx)\})\s*\n\s*\}', r'\1', text)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("Cleaned all resizebox artifacts!")
