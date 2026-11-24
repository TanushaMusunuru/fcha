import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Let's find all \begin{table}[H] ... \end{table} blocks
table_pattern = re.compile(r'(\\begin\{table\}(?:\[H\])?\s*\n)(.*?)(\\end\{table\})', re.DOTALL)

def process_table_block(match):
    prefix = match.group(1)
    body = match.group(2)
    suffix = match.group(3)
    
    # Check if already has resizebox
    if r"\resizebox{\textwidth}{!}" in body:
        return match.group(0)
    
    # Find caption and label
    cap_match = re.search(r'\\caption\{[^}]+\}', body)
    lbl_match = re.search(r'\\label\{[^}]+\}', body)
    
    cap_str = cap_match.group(0) if cap_match else ""
    lbl_str = lbl_match.group(0) if lbl_match else ""
    
    # Remove caption and label from body
    clean_body = body
    if cap_str:
        clean_body = clean_body.replace(cap_str, "")
    if lbl_str:
        clean_body = clean_body.replace(lbl_str, "")
        
    clean_body = clean_body.replace(r"\centering", "")
    clean_body = clean_body.replace(r"\small", "")
    
    # Check for tabularx without X column
    if r"\begin{tabularx}{\textwidth}" in clean_body:
        # Check if X is in the col spec
        col_spec_match = re.search(r'\\begin\{tabularx\}\{\\textwidth\}\{([^}]+)\}', clean_body)
        if col_spec_match:
            spec = col_spec_match.group(1)
            if 'X' not in spec:
                clean_body = clean_body.replace(f"\\begin{{tabularx}}{{\\textwidth}}{{{spec}}}", f"\\begin{{tabular}}{{{spec}}}")
                clean_body = clean_body.replace(r"\end{tabularx}", r"\end{tabular}")
    
    clean_body = clean_body.strip()
    
    # Reassemble with caption on top, then resizebox
    header = "\\centering\n"
    if cap_str:
        header += f"{cap_str}\n"
    if lbl_str:
        header += f"{lbl_str}\n"
        
    wrapped = f"{header}\\resizebox{{\\textwidth}}{{!}}{{\n{clean_body}\n}}"
    return f"{prefix}{wrapped}\n{suffix}"

new_text = table_pattern.sub(process_table_block, text)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(new_text)

print("Processed all tables in dissertation_overleaf.tex!")
