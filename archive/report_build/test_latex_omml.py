import docx
import latex2mathml.commands
from latex2mathml.converter import convert as latex_to_mathml
import lxml.etree as ET
from docx.oxml import parse_xml

xslt_path = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
xslt_doc = ET.parse(xslt_path)
xslt_transform = ET.XSLT(xslt_doc)

def latex_to_omml(latex_code):
    mathml = latex_to_mathml(latex_code)
    mml_dom = ET.fromstring(mathml)
    omml_dom = xslt_transform(mml_dom)
    return str(omml_dom)

doc = docx.Document()
p = doc.add_paragraph("Test LaTeX converted to native Word OMML equation:")

# Test equation: x_u = \frac{1}{\text{deg}(u)} \sum_{(u, v) \in \mathcal{E}} e_{uv}
latex_sample = r"x_u = \frac{1}{\text{deg}(u)} \sum_{(u, v) \in \mathcal{E}} e_{uv}"
omml_str = latex_to_omml(latex_sample)
print("OMML generated:")
print(omml_str[:200])

omml_element = parse_xml(omml_str)
p._p.append(omml_element)
doc.save("test_converted_omml.docx")
print("Saved test_converted_omml.docx successfully!")
