import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def add_neat_equation(doc, math_runs, eq_num_str):
    """
    Inserts a neat, professionally aligned academic equation block:
    Uses a 1-row, 2-column borderless table where:
    - Col 1 (width ~5.7 in): Centered mathematical formula with mathematical styling
    - Col 2 (width ~0.8 in): Right-aligned equation number e.g. '(4.1)'
    """
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Borderless
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

    c_math.width = Inches(5.7)
    c_num.width = Inches(0.8)

    # Format Math cell
    p_m = c_math.paragraphs[0]
    p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_m.paragraph_format.space_before = Pt(4)
    p_m.paragraph_format.space_after = Pt(4)
    p_m.paragraph_format.line_spacing = 1.2

    for text, is_italic, is_bold, font_name, font_size in math_runs:
        run = p_m.add_run(text)
        run.italic = is_italic
        run.bold = is_bold
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    # Format Number cell
    p_n = c_num.paragraphs[0]
    p_n.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_n.paragraph_format.space_before = Pt(4)
    p_n.paragraph_format.space_after = Pt(4)
    run_num = p_n.add_run(eq_num_str)
    run_num.font.name = 'Times New Roman'
    run_num.font.size = Pt(11)
    run_num.bold = True
    run_num.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

doc = docx.Document()
add_neat_equation(doc, [
    ("x", True, False, "Cambria Math", 12),
    ("ᵤ = ", False, False, "Cambria Math", 12),
    ("1", False, False, "Cambria Math", 12),
    (" / deg(", False, False, "Cambria Math", 12),
    ("u", True, False, "Cambria Math", 12),
    (") ∑", False, False, "Cambria Math", 13),
    ("₍ᵤ, ᵥ₎ ∈ ℰ ", False, False, "Cambria Math", 11),
    ("e", True, False, "Cambria Math", 12),
    ("ᵤᵥ", False, False, "Cambria Math", 10)
], "(3.1)")

doc.save("test_neat_math.docx")
print("Neat math docx created successfully.")
