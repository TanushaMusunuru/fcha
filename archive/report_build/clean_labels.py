with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
seen_labels = set()

for i, line in enumerate(lines):
    # Check if line is just \label{foo}\n
    stripped = line.strip()
    if stripped.startswith(r"\label{") and stripped.endswith("}"):
        lbl = stripped[7:-1]
        if lbl in seen_labels:
            print(f"Removing duplicate standalone label at line {i+1}: {lbl}")
            continue
        seen_labels.add(lbl)
    else:
        # Check if line contains \label{foo}
        import re
        found = re.findall(r'\\label\{([^}]+)\}', line)
        for f in found:
            seen_labels.add(f)
    new_lines.append(line)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Finished cleaning duplicate labels!")
