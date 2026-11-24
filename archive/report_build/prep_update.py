import os
import sys

# Update assemble_massive_dissertation.py to render equations neatly

code_to_insert = '''
import render_equations

def create_neat_equation_table(doc, math_text, eq_number):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    tblPr = tbl._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="none"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

    c_math = tbl.cell(0, 0)
    c_num = tbl.cell(0, 1)

    c_math.width = Inches(5.8)
    c_num.width = Inches(0.7)

    p_m = c_math.paragraphs[0]
    p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_m.paragraph_format.space_before = Pt(8)
    p_m.paragraph_format.space_after = Pt(8)
    p_m.paragraph_format.line_spacing = 1.3

    run = p_m.add_run(math_text)
    run.font.name = 'Cambria Math'
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0x10, 0x10, 0x10)

    p_n = c_num.paragraphs[0]
    p_n.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_n.paragraph_format.space_before = Pt(8)
    p_n.paragraph_format.space_after = Pt(8)
    run_num = p_n.add_run(eq_number)
    run_num.font.name = 'Times New Roman'
    run_num.font.size = Pt(11)
    run_num.bold = True
    run_num.font.color.rgb = RGBColor(0x30, 0x30, 0x30)
'''
print("Snippet ready.")
