import sys
import re

with open("build_overleaf_tex.py", "r", encoding="utf-8") as f:
    content = f.read()

print("Total length of build_overleaf_tex.py:", len(content))
lines = content.splitlines()
print("Total lines:", len(lines))

# Search for section markers
markers = [i for i, line in enumerate(lines) if "\\chapter{" in line or "\\section{" in line]
print(f"Found {len(markers)} chapter/section markers.")
for idx in markers[:10]:
    print(f"Line {idx}: {lines[idx]}")
