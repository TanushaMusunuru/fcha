import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
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

def build_extended_report(output_docx_path, output_md_path, figures_dir):
    doc = docx.Document()
    md_content = []

    # Configure Margins: 1.0 inch top/bottom/left/right (Amrita Standard)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.different_first_page_header_footer = True

    # Styling defaults
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
        run.font.color.rgb = RGBColor(0x8B, 0x00, 0x00) # Deep Crimson Accent

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(20)
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

    def add_subsubsec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(0x40, 0x50, 0x70)

        md_content.append(f"\n#### {title}\n")

    def add_text_paragraph(text):
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
    # 1. TITLE PAGE
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

    # ==========================================
    # 2. CERTIFICATE
    # ==========================================
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

    # ==========================================
    # 3. ABSTRACT
    # ==========================================
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

    # ==========================================
    # 4. DECLARATION
    # ==========================================
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

    # ==========================================
    # 5. ACKNOWLEDGEMENT
    # ==========================================
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

    # ==========================================
    # 6. TABLE OF CONTENTS
    # ==========================================
    doc.add_page_break()
    add_p("TABLE OF CONTENTS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    
    toc_table = doc.add_table(rows=1, cols=3)
    toc_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(toc_table)
    hdr_cells = toc_table.rows[0].cells
    hdr_cells[0].text = "CHAPTER"
    hdr_cells[1].text = "TITLE"
    hdr_cells[2].text = "PAGE NO."
    for cell in hdr_cells:
        set_cell_background(cell, "EAEAEA")
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(11)

    toc_entries = [
        ("", "ABSTRACT", "iii"),
        ("", "LIST OF TABLES", "vii"),
        ("", "LIST OF FIGURES", "ix"),
        ("", "LIST OF ABBREVIATIONS", "xi"),
        ("1", "INTRODUCTION", "1"),
        ("1.1", "Introduction (Background)", "1"),
        ("1.2", "Problem Statement", "4"),
        ("1.3", "Objectives", "6"),
        ("1.4", "Contributions", "7"),
        ("1.5", "Organization of the Report", "9"),
        ("2", "LITERATURE SURVEY", "10"),
        ("2.1", "Comprehensive Survey", "10"),
        ("2.2", "Summary and Findings of Survey in Tabular Format", "16"),
        ("2.3", "Challenges in Graph-Based Federated Detection", "18"),
        ("2.4", "Motivation of the Project Work", "20"),
        ("3", "MATERIALS AND METHODS", "22"),
        ("3.1", "Datasets Description (NF-ToN-IoT and NF-UNSW-NB15)", "22"),
        ("3.2", "Methods of Data Processing and Pre-processing", "27"),
        ("3.3", "Programming Tools and Simulation Framework", "33"),
        ("4", "METHODOLOGY", "35"),
        ("4.1", "Design / Methodology 1 of Existing Work (Centralized & Standard FedNIDS)", "35"),
        ("4.2", "Design / Methodology 2 of Existing Work (Base FedGATSage Framework)", "38"),
        ("4.3", "Proposed Architecture", "41"),
        ("4.4", "Proposed Design / Detailed Methodology Formulations", "43"),
        ("4.5", "Proposed Complete Flowchart and Execution Algorithms", "51"),
        ("5", "RESULTS AND DISCUSSION", "55"),
        ("5.1", "Experimental Setup and Evaluation Protocol", "55"),
        ("5.2", "Qualitative Results (Manifold Disentanglement and Heatmaps)", "58"),
        ("5.3", "Quantitative Results (Multi-Seed Benchmark Verification)", "61"),
        ("5.4", "Ablation Studies and Hypothesis Testing", "66"),
        ("5.5", "Discussion and Limitations", "72"),
        ("6", "CONCLUSION AND FUTURE DIRECTIONS", "76"),
        ("6.1", "Conclusion", "76"),
        ("6.2", "Future Directions", "78"),
        ("", "REFERENCES", "81"),
        ("", "LIST OF PUBLICATIONS", "88"),
        ("", "PLAGIARISM AND AI COMPLIANCE REPORT", "89")
    ]

    for ch, tit, pg in toc_entries:
        row = toc_table.add_row()
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.text = ch
        c1.text = tit
        c2.text = pg
        set_cell_margins(c0, 50, 50, 80, 80)
        set_cell_margins(c1, 50, 50, 80, 80)
        set_cell_margins(c2, 50, 50, 80, 80)
        c0.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if ch.isdigit() or ch == "":
            c0.paragraphs[0].runs[0].bold = True
            c1.paragraphs[0].runs[0].bold = True
            c2.paragraphs[0].runs[0].bold = True

    # ==========================================
    # 7. LIST OF TABLES
    # ==========================================
    doc.add_page_break()
    add_p("LIST OF TABLES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    tables_list = [
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
    ]
    t_tab = doc.add_table(rows=1, cols=3)
    t_tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_tab)
    t_tab.rows[0].cells[0].text = "TABLE NO."
    t_tab.rows[0].cells[1].text = "TITLE"
    t_tab.rows[0].cells[2].text = "PAGE NO."
    set_cell_background(t_tab.rows[0].cells[0], "EAEAEA")
    set_cell_background(t_tab.rows[0].cells[1], "EAEAEA")
    set_cell_background(t_tab.rows[0].cells[2], "EAEAEA")
    for num, tit, pg in tables_list:
        r = t_tab.add_row()
        r.cells[0].text = num
        r.cells[1].text = tit
        r.cells[2].text = pg
        r.cells[0].paragraphs[0].runs[0].bold = True
        r.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # ==========================================
    # 8. LIST OF FIGURES
    # ==========================================
    doc.add_page_break()
    add_p("LIST OF FIGURES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    figures_list = [
        ("Figure 4.1", "Proposed Contrastive Hybrid Federated GNN System Architecture Workflow", "42"),
        ("Figure 4.2", "Complete Procedural Flowchart of Client-Server Federated Cycle and Meta-Learner", "53"),
        ("Figure 5.1", "Confusion Matrix Heatmaps on NF-ToN-IoT: Anchor (Plain CE) vs Proposed Framework (mu=0.1)", "60"),
        ("Figure 5.2", "Per-Class Detection Recall and Balanced Accuracy as a Function of Contrastive Strength mu", "69")
    ]
    f_tab = doc.add_table(rows=1, cols=3)
    f_tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(f_tab)
    f_tab.rows[0].cells[0].text = "FIGURE NO."
    f_tab.rows[0].cells[1].text = "TITLE"
    f_tab.rows[0].cells[2].text = "PAGE NO."
    set_cell_background(f_tab.rows[0].cells[0], "EAEAEA")
    set_cell_background(f_tab.rows[0].cells[1], "EAEAEA")
    set_cell_background(f_tab.rows[0].cells[2], "EAEAEA")
    for num, tit, pg in figures_list:
        r = f_tab.add_row()
        r.cells[0].text = num
        r.cells[1].text = tit
        r.cells[2].text = pg
        r.cells[0].paragraphs[0].runs[0].bold = True
        r.cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # ==========================================
    # 9. LIST OF ABBREVIATIONS
    # ==========================================
    doc.add_page_break()
    add_p("LIST OF ABBREVIATIONS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    abbrevs = [
        ("NIDS", "Network Intrusion Detection System"),
        ("IoT", "Internet of Things"),
        ("IIoT", "Industrial Internet of Things"),
        ("SCADA", "Supervisory Control and Data Acquisition"),
        ("FL", "Federated Learning"),
        ("FedAvg", "Federated Averaging Algorithm"),
        ("GNN", "Graph Neural Network"),
        ("GCN", "Graph Convolutional Network"),
        ("GAT", "Graph Attention Network"),
        ("GraphSAGE", "Sample and Aggregate Graph Convolutional Network"),
        ("SupCon", "Supervised Contrastive Learning"),
        ("CB-Focal", "Class-Balanced Focal Loss"),
        ("CPM", "Constant Potts Model"),
        ("FNR", "False Negative Rate"),
        ("FPR", "False Positive Rate"),
        ("BalAcc", "Balanced Accuracy"),
        ("MLP", "Multi-Layer Perceptron"),
        ("RF", "Random Forest Classifier"),
        ("RFC", "Request for Comments (IETF Technical Standard)"),
        ("TCP", "Transmission Control Protocol"),
        ("UDP", "User Datagram Protocol"),
        ("IP", "Internet Protocol"),
        ("DDoS", "Distributed Denial of Service"),
        ("DoS", "Denial of Service"),
        ("XSS", "Cross-Site Scripting"),
        ("C2", "Command and Control Infrastructure"),
        ("Non-IID", "Non-Independent and Identically Distributed Data"),
        ("SOC", "Security Operations Center"),
        ("PCAP", "Packet Capture"),
        ("ADFA", "Australian Defence Force Academy"),
        ("DP", "Differential Privacy")
    ]
    a_tab = doc.add_table(rows=1, cols=2)
    a_tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(a_tab)
    a_tab.rows[0].cells[0].text = "ABBREVIATION"
    a_tab.rows[0].cells[1].text = "EXPANSION"
    set_cell_background(a_tab.rows[0].cells[0], "EAEAEA")
    set_cell_background(a_tab.rows[0].cells[1], "EAEAEA")
    for abb, exp in abbrevs:
        r = a_tab.add_row()
        r.cells[0].text = abb
        r.cells[1].text = exp
        r.cells[0].paragraphs[0].runs[0].bold = True

    # Continue with comprehensive chapters...
    print("Front matter generated. Building Chapter 1...")
    
    # Save checkpoint
    doc.save(output_docx_path)
    return doc, md_content

if __name__ == '__main__':
    out_docx = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\PROJECT_REPORT_FED_GNN.docx"
    out_md = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\PROJECT_REPORT_FED_GNN.md"
    fig_dir = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\papers\paper_latex\figures"
    doc, md_content = build_extended_report(out_docx, out_md, fig_dir)
    print("Checkpoint saved.")
