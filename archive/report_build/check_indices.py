import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("build_overleaf_tex.py", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect where chapters are
idx_doc = text.find(r"\begin{document}")
idx_ch1 = text.find(r"\chapter{Introduction}")
idx_ch2 = text.find(r"\chapter{Literature Survey}")
idx_ch3 = text.find(r"\chapter{Materials and Methods}")
idx_ch4 = text.find(r"\chapter{Methodology}")
idx_ch5 = text.find(r"\chapter{Results and Discussion}")
idx_ch6 = text.find(r"\chapter{Conclusion and Future Directions}")
idx_bib = text.find(r"\begin{thebibliography}")

print("Indices:")
print("doc:", idx_doc)
print("ch1:", idx_ch1)
print("ch2:", idx_ch2)
print("ch3:", idx_ch3)
print("ch4:", idx_ch4)
print("ch5:", idx_ch5)
print("ch6:", idx_ch6)
print("bib:", idx_bib)
