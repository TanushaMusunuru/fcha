import re

with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect Table 3.1
pos = text.find("tab:dataset_distribution")
print("Table 3.1 chunk:\n", text[pos-80:pos+300])

# Let's inspect Table 3.2
pos2 = text.find("tab:dataset_unsw_distribution")
print("\nTable 3.2 chunk:\n", text[pos2-80:pos2+300])
