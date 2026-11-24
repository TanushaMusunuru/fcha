# -*- coding: utf-8 -*-
"""
Script to build the full, production-grade 60+ page Overleaf dissertation
adhering strictly to Amrita Vishwa Vidyapeetham template requirements:
- Exact front matter from Screenshots 1-7
- Single crisp border on every page
- Removed header and footer on every page (only top-right page numbers)
- Minimum 60 pages report
"""

import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

# Read existing chapter text from build_overleaf_tex.py
with open("build_overleaf_tex.py", "r", encoding="utf-8") as f:
    orig_code = f.read()

# Extract the body text from chapter 1 onwards
idx_ch1 = orig_code.find(r"\chapter{Introduction}")
idx_bib = orig_code.find(r"\begin{thebibliography}")
idx_end_bib = orig_code.find(r"\end{thebibliography}") + len(r"\end{thebibliography}")
idx_pub = orig_code.find(r"% LIST OF PUBLICATIONS")
idx_end_doc = orig_code.rfind(r"\end{document}")

print("Ch1 index:", idx_ch1)
print("Bib index:", idx_bib)
print("End Bib index:", idx_end_bib)
print("Pub index:", idx_pub)
print("End doc index:", idx_end_doc)
