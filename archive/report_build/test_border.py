import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()
sect = doc.sections[0]
sectPr = sect._sectPr
b = parse_xml(
    '<w:pgBorders ' + nsdecls('w') + ' w:offsetFrom="page">'
    '<w:top w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
    '<w:bottom w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
    '<w:left w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
    '<w:right w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
    '</w:pgBorders>'
)
sectPr.append(b)
doc.add_paragraph('Test border paragraph')
doc.save('test_border.docx')
print('Page border created successfully!')
