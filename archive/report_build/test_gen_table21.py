import sys
sys.stdout.reconfigure(encoding='utf-8')
import text_ch2

def generate_lit_table_latex():
    tex = []
    tex.append(r"\begin{longtable}{|p{2.6cm}|p{2.8cm}|p{2.0cm}|p{4.2cm}|p{3.8cm}|}")
    tex.append(r"\caption{Comprehensive Scholarly Survey of 15 Foundational and Contemporary Research Works in IoT Intrusion Detection.}\label{tab:lit_survey}\\")
    tex.append(r"\hline")
    tex.append(r"\textbf{Authors \& Year} & \textbf{Proposed Model} & \textbf{Benchmark Dataset} & \textbf{Key Empirical Findings} & \textbf{Critical Architectural Shortcoming} \\")
    tex.append(r"\hline")
    tex.append(r"\endfirsthead")
    tex.append(r"\hline")
    tex.append(r"\textbf{Authors \& Year} & \textbf{Proposed Model} & \textbf{Benchmark Dataset} & \textbf{Key Empirical Findings} & \textbf{Critical Architectural Shortcoming} \\")
    tex.append(r"\hline")
    tex.append(r"\endhead")
    tex.append(r"\hline \multicolumn{5}{r}{\footnotesize Continued on next page\dots} \\")
    tex.append(r"\endfoot")
    tex.append(r"\hline")
    tex.append(r"\endlastfoot")
    
    for row in text_ch2.LIT_TABLE_ROWS:
        authors, model, dataset, findings, shortcomings = row
        # Clean latex special chars
        def clean(s):
            return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
        tex.append(f"{clean(authors)} & {clean(model)} & {clean(dataset)} & {clean(findings)} & {clean(shortcomings)} \\\\")
        tex.append(r"\hline")
        
    tex.append(r"\end{longtable}")
    return "\n".join(tex)

s = generate_lit_table_latex()
print("Generated Table 2.1 length:", len(s))
print(s[:500])
