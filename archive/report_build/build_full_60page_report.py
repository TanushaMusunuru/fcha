# Python script to generate the complete, production-grade Overleaf LaTeX dissertation
# satisfying:
# 1. Exact template format from Screenshots 1 to 7 (Amrita Vishwa Vidyapeetham, Amaravati)
# 2. Single crisp border on every page
# 3. Header and footer removed on every page (only top-right page numbers)
# 4. Minimum 60 pages report (exhaustive academic text, all equations, all tables, algorithms, citations)

import os
import sys

output_tex_path = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\dissertation_overleaf.tex"

# Let's import the chapter text modules to verify and incorporate rich tables and text
import text_ch1
import text_ch2
import text_ch3
import text_ch4
import text_ch5
import text_ch6

print("Imported text_ch1 through text_ch6 successfully.")
