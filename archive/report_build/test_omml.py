import docx
from docx.oxml import parse_xml

doc = docx.Document()
p = doc.add_paragraph("Here is an equation:")
omml_xml = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:sSub>'
    '<m:e><m:r><m:t>x</m:t></m:r></m:e>'
    '<m:sub><m:r><m:t>u</m:t></m:r></m:sub>'
    '</m:sSub>'
    '<m:r><m:t> = </m:t></m:r>'
    '<m:f>'
    '<m:num><m:r><m:t>1</m:t></m:r></m:num>'
    '<m:den><m:r><m:t>deg(u)</m:t></m:r></m:den>'
    '</m:f>'
    '<m:nary>'
    '<m:naryPr><m:chr m:val="∑"/></m:naryPr>'
    '<m:sub><m:r><m:t>(u,v)∈E</m:t></m:r></m:sub>'
    '<m:sup/>'
    '<m:e><m:sSub><m:e><m:r><m:t>e</m:t></m:r></m:e><m:sub><m:r><m:t>uv</m:t></m:r></m:sub></m:sSub></m:e>'
    '</m:nary>'
    '</m:oMath>'
    '</m:oMathPara>'
)

try:
    p._p.append(parse_xml(omml_xml))
    doc.save("test_omml_native.docx")
    print("Native OMML appended and saved successfully.")
except Exception as e:
    print("OMML error:", e)
