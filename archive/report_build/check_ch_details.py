import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("build_overleaf_tex.py", "r", encoding="utf-8") as f:
    text = f.read()

idx_ch2 = text.find(r"\chapter{Literature Survey}")
idx_ch3 = text.find(r"\chapter{Materials and Methods}")
ch2_text = text[idx_ch2:idx_ch3]
print("Chapter 2 length:", len(ch2_text))
print("Has longtable in ch2:", "\\begin{longtable}" in ch2_text)
print("Has table in ch2:", "\\begin{table}" in ch2_text)

idx_ch4 = text.find(r"\chapter{Methodology}")
idx_ch5 = text.find(r"\chapter{Results and Discussion}")
ch4_text = text[idx_ch4:idx_ch5]
print("Chapter 4 length:", len(ch4_text))
print("Has algorithm in ch4:", "\\begin{algorithm}" in ch4_text)
print("Algorithm count in ch4:", ch4_text.count("\\begin{algorithm}"))

idx_ch5 = text.find(r"\chapter{Results and Discussion}")
idx_ch6 = text.find(r"\chapter{Conclusion and Future Directions}")
ch5_text = text[idx_ch5:idx_ch6]
print("Chapter 5 length:", len(ch5_text))
print("Table count in ch5:", ch5_text.count("\\begin{table}"))
