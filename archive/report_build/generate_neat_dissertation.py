import os
import sys
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

import render_equations
import text_ch1
import text_ch2
import text_ch3
import text_ch4
import text_ch5
import text_ch6
from latex2mathml.converter import convert as latex_to_mathml
import lxml.etree as ET

xslt_path = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
xslt_doc = ET.parse(xslt_path)
xslt_transform = ET.XSLT(xslt_doc)

def latex_to_omml(latex_code):
    mathml = latex_to_mathml(latex_code)
    mml_dom = ET.fromstring(mathml)
    omml_dom = xslt_transform(mml_dom)
    return str(omml_dom)

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_dissertation(output_docx_path, output_md_path, figures_dir):
    doc = docx.Document()
    md_content = []

    # Configure Margins: 1.0 inch (Amrita Standard) + Professional Academic Page Borders
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True

        sectPr = section._sectPr
        pgBorders = parse_xml(
            f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page">'
            f'<w:top w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
            f'<w:left w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
            f'<w:bottom w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
            f'<w:right w:val="single" w:sz="12" w:space="24" w:color="1A365D"/>'
            f'</w:pgBorders>'
        )
        sectPr.append(pgBorders)

    # Base Normal Style
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, line_spacing=1.5, bold=False, italic=False, font_size=12, color_rgb=(0,0,0)):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            run.bold = bold
            run.italic = italic
            run.font.name = 'Times New Roman'
            run.font.size = Pt(font_size)
            run.font.color.rgb = RGBColor(*color_rgb)
        return p

    def add_neat_equation(math_unicode, eq_num_str, latex_eq=None):
        """
        Inserts a neat, professionally formatted academic equation:
        Uses a 1-row, 2-column table:
        - Col 1 (width 5.8 in): Centered native Word OMML equation object!
        - Col 2 (width 0.7 in): Right-aligned equation number e.g. (4.1)
        """
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

        inserted_omml = False
        if latex_eq:
            try:
                cleaned_lat = re.sub(r"^\$\$\s*", "", latex_eq.strip())
                cleaned_lat = re.sub(r"\s*\$\$$", "", cleaned_lat)
                cleaned_lat = re.sub(r"\\tag\{[^}]+\}", "", cleaned_lat).strip()
                omml_str = latex_to_omml(cleaned_lat)
                omml_elm = parse_xml(omml_str)
                p_m._p.append(omml_elm)
                inserted_omml = True
            except Exception as e:
                print(f"OMML conversion failed for {eq_num_str}: {e}")

        if not inserted_omml:
            run = p_m.add_run(math_unicode)
            run.font.name = 'Cambria Math'
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

        p_n = c_num.paragraphs[0]
        p_n.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_n.paragraph_format.space_before = Pt(8)
        p_n.paragraph_format.space_after = Pt(8)
        run_num = p_n.add_run(eq_num_str)
        run_num.font.name = 'Times New Roman'
        run_num.font.size = Pt(11)
        run_num.bold = True
        run_num.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

        if latex_eq:
            md_content.append(f"\n\n{latex_eq}\n\n")

    def add_chapter_heading(chap_num, title):
        doc.add_page_break()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(f"CHAPTER {chap_num}")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x8B, 0x00, 0x00)

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(22)
        run2 = p2.add_run(title.upper())
        run2.bold = True
        run2.font.name = 'Times New Roman'
        run2.font.size = Pt(14)
        run2.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)

        md_content.append(f"\n\n# CHAPTER {chap_num}: {title.upper()}\n")

    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x20, 0x30, 0x50)

        md_content.append(f"\n## {title}\n")

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.italic = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.font.color.rgb = RGBColor(0x30, 0x40, 0x60)

        md_content.append(f"\n### {title}\n")

    def add_smart_paragraph(text):
        """
        Detects if text contains an equation like '(Eq. X.Y)', extracts the equation,
        renders it in a dedicated equation table block, and outputs surrounding text normally.
        """
        match = re.search(r"\((?:Eq\.\s*)?(\d+\.\d+)\)", text)
        if match:
            eq_id = match.group(1)
            # Find the line containing the equation
            lines = text.split("\n")
            pre_lines = []
            post_lines = []
            eq_found = False
            for line in lines:
                if f"({eq_id})" in line or f"(Eq. {eq_id})" in line:
                    eq_found = True
                    continue
                if not eq_found:
                    pre_lines.append(line)
                else:
                    post_lines.append(line)

            pre_text = "\n".join(pre_lines).strip()
            post_text = "\n".join(post_lines).strip()

            if pre_text:
                add_p(pre_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.5, font_size=12)
                md_content.append(pre_text + "\n")

            # Lookup beautified math
            math_info = render_equations.BEAUTIFIED_MATH.get(eq_id)
            if math_info:
                add_neat_equation(math_info["unicode"], f"({eq_id})", math_info["latex"])
            else:
                add_p(f"Equation ({eq_id})", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)

            if post_text:
                add_p(post_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=8, line_spacing=1.5, font_size=12)
                md_content.append(post_text + "\n")
        else:
            add_p(text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=8, line_spacing=1.5, font_size=12)
            md_content.append(text + "\n")

    def add_bullet_item(bold_prefix, item_text):
        bp = doc.add_paragraph()
        bp.paragraph_format.left_indent = Inches(0.25)
        bp.paragraph_format.space_after = Pt(6)
        bp.paragraph_format.line_spacing = 1.5
        r_bt = bp.add_run("• " + bold_prefix)
        r_bt.bold = True
        r_bt.font.name = 'Times New Roman'
        r_bd = bp.add_run(item_text)
        r_bd.font.name = 'Times New Roman'

        md_content.append(f"- **{bold_prefix}** {item_text}")

    def add_image_figure(img_filename, caption_text, width_inches=6.0):
        img_path = os.path.join(figures_dir, img_filename)
        if os.path.exists(img_path):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run()
            run.add_picture(img_path, width=Inches(width_inches))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(0)
            p_cap.paragraph_format.space_after = Pt(16)
            r_c = p_cap.add_run(caption_text)
            r_c.font.name = 'Times New Roman'
            r_c.font.size = Pt(10.5)
            r_c.italic = True
            r_c.bold = True

            md_content.append(f"\n![{caption_text}]({img_path})\n*{caption_text}*\n")

    # ==========================================
    # FRONT MATTER
    # ==========================================
    add_p("A CONTRASTIVE HYBRID FEDERATED GRAPH NEURAL NETWORK ARCHITECTURE WITH LEAKAGE-CONTROLLED EVALUATION FOR IOT INTRUSION DETECTION", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=36, space_after=24, bold=True, font_size=15, color_rgb=(0x8B, 0x00, 0x00))
    add_p("Submitted by", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=12, italic=True, font_size=12)
    add_p("Student 1 Name [Register No. 1]\nStudent 2 Name [Register No. 2]\nStudent 3 Name [Register No. 3]\nStudent 4 Name [Register No. 4]", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, font_size=12, color_rgb=(0x8B, 0x00, 0x00))
    add_p("Under the guidance of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=6, italic=True, font_size=12)
    add_p("Guide Name, Ph.D.\nDesignation, School of Computing", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, font_size=12, color_rgb=(0x8B, 0x00, 0x00))
    add_p("in partial fulfilment of the requirements for the degree of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=12, italic=True, font_size=12)
    add_p("BACHELOR OF TECHNOLOGY\nIN\nCOMPUTER SCIENCE AND ENGINEERING / COMPUTER SCIENCE AND ENGINEERING - ARTIFICIAL INTELLIGENCE", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, font_size=12.5, color_rgb=(0x1A, 0x1A, 0x1A))
    add_p("SCHOOL OF COMPUTING\nAMRITA VISHWA VIDYAPEETHAM\nAMARAVATI – 522503\nOCTOBER- 2026", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=0, bold=True, font_size=13, color_rgb=(0x8B, 0x00, 0x00))

    # Certificate
    doc.add_page_break()
    add_p("AMRITA VISHWA VIDYAPEETHAM\nSCHOOL OF COMPUTING, AMARAVATI – 522503", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    add_p("CERTIFICATE", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=24, bold=True, font_size=14)
    cert_text = (
        "This is to certify that the project report entitled \"A Contrastive Hybrid Federated Graph Neural Network "
        "Architecture with Leakage-Controlled Evaluation for IoT Intrusion Detection\" submitted by Student 1 Name (Roll No. 1), "
        "Student 2 Name (Roll No. 2), Student 3 Name (Roll No. 3), and Student 4 Name (Roll No. 4) in partial fulfillment "
        "of the requirements for the award of Degree Bachelor of Technology in Computer Science and Engineering / "
        "Computer Science and Engineering-Artificial Intelligence is a bonafide record of the research and development work "
        "carried out under our guidance and supervision at School of Computing, Amrita Vishwa Vidyapeetham, Amaravati Campus."
    )
    add_p(cert_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=36, line_spacing=1.5, font_size=12)

    sig_table = doc.add_table(rows=2, cols=2)
    sig_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_guide = sig_table.cell(0, 0)
    cell_chair = sig_table.cell(0, 1)
    p_g = cell_guide.paragraphs[0]
    p_g.paragraph_format.line_spacing = 1.3
    r = p_g.add_run("Guide Name, Ph.D.\nB.Tech. Project Guide\nDesignation, School of Computing\nAmrita Vishwa Vidyapeetham")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)
    p_c = cell_chair.paragraphs[0]
    p_c.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_c.paragraph_format.line_spacing = 1.3
    r = p_c.add_run("Dr. M. Nageswara Rao\nChairperson\nSchool of Computing\nAmrita Vishwa Vidyapeetham")
    r.font.name = 'Times New Roman'
    r.font.size = Pt(11)

    add_p("\nProject Review Panel:", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=24, space_after=12, bold=True, font_size=12)
    add_p("1. Name / Designation: _______________________________   Signature: ______________   Date: ________\n"
          "2. Name / Designation: _______________________________   Signature: ______________   Date: ________\n"
          "3. Name / Designation: _______________________________   Signature: ______________   Date: ________\n"
          "4. Name / Designation: _______________________________   Signature: ______________   Date: ________", 
          align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=12, font_size=11, line_spacing=1.5)

    # Abstract
    doc.add_page_break()
    add_p("ABSTRACT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=24, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    abstract_text = (
        "Decentralized Internet of Things (IoT) ecosystems require robust Network Intrusion Detection Systems (NIDS) "
        "that preserve privacy while capturing complex topological attack patterns. Standard Federated Graph Neural Networks "
        "(FedGNNs) frequently exhibit catastrophic false-negative collapse on rare attack classes under empirical risk minimization. "
        "Furthermore, prevailing NIDS benchmarks suffer from pervasive socket-signature evaluation leakage. This project presents a "
        "contrastive hybrid federated GNN framework evaluated under a strict zero-leakage 8-tuple signature-grouped protocol on the "
        "official 1,377,837-record NF-ToN-IoT benchmark. Our architecture integrates three domain-specialized Graph Attention Network "
        "(GAT) clients (Temporal, Content, and Behavioral), Leiden community partitioning, and a server-side GraphSAGE overlay. "
        "To eliminate minority collapse, we formulate a joint optimization objective uniting Class-Balanced Focal loss (beta=0.9999, "
        "gamma=2.0) with Supervised Contrastive (SupCon) metric regularization (mu=0.1, tau=0.07), supported by dynamic class-balanced "
        "sampling and intra-class convex edge interpolation. Across three independent random seeds (42, 43, 44), our proposed framework "
        "reduces the Macro False Negative Rate from 21.89 ± 2.01% to 5.72 ± 1.20%, elevating Balanced Accuracy from 78.11 ± 2.01% to "
        "94.28 ± 1.20%. Crucially, contrastive metric regularization resolves a catastrophic topological collapse wherein 99.83% of rare "
        "Backdoor intrusions were misclassified as Injection flows, rescuing Backdoor detection recall from 0.11 ± 0.08% to 99.57 ± 0.16%. "
        "Cross-dataset evaluation on NF-UNSW-NB15 across five seeds confirms the critical role of metric separation in decentralized graph learning."
    )
    add_p(abstract_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=18, line_spacing=1.5, font_size=12)
    add_p("Keywords: Federated Learning, Graph Neural Networks, IoT Intrusion Detection, Supervised Contrastive Learning, Class Imbalance, Data Leakage.", 
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=12, bold=True, font_size=11)

    # Declaration
    doc.add_page_break()
    add_p("DECLARATION", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=24, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    dec_text = (
        "We, the undersigned, solemnly declare that the project report entitled \"A Contrastive Hybrid Federated Graph "
        "Neural Network Architecture with Leakage-Controlled Evaluation for IoT Intrusion Detection\" is based on our own "
        "work carried out during the course of our study under the guidance of Guide Name, Ph.D., Designation, School of Computing, "
        "Amrita Vishwa Vidyapeetham, Amaravati. This work has not formed the basis for the award of any other degree or diploma "
        "in this or any other Institution or University. In keeping with ethical academic practice in reporting scientific information, "
        "due acknowledgement has been made wherever the findings of others have been cited."
    )
    add_p(dec_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=48, line_spacing=1.5, font_size=12)

    dec_table = doc.add_table(rows=4, cols=2)
    dec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    students = [
        ("Student Name 1 [Register No. 1]", "Signature of Student 1: ___________________"),
        ("Student Name 2 [Register No. 2]", "Signature of Student 2: ___________________"),
        ("Student Name 3 [Register No. 3]", "Signature of Student 3: ___________________"),
        ("Student Name 4 [Register No. 4]", "Signature of Student 4: ___________________")
    ]
    for row_idx, (st_name, st_sig) in enumerate(students):
        cell_l = dec_table.cell(row_idx, 0)
        cell_r = dec_table.cell(row_idx, 1)
        p1 = cell_l.paragraphs[0]
        p1.paragraph_format.line_spacing = 1.3
        p1.paragraph_format.space_after = Pt(8)
        r1 = p1.add_run(st_name)
        r1.font.name = 'Times New Roman'
        r1.font.size = Pt(11)
        r1.bold = True
        p2 = cell_r.paragraphs[0]
        p2.paragraph_format.line_spacing = 1.3
        p2.paragraph_format.space_after = Pt(8)
        r2 = p2.add_run(st_sig)
        r2.font.name = 'Times New Roman'
        r2.font.size = Pt(11)

    # Acknowledgement
    doc.add_page_break()
    add_p("ACKNOWLEDGEMENT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=24, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    ack_text_1 = (
        "We express our deep gratitude to our beloved Chancellor Sri Mata Amritanandamayi Devi AMMA "
        "for providing the bright academic climate, spiritual inspiration, and cutting-edge resources at Amrita Vishwa Vidyapeetham, "
        "which has made this entire project work possible. This acknowledgment is intended to thank all those people involved directly "
        "or indirectly with our project. We thank the Board of Management for providing us with the necessary computing "
        "infrastructure and research facilities required for the completion of this project."
    )
    add_p(ack_text_1, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=12, line_spacing=1.5, font_size=12)
    ack_text_2 = (
        "We express our heartfelt gratitude to Mr. M. S. Vijayendra, Executive Director, Amaravati Campus, Prof. C. K. Jayashankar, "
        "Associate Dean, Amaravati Campus, Prof. Shiva Pratap Gopakumar, Principal, Amaravati Campus, and Prof. M. Nageswara Rao, "
        "Chairperson, Amrita School of Computing, for their constant encouragement, administrative guidance, and scholarly support, "
        "and all the faculty members of the School of Computing for their valuable feedback throughout our B.Tech program."
    )
    add_p(ack_text_2, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=12, line_spacing=1.5, font_size=12)
    ack_text_3 = (
        "We wish to record our deep sense of gratitude and profound thanks to our project guide Guide Name, Ph.D., Designation, "
        "Amrita School of Computing, for his/her keen interest, inspiring guidance, rigorous technical critiques, and constant "
        "encouragement during all stages, to bring this research work into fruition. We also feel extremely grateful to the Project Review "
        "Panel members for their insightful feedback, methodological challenges, and constructive recommendations during project milestones."
    )
    add_p(ack_text_3, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=12, line_spacing=1.5, font_size=12)
    ack_text_4 = (
        "We would also like to thank the entire fraternity and technical staff of the School of Computing. We extend our sincere thanks "
        "to our family members and peers for their unwavering patience, motivation, and support throughout this endeavor. Last but not least, "
        "we offer our humble pranams and thank the divine supreme energy which bestowed clarity and perseverance to make our project a success."
    )
    add_p(ack_text_4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=24, line_spacing=1.5, font_size=12)
    add_p("Student Name 1\nStudent Name 2\nStudent Name 3\nStudent Name 4", 
          align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=12, space_after=0, bold=True, font_size=12, color_rgb=(0x8B, 0x00, 0x00))

    # Table of Contents
    doc.add_page_break()
    add_p("TABLE OF CONTENTS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    toc_table = doc.add_table(rows=1, cols=3)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(toc_table)
    toc_table.rows[0].cells[0].text = "CHAPTER"
    toc_table.rows[0].cells[1].text = "TITLE"
    toc_table.rows[0].cells[2].text = "PAGE NO."
    set_cell_background(toc_table.rows[0].cells[0], "EAEAEA")
    set_cell_background(toc_table.rows[0].cells[1], "EAEAEA")
    set_cell_background(toc_table.rows[0].cells[2], "EAEAEA")
    for ch, tit, pg in [
        ("", "ABSTRACT", "iii"), ("", "LIST OF TABLES", "vii"), ("", "LIST OF FIGURES", "ix"), ("", "LIST OF ABBREVIATIONS", "xi"),
        ("1", "INTRODUCTION", "1"), ("1.1", "Introduction (Background)", "1"), ("1.2", "Problem Statement", "4"),
        ("1.3", "Objectives of the Dissertation", "6"), ("1.4", "Research Contributions", "7"), ("1.5", "Organization of the Report", "9"),
        ("2", "LITERATURE SURVEY", "10"), ("2.1", "Comprehensive Survey", "10"), ("2.2", "Summary and Findings in Tabular Format", "16"),
        ("2.3", "Challenges in Graph-Based Federated Detection", "18"), ("2.4", "Motivation of the Project Work", "20"),
        ("3", "MATERIALS AND METHODS", "22"), ("3.1", "Datasets Description (NF-ToN-IoT and NF-UNSW-NB15)", "22"),
        ("3.2", "Methods of Data Processing and Pre-processing", "27"), ("3.3", "Programming Tools and Simulation Framework", "33"),
        ("4", "METHODOLOGY", "35"), ("4.1", "Design / Methodology 1 of Existing Work (Centralized & Standard FedNIDS)", "35"),
        ("4.2", "Design / Methodology 2 of Existing Work (Base FedGATSage Framework)", "38"), ("4.3", "Proposed Architecture", "41"),
        ("4.4", "Proposed Design / Detailed Methodology Formulations", "43"), ("4.5", "Proposed Complete Flowchart and Execution Algorithms", "51"),
        ("5", "RESULTS AND DISCUSSION", "55"), ("5.1", "Experimental Setup and Evaluation Protocol", "55"),
        ("5.2", "Qualitative Results (Manifold Disentanglement and Heatmaps)", "58"), ("5.3", "Quantitative Results (Multi-Seed Benchmark Verification)", "61"),
        ("5.4", "Ablation Studies and Hypothesis Testing", "66"), ("5.5", "Discussion and Limitations", "72"),
        ("6", "CONCLUSION AND FUTURE DIRECTIONS", "76"), ("6.1", "Conclusion", "76"), ("6.2", "Future Directions", "78"),
        ("", "REFERENCES", "81"), ("", "LIST OF PUBLICATIONS", "88"), ("", "PLAGIARISM AND AI COMPLIANCE REPORT", "89")
    ]:
        row = toc_table.add_row()
        row.cells[0].text = ch
        row.cells[1].text = tit
        row.cells[2].text = pg
        set_cell_margins(row.cells[0], 50, 50, 70, 70)
        set_cell_margins(row.cells[1], 50, 50, 70, 70)
        set_cell_margins(row.cells[2], 50, 50, 70, 70)
        row.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if ch.isdigit() or ch == "":
            row.cells[0].paragraphs[0].runs[0].bold = True
            row.cells[1].paragraphs[0].runs[0].bold = True
            row.cells[2].paragraphs[0].runs[0].bold = True

    # List of Tables
    doc.add_page_break()
    add_p("LIST OF TABLES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    t_tab = doc.add_table(rows=1, cols=3)
    t_tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_tab)
    t_tab.rows[0].cells[0].text = "TABLE NO."
    t_tab.rows[0].cells[1].text = "TITLE"
    t_tab.rows[0].cells[2].text = "PAGE NO."
    set_cell_background(t_tab.rows[0].cells[0], "EAEAEA")
    set_cell_background(t_tab.rows[0].cells[1], "EAEAEA")
    set_cell_background(t_tab.rows[0].cells[2], "EAEAEA")
    for num, tit, pg in [
        ("Table 2.1", "Comprehensive Survey Comparison of Intrusion Detection Frameworks", "17"),
        ("Table 3.1", "NF-ToN-IoT Ground-Truth Class Distribution and Partitioning Statistics", "23"),
        ("Table 3.2", "NF-UNSW-NB15 Ground-Truth Class Distribution and Partitioning Statistics", "25"),
        ("Table 3.3", "Standard NetFlow V9 Attribute Dictionary and Structural Features", "26"),
        ("Table 3.4", "Domain-Specialized Feature Engineering Dictionary (Temporal, Content, Behavioral)", "30"),
        ("Table 3.5", "Socket Signature Leakage Audit: Random Row Split vs 8-Tuple Grouped Split", "32"),
        ("Table 5.1", "Simulation Environment Hardware and Software Parameters", "56"),
        ("Table 5.2", "Headline Empirical Results across Regularization Strengths on NF-ToN-IoT (3 Seeds)", "62"),
        ("Table 5.3", "Per-Class Detection Recall across Model Configurations on NF-ToN-IoT", "63"),
        ("Table 5.4", "Per-Class F1-Scores across Model Configurations on NF-ToN-IoT", "64"),
        ("Table 5.5", "Decomposition of Balanced Accuracy Improvement from mu=0.0 to mu=0.1", "65"),
        ("Table 5.6", "Cumulative Component Ablation Progression under Signature-Grouped Zero-Leakage Split", "67"),
        ("Table 5.7", "Node-Averaging Mechanism Test: Validating Host Dilution vs Edge Representation", "68"),
        ("Table 5.8", "Impact of Raw Feature Inclusion on Meta-Classifier Arbitration", "70"),
        ("Table 5.9", "Cross-Dataset Multi-Seed Evaluation on NF-UNSW-NB15 across 5 Seeds", "71")
    ]:
        r = t_tab.add_row()
        r.cells[0].text = num
        r.cells[1].text = tit
        r.cells[2].text = pg
        r.cells[0].paragraphs[0].runs[0].bold = True
        r.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # List of Figures
    doc.add_page_break()
    add_p("LIST OF FIGURES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    f_tab = doc.add_table(rows=1, cols=3)
    f_tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(f_tab)
    f_tab.rows[0].cells[0].text = "FIGURE NO."
    f_tab.rows[0].cells[1].text = "TITLE"
    f_tab.rows[0].cells[2].text = "PAGE NO."
    set_cell_background(f_tab.rows[0].cells[0], "EAEAEA")
    set_cell_background(f_tab.rows[0].cells[1], "EAEAEA")
    set_cell_background(f_tab.rows[0].cells[2], "EAEAEA")
    for num, tit, pg in [
        ("Figure 4.1", "Proposed Contrastive Hybrid Federated GNN System Architecture Workflow", "42"),
        ("Figure 4.2", "Complete Procedural Flowchart of Client-Server Federated Cycle and Meta-Learner", "53"),
        ("Figure 5.1", "Confusion Matrix Heatmaps on NF-ToN-IoT: Anchor (Plain CE) vs Proposed Framework (mu=0.1)", "60"),
        ("Figure 5.2", "Per-Class Detection Recall and Balanced Accuracy as a Function of Contrastive Strength mu", "69")
    ]:
        r = f_tab.add_row()
        r.cells[0].text = num
        r.cells[1].text = tit
        r.cells[2].text = pg
        r.cells[0].paragraphs[0].runs[0].bold = True
        r.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # List of Abbreviations
    doc.add_page_break()
    add_p("LIST OF ABBREVIATIONS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    a_tab = doc.add_table(rows=1, cols=2)
    a_tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(a_tab)
    a_tab.rows[0].cells[0].text = "ABBREVIATION"
    a_tab.rows[0].cells[1].text = "EXPANSION"
    set_cell_background(a_tab.rows[0].cells[0], "EAEAEA")
    set_cell_background(a_tab.rows[0].cells[1], "EAEAEA")
    for abb, exp in [
        ("NIDS", "Network Intrusion Detection System"), ("IoT", "Internet of Things"), ("IIoT", "Industrial Internet of Things"),
        ("SCADA", "Supervisory Control and Data Acquisition"), ("FL", "Federated Learning"), ("FedAvg", "Federated Averaging Algorithm"),
        ("GNN", "Graph Neural Network"), ("GCN", "Graph Convolutional Network"), ("GAT", "Graph Attention Network"),
        ("GraphSAGE", "Sample and Aggregate Graph Convolutional Network"), ("SupCon", "Supervised Contrastive Learning"),
        ("CB-Focal", "Class-Balanced Focal Loss"), ("CPM", "Constant Potts Model"), ("FNR", "False Negative Rate"),
        ("FPR", "False Positive Rate"), ("BalAcc", "Balanced Accuracy"), ("MLP", "Multi-Layer Perceptron"),
        ("RF", "Random Forest Classifier"), ("RFC", "Request for Comments (IETF Technical Standard)"),
        ("TCP", "Transmission Control Protocol"), ("UDP", "User Datagram Protocol"), ("IP", "Internet Protocol"),
        ("DDoS", "Distributed Denial of Service"), ("DoS", "Denial of Service"), ("XSS", "Cross-Site Scripting"),
        ("C2", "Command and Control Infrastructure"), ("Non-IID", "Non-Independent and Identically Distributed Data"),
        ("SOC", "Security Operations Center"), ("PCAP", "Packet Capture"), ("ADFA", "Australian Defence Force Academy"),
        ("DP", "Differential Privacy")
    ]:
        r = a_tab.add_row()
        r.cells[0].text = abb
        r.cells[1].text = exp
        r.cells[0].paragraphs[0].runs[0].bold = True

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_chapter_heading(1, text_ch1.CHAPTER_1_TITLE)
    add_sec_heading(text_ch1.SEC_1_1_TITLE)
    for p_text in text_ch1.SEC_1_1_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch1.SEC_1_2_TITLE)
    for p_text in text_ch1.SEC_1_2_PARAS:
        add_smart_paragraph(p_text)
    for b_title, b_desc in text_ch1.SEC_1_2_BULLETS:
        add_bullet_item(b_title, b_desc)

    add_sec_heading(text_ch1.SEC_1_3_TITLE)
    for p_text in text_ch1.SEC_1_3_PARAS:
        add_smart_paragraph(p_text)
    for o_title, o_desc in text_ch1.SEC_1_3_OBJS:
        add_bullet_item(o_title, o_desc)

    add_sec_heading(text_ch1.SEC_1_4_TITLE)
    for p_text in text_ch1.SEC_1_4_PARAS:
        add_smart_paragraph(p_text)
    for c_title, c_desc in text_ch1.SEC_1_4_CONTRIBS:
        add_bullet_item(c_title, c_desc)

    add_sec_heading(text_ch1.SEC_1_5_TITLE)
    for p_text in text_ch1.SEC_1_5_PARAS:
        add_smart_paragraph(p_text)

    # ==========================================
    # CHAPTER 2: LITERATURE SURVEY
    # ==========================================
    add_chapter_heading(2, text_ch2.CHAPTER_2_TITLE)
    add_sec_heading(text_ch2.SEC_2_1_TITLE)
    for p_text in text_ch2.SEC_2_1_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch2.SUBSEC_2_1_1_TITLE)
    for p_text in text_ch2.SUBSEC_2_1_1_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch2.SUBSEC_2_1_2_TITLE)
    for p_text in text_ch2.SUBSEC_2_1_2_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch2.SUBSEC_2_1_3_TITLE)
    for p_text in text_ch2.SUBSEC_2_1_3_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch2.SUBSEC_2_1_4_TITLE)
    for p_text in text_ch2.SUBSEC_2_1_4_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch2.SUBSEC_2_1_5_TITLE)
    for p_text in text_ch2.SUBSEC_2_1_5_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch2.SUBSEC_2_1_6_TITLE)
    for p_text in text_ch2.SUBSEC_2_1_6_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch2.SEC_2_2_TITLE)
    for p_text in text_ch2.SEC_2_2_PARAS:
        add_smart_paragraph(p_text)

    # Table 2.1
    t21 = doc.add_table(rows=1, cols=5)
    t21.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t21)
    for idx, h in enumerate(["Author & Year", "Methodology / Architecture", "Dataset Used", "Primary Findings", "Identified Critical Limitations"]):
        t21.rows[0].cells[idx].text = h
        set_cell_background(t21.rows[0].cells[idx], "EAEAEA")
        t21.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t21.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t21.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.5)
    for row_d in text_ch2.LIT_TABLE_ROWS:
        r = t21.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 40, 40, 50, 50)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.2
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(9.0)
                if c_idx == 0:
                    run_i.bold = True
    add_p("Table 2.1: Comprehensive Survey Comparison of Intrusion Detection Frameworks.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_sec_heading(text_ch2.SEC_2_3_TITLE)
    for p_text in text_ch2.SEC_2_3_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch2.SEC_2_4_TITLE)
    for p_text in text_ch2.SEC_2_4_PARAS:
        add_smart_paragraph(p_text)

    # ==========================================
    # CHAPTER 3: MATERIALS AND METHODS
    # ==========================================
    add_chapter_heading(3, text_ch3.CHAPTER_3_TITLE)
    add_sec_heading(text_ch3.SEC_3_1_TITLE)
    for p_text in text_ch3.SEC_3_1_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch3.SUBSEC_3_1_1_TITLE)
    for p_text in text_ch3.SUBSEC_3_1_1_PARAS:
        add_smart_paragraph(p_text)

    # Table 3.1
    t31 = doc.add_table(rows=1, cols=5)
    t31.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t31)
    for idx, h in enumerate(["Class Name", "Raw Flow Count", "Proportion (%)", "Train Support (80%)", "Test Support (20%)"]):
        t31.rows[0].cells[idx].text = h
        set_cell_background(t31.rows[0].cells[idx], "EAEAEA")
        t31.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t31.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t31.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.5)
    for row_d in text_ch3.TABLE_3_1_ROWS:
        r = t31.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 40, 40, 50, 50)
            p = c.paragraphs[0]
            if c_idx >= 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(9.0)
                if "Total" in row_d[0]:
                    run_i.bold = True
    add_p("Table 3.1: NF-ToN-IoT Ground-Truth Class Distribution and Partitioning Statistics.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_subsec_heading(text_ch3.SUBSEC_3_1_2_TITLE)
    for p_text in text_ch3.SUBSEC_3_1_2_PARAS:
        add_smart_paragraph(p_text)

    # Table 3.2
    t32 = doc.add_table(rows=1, cols=5)
    t32.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t32)
    for idx, h in enumerate(["Class Name", "Raw Flow Count", "Proportion (%)", "Train Support (80%)", "Test Support (20%)"]):
        t32.rows[0].cells[idx].text = h
        set_cell_background(t32.rows[0].cells[idx], "EAEAEA")
        t32.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t32.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t32.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.5)
    for row_d in text_ch3.TABLE_3_2_ROWS:
        r = t32.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 40, 40, 50, 50)
            p = c.paragraphs[0]
            if c_idx >= 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(9.0)
                if "Total" in row_d[0]:
                    run_i.bold = True
    add_p("Table 3.2: NF-UNSW-NB15 Ground-Truth Class Distribution and Partitioning Statistics.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_subsec_heading(text_ch3.SUBSEC_3_1_3_TITLE)
    for p_text in text_ch3.SUBSEC_3_1_3_PARAS:
        add_smart_paragraph(p_text)

    # Table 3.3
    t33 = doc.add_table(rows=1, cols=4)
    t33.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t33)
    for idx, h in enumerate(["Attribute Name", "Data Type", "Network Telemetry Description", "Pipeline Role"]):
        t33.rows[0].cells[idx].text = h
        set_cell_background(t33.rows[0].cells[idx], "EAEAEA")
        t33.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t33.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t33.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.5)
    for row_d in text_ch3.TABLE_3_3_ROWS:
        r = t33.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 40, 40, 50, 50)
            p = c.paragraphs[0]
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(9.0)
                if c_idx == 0:
                    run_i.bold = True
    add_p("Table 3.3: Standard NetFlow V9 Attribute Dictionary and Structural Features.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_sec_heading(text_ch3.SEC_3_2_TITLE)
    for p_text in text_ch3.SEC_3_2_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch3.SUBSEC_3_2_1_TITLE)
    for p_text in text_ch3.SUBSEC_3_2_1_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch3.SUBSEC_3_2_2_TITLE)
    for p_text in text_ch3.SUBSEC_3_2_2_PARAS:
        add_smart_paragraph(p_text)

    # Table 3.4
    t34 = doc.add_table(rows=1, cols=3)
    t34.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t34)
    for idx, h in enumerate(["Specialized Feature Sub-Set", "Engineered Feature Attributes", "Targeted Threat Category"]):
        t34.rows[0].cells[idx].text = h
        set_cell_background(t34.rows[0].cells[idx], "EAEAEA")
        t34.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t34.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t34.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.5)
    for row_d in text_ch3.TABLE_3_4_ROWS:
        r = t34.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 40, 40, 50, 50)
            p = c.paragraphs[0]
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(9.0)
                if c_idx == 0:
                    run_i.bold = True
    add_p("Table 3.4: Domain-Specialized Feature Engineering Dictionary (Temporal, Content, Behavioral).", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_subsec_heading(text_ch3.SUBSEC_3_2_3_TITLE)
    for p_text in text_ch3.SUBSEC_3_2_3_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch3.SUBSEC_3_2_4_TITLE)
    for p_text in text_ch3.SUBSEC_3_2_4_PARAS:
        add_smart_paragraph(p_text)

    # Table 3.5
    t35 = doc.add_table(rows=1, cols=5)
    t35.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t35)
    for idx, h in enumerate(["Data Partitioning Protocol", "Train Flows (80%)", "Test Flows (20%)", "Identified Socket Signature Leakage", "Evaluation Integrity Status"]):
        t35.rows[0].cells[idx].text = h
        set_cell_background(t35.rows[0].cells[idx], "EAEAEA")
        t35.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t35.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t35.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.5)
    for row_d in text_ch3.TABLE_3_5_ROWS:
        r = t35.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 40, 40, 50, 50)
            p = c.paragraphs[0]
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(9.0)
                if c_idx == 0:
                    run_i.bold = True
    add_p("Table 3.5: Socket Signature Leakage Audit: Random Row Split vs 8-Tuple Grouped Split.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_subsec_heading(text_ch3.SUBSEC_3_2_5_TITLE)
    for p_text in text_ch3.SUBSEC_3_2_5_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch3.SEC_3_3_TITLE)
    for p_text in text_ch3.SEC_3_3_PARAS:
        add_smart_paragraph(p_text)

    # ==========================================
    # CHAPTER 4: METHODOLOGY
    # ==========================================
    add_chapter_heading(4, text_ch4.CHAPTER_4_TITLE)
    add_sec_heading(text_ch4.SEC_4_1_TITLE)
    for p_text in text_ch4.SEC_4_1_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch4.SEC_4_2_TITLE)
    for p_text in text_ch4.SEC_4_2_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch4.SEC_4_3_TITLE)
    for p_text in text_ch4.SEC_4_3_PARAS:
        add_smart_paragraph(p_text)

    # Figure 4.1
    add_image_figure("fig1_architecture.png", "Figure 4.1: Proposed Contrastive Hybrid Federated GNN System Architecture Workflow.", width_inches=6.2)

    add_sec_heading(text_ch4.SEC_4_4_TITLE)
    for p_text in text_ch4.SEC_4_4_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch4.SUBSEC_4_4_1_TITLE)
    for p_text in text_ch4.SUBSEC_4_4_1_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch4.SUBSEC_4_4_2_TITLE)
    for p_text in text_ch4.SUBSEC_4_4_2_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch4.SUBSEC_4_4_3_TITLE)
    for p_text in text_ch4.SUBSEC_4_4_3_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch4.SUBSEC_4_4_4_TITLE)
    for p_text in text_ch4.SUBSEC_4_4_4_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch4.SUBSEC_4_4_5_TITLE)
    for p_text in text_ch4.SUBSEC_4_4_5_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch4.SUBSEC_4_4_6_TITLE)
    for p_text in text_ch4.SUBSEC_4_4_6_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch4.SEC_4_5_TITLE)
    for p_text in text_ch4.SEC_4_5_PARAS:
        add_smart_paragraph(p_text)

    # Algorithmic boxes
    add_p("ALGORITHM 4.1: CONTRASTIVE HYBRID FEDERATED GNN PIPELINE", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, bold=True, font_size=11, color_rgb=(0x20, 0x30, 0x50))
    add_p(text_ch4.ALGO_4_1_TEXT, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=12, line_spacing=1.3, font_size=10.5)

    add_p("ALGORITHM 4.2: DYNAMIC CLASS-BALANCED SAMPLING & SUPCON EVALUATION", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=8, space_after=4, bold=True, font_size=11, color_rgb=(0x20, 0x30, 0x50))
    add_p(text_ch4.ALGO_4_2_TEXT, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=12, line_spacing=1.3, font_size=10.5)

    # Figure 4.2
    add_image_figure("fig1_architecture.png", "Figure 4.2: Complete Procedural Flowchart of Client-Server Federated Cycle and Meta-Learner.", width_inches=6.0)

    # ==========================================
    # CHAPTER 5: RESULTS AND DISCUSSION
    # ==========================================
    add_chapter_heading(5, text_ch5.CHAPTER_5_TITLE)
    add_sec_heading(text_ch5.SEC_5_1_TITLE)
    for p_text in text_ch5.SEC_5_1_PARAS:
        add_smart_paragraph(p_text)

    # Table 5.1
    t51 = doc.add_table(rows=1, cols=2)
    t51.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t51)
    t51.rows[0].cells[0].text = "SYSTEM PARAMETER"
    t51.rows[0].cells[1].text = "CONFIGURATION VALUE"
    set_cell_background(t51.rows[0].cells[0], "EAEAEA")
    set_cell_background(t51.rows[0].cells[1], "EAEAEA")
    t51.rows[0].cells[0].paragraphs[0].runs[0].bold = True
    t51.rows[0].cells[1].paragraphs[0].runs[0].bold = True
    for p_name, p_val in text_ch5.TABLE_5_1_ROWS:
        r = t51.add_row()
        r.cells[0].text = p_name
        r.cells[1].text = p_val
        r.cells[0].paragraphs[0].runs[0].bold = True
        set_cell_margins(r.cells[0], 40, 40, 50, 50)
        set_cell_margins(r.cells[1], 40, 40, 50, 50)
    add_p("Table 5.1: Simulation Environment Hardware and Software Parameters.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_sec_heading(text_ch5.SEC_5_2_TITLE)
    for p_text in text_ch5.SEC_5_2_PARAS:
        add_smart_paragraph(p_text)

    # Figure 5.1
    add_image_figure("fig2_confusion_matrices.png", "Figure 5.1: Confusion Matrix Heatmaps on NF-ToN-IoT: Anchor (Plain CE) vs Proposed Framework (mu=0.1).", width_inches=6.2)

    add_sec_heading(text_ch5.SEC_5_3_TITLE)
    for p_text in text_ch5.SEC_5_3_PARAS:
        add_smart_paragraph(p_text)

    # Table 5.2
    t52 = doc.add_table(rows=1, cols=8)
    t52.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t52)
    for idx, h in enumerate(["Model Configuration", "Accuracy (%)", "BalAcc (%)", "Macro F1 (%)", "Macro FNR (%)", "Backdoor Rec", "Scanning Rec", "Password Rec"]):
        t52.rows[0].cells[idx].text = h
        set_cell_background(t52.rows[0].cells[idx], "EAEAEA")
        t52.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t52.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t52.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(8.5)
    for row_d in text_ch5.TABLE_5_2_ROWS:
        r = t52.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 35, 35, 40, 40)
            p = c.paragraphs[0]
            if c_idx >= 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(8.5)
                if "Proposed" in row_d[0]:
                    run_i.bold = True
    add_p("Table 5.2: Headline Empirical Results across Regularization Strengths on NF-ToN-IoT (3 Seeds).", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    # Table 5.3
    t53 = doc.add_table(rows=1, cols=6)
    t53.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t53)
    for idx, h in enumerate(["Class Name", "GNN Anchor Rec", "mu = 0.0 Rec", "mu = 0.1 Rec", "mu = 0.3 Rec", "mu = 0.5 Rec"]):
        t53.rows[0].cells[idx].text = h
        set_cell_background(t53.rows[0].cells[idx], "EAEAEA")
        t53.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t53.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t53.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.0)
    for row_d in text_ch5.TABLE_5_3_ROWS:
        r = t53.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 35, 35, 45, 45)
            p = c.paragraphs[0]
            if c_idx >= 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(8.5)
                if row_d[0] == "Backdoor":
                    run_i.bold = True
    add_p("Table 5.3: Per-Class Detection Recall across Model Configurations on NF-ToN-IoT.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    # Table 5.4
    t54 = doc.add_table(rows=1, cols=6)
    t54.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t54)
    for idx, h in enumerate(["Class Name", "GNN Anchor F1", "mu = 0.0 F1", "mu = 0.1 F1", "mu = 0.3 F1", "mu = 0.5 F1"]):
        t54.rows[0].cells[idx].text = h
        set_cell_background(t54.rows[0].cells[idx], "EAEAEA")
        t54.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t54.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t54.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(9.0)
    for row_d in text_ch5.TABLE_5_4_ROWS:
        r = t54.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 35, 35, 45, 45)
            p = c.paragraphs[0]
            if c_idx >= 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(8.5)
                if row_d[0] == "Backdoor":
                    run_i.bold = True
    add_p("Table 5.4: Per-Class F1-Scores across Model Configurations on NF-ToN-IoT.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_subsec_heading(text_ch5.SUBSEC_5_3_1_TITLE)
    for p_text in text_ch5.SUBSEC_5_3_1_PARAS:
        add_smart_paragraph(p_text)

    # Table 5.5
    t55 = doc.add_table(rows=1, cols=6)
    t55.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t55)
    for idx, h in enumerate(["Class Name", "mu = 0.0 Recall", "mu = 0.1 Recall", "Recall Gain", "BalAcc Gain Contribution", "% of Total BalAcc Gain"]):
        t55.rows[0].cells[idx].text = h
        set_cell_background(t55.rows[0].cells[idx], "EAEAEA")
        t55.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t55.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t55.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(8.5)
    for row_d in text_ch5.TABLE_5_5_ROWS:
        r = t55.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 35, 35, 40, 40)
            p = c.paragraphs[0]
            if c_idx >= 1:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(8.5)
                if row_d[0] == "Backdoor" or "Total" in row_d[0]:
                    run_i.bold = True
    add_p("Table 5.5: Decomposition of Balanced Accuracy Improvement from mu=0.0 to mu=0.1.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_sec_heading(text_ch5.SEC_5_4_TITLE)
    for p_text in text_ch5.SEC_5_4_PARAS:
        add_smart_paragraph(p_text)

    add_subsec_heading(text_ch5.SUBSEC_5_4_1_TITLE)
    for p_text in text_ch5.SUBSEC_5_4_1_PARAS:
        add_smart_paragraph(p_text)

    # Table 5.6
    t56 = doc.add_table(rows=1, cols=7)
    t56.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t56)
    for idx, h in enumerate(["Ablation Step", "Accuracy (%)", "BalAcc (%)", "Macro F1 (%)", "Macro FNR (%)", "Backdoor Rec", "Architectural Finding"]):
        t56.rows[0].cells[idx].text = h
        set_cell_background(t56.rows[0].cells[idx], "EAEAEA")
        t56.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t56.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t56.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(8.5)
    for row_d in text_ch5.TABLE_5_6_ROWS:
        r = t56.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 35, 35, 40, 40)
            p = c.paragraphs[0]
            if 1 <= c_idx <= 5:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(8.5)
                if "(d)" in row_d[0]:
                    run_i.bold = True
    add_p("Table 5.6: Cumulative Component Ablation Progression under Signature-Grouped Zero-Leakage Split.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_subsec_heading(text_ch5.SUBSEC_5_4_2_TITLE)
    for p_text in text_ch5.SUBSEC_5_4_2_PARAS:
        add_smart_paragraph(p_text)

    # Table 5.7
    t57 = doc.add_table(rows=1, cols=7)
    t57.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t57)
    for idx, h in enumerate(["Configuration", "GNN Aggregation", "BalAcc (%)", "Macro F1 (%)", "Backdoor Rec", "Scanning Rec", "Password Rec"]):
        t57.rows[0].cells[idx].text = h
        set_cell_background(t57.rows[0].cells[idx], "EAEAEA")
        t57.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t57.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t57.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(8.5)
    for row_d in text_ch5.TABLE_5_7_ROWS:
        r = t57.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 35, 35, 40, 40)
            p = c.paragraphs[0]
            if c_idx >= 2:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(8.5)
                if "Proposed" in row_d[0] or "Edge-Only Anchor" in row_d[0]:
                    run_i.bold = True
    add_p("Table 5.7: Node-Averaging Mechanism Test: Validating Host Dilution vs Edge Representation.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_subsec_heading(text_ch5.SUBSEC_5_4_3_TITLE)
    for p_text in text_ch5.SUBSEC_5_4_3_PARAS:
        add_smart_paragraph(p_text)

    # Figure 5.2
    add_image_figure("fig3_per_class_recalls.png", "Figure 5.2: Per-Class Detection Recall and Balanced Accuracy as a Function of Contrastive Strength mu.", width_inches=6.0)

    add_subsec_heading(text_ch5.SUBSEC_5_4_4_TITLE)
    for p_text in text_ch5.SUBSEC_5_4_4_PARAS:
        add_smart_paragraph(p_text)

    # Table 5.9
    t59 = doc.add_table(rows=1, cols=7)
    t59.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t59)
    for idx, h in enumerate(["Configuration", "Evaluated Seeds", "BalAcc (%)", "Macro F1 (%)", "Macro FNR (%)", "Collapsed Seeds", "Backdoor Rec (%)"]):
        t59.rows[0].cells[idx].text = h
        set_cell_background(t59.rows[0].cells[idx], "EAEAEA")
        t59.rows[0].cells[idx].paragraphs[0].runs[0].bold = True
        t59.rows[0].cells[idx].paragraphs[0].runs[0].font.name = 'Times New Roman'
        t59.rows[0].cells[idx].paragraphs[0].runs[0].font.size = Pt(8.5)
    for row_d in text_ch5.TABLE_5_9_ROWS:
        r = t59.add_row()
        for c_idx, val in enumerate(row_d):
            c = r.cells[c_idx]
            c.text = val
            set_cell_margins(c, 35, 35, 40, 40)
            p = c.paragraphs[0]
            if 2 <= c_idx <= 4 or c_idx == 6:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for run_i in p.runs:
                run_i.font.name = 'Times New Roman'
                run_i.font.size = Pt(8.5)
    add_p("Table 5.9: Cross-Dataset Multi-Seed Evaluation on NF-UNSW-NB15 across 5 Seeds.", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=12, italic=True, bold=True, font_size=10.5)

    add_sec_heading(text_ch5.SEC_5_5_TITLE)
    for p_text in text_ch5.SEC_5_5_PARAS:
        add_smart_paragraph(p_text)

    # ==========================================
    # CHAPTER 6: CONCLUSION AND FUTURE DIRECTIONS
    # ==========================================
    add_chapter_heading(6, text_ch6.CHAPTER_6_TITLE)
    add_sec_heading(text_ch6.SEC_6_1_TITLE)
    for p_text in text_ch6.SEC_6_1_PARAS:
        add_smart_paragraph(p_text)

    add_sec_heading(text_ch6.SEC_6_2_TITLE)
    for p_text in text_ch6.SEC_6_2_PARAS:
        add_smart_paragraph(p_text)
    for b_title, b_desc in text_ch6.FUTURE_DIRECTIONS_BULLETS:
        add_bullet_item(b_title, b_desc)

    # References
    doc.add_page_break()
    add_p("REFERENCES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=24, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    md_content.append("\n\n# REFERENCES\n")
    for ref_str in text_ch6.REFERENCES_LIST:
        add_p(ref_str, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6, line_spacing=1.3, font_size=10.5)
        md_content.append(ref_str + "\n")

    # List of Publications
    doc.add_page_break()
    add_p("LIST OF PUBLICATIONS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=24, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    md_content.append("\n\n# LIST OF PUBLICATIONS\n")
    add_p(text_ch6.PUBLICATIONS_TEXT, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=18, line_spacing=1.5, font_size=11.5)
    md_content.append(text_ch6.PUBLICATIONS_TEXT + "\n")

    # Plagiarism Report
    doc.add_page_break()
    add_p("PLAGIARISM AND AI INTEGRITY COMPLIANCE REPORT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=24, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    md_content.append("\n\n# PLAGIARISM AND AI INTEGRITY COMPLIANCE REPORT\n")
    plag_table = doc.add_table(rows=1, cols=3)
    plag_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(plag_table)
    plag_table.rows[0].cells[0].text = "METRIC EVALUATED"
    plag_table.rows[0].cells[1].text = "MEASURED SCORE"
    plag_table.rows[0].cells[2].text = "INSTITUTIONAL THRESHOLD / STATUS"
    set_cell_background(plag_table.rows[0].cells[0], "EAEAEA")
    set_cell_background(plag_table.rows[0].cells[1], "EAEAEA")
    set_cell_background(plag_table.rows[0].cells[2], "EAEAEA")
    plag_table.rows[0].cells[0].paragraphs[0].runs[0].bold = True
    plag_table.rows[0].cells[1].paragraphs[0].runs[0].bold = True
    plag_table.rows[0].cells[2].paragraphs[0].runs[0].bold = True
    for m_name, m_score, m_stat in text_ch6.PLAGIARISM_REPORT_ROWS:
        row = plag_table.add_row()
        row.cells[0].text = m_name
        row.cells[1].text = m_score
        row.cells[2].text = m_stat
        row.cells[0].paragraphs[0].runs[0].bold = True
        row.cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row.cells[1].paragraphs[0].runs[0].bold = True
        set_cell_margins(row.cells[0], 45, 45, 60, 60)
        set_cell_margins(row.cells[1], 45, 45, 60, 60)
        set_cell_margins(row.cells[2], 45, 45, 60, 60)

    add_p(text_ch6.PLAGIARISM_CERT_TEXT, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=18, line_spacing=1.5, font_size=11.5)
    md_content.append(text_ch6.PLAGIARISM_CERT_TEXT + "\n")

    # Save Word document
    doc.save(output_docx_path)
    print(f"Successfully generated DOCX report at: {output_docx_path}")

    # Save Markdown document
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content))
    print(f"Successfully generated Markdown report at: {output_md_path}")

if __name__ == '__main__':
    out_docx = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\PROJECT_REPORT_FED_GNN.docx"
    out_md = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\PROJECT_REPORT_FED_GNN.md"
    fig_dir = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\papers\paper_latex\figures"
    build_dissertation(out_docx, out_md, fig_dir)
