import render_equations
from latex2mathml.converter import convert as latex_to_mathml
import lxml.etree as ET
import re

xslt_path = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
xslt_doc = ET.parse(xslt_path)
xslt_transform = ET.XSLT(xslt_doc)

def clean_latex(latex_str):
    s = re.sub(r"^\$\$\s*", "", latex_str.strip())
    s = re.sub(r"\s*\$\$$", "", s)
    s = re.sub(r"\\tag\{[^}]+\}", "", s).strip()
    return s

for eq_id, info in render_equations.BEAUTIFIED_MATH.items():
    raw_latex = info['latex']
    cleaned = clean_latex(raw_latex)
    try:
        mml = latex_to_mathml(cleaned)
        omml = xslt_transform(ET.fromstring(mml))
        print(f"Eq {eq_id}: SUCCESS")
    except Exception as e:
        print(f"Eq {eq_id}: FAILED -> {e} | LaTeX: {cleaned}")
