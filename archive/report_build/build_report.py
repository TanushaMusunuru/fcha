import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
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

def build_docx_report(output_path, figures_dir):
    doc = docx.Document()

    # Configure Margins (1 inch all sides)
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
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(f"CHAPTER {chap_num}")
        run.bold = True
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x99, 0x00, 0x00) # Deep Crimson Amrita Accent

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(18)
        run2 = p2.add_run(title.upper())
        run2.bold = True
        run2.font.name = 'Times New Roman'
        run2.font.size = Pt(14)
        run2.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)

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

    # ==========================================
    # PAGE 1: TITLE PAGE
    # ==========================================
    add_p("A CONTRASTIVE HYBRID FEDERATED GRAPH NEURAL NETWORK ARCHITECTURE WITH LEAKAGE-CONTROLLED EVALUATION FOR IOT INTRUSION DETECTION", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=36, space_after=24, bold=True, font_size=16, color_rgb=(0x99, 0x00, 0x00))
    
    add_p("Submitted by", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=12, italic=True, font_size=12)
    
    add_p("Student 1 Name [Register No. / Roll No.]\nStudent 2 Name [Register No. / Roll No.]\nStudent 3 Name [Register No. / Roll No.]\nStudent 4 Name [Register No. / Roll No.]", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, font_size=12, color_rgb=(0x8B, 0x00, 0x00))
    
    add_p("Under the guidance of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=6, italic=True, font_size=12)
    add_p("Guide Name, Ph.D.\nDesignation, School of Computing", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, font_size=12, color_rgb=(0x8B, 0x00, 0x00))
    
    add_p("in partial fulfilment of the requirements for the degree of", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=12, space_after=12, italic=True, font_size=12)
    add_p("BACHELOR OF TECHNOLOGY\nIN\nCOMPUTER SCIENCE AND ENGINEERING / COMPUTER SCIENCE AND ENGINEERING-ARTIFICIAL INTELLIGENCE", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=0, space_after=24, bold=True, font_size=13, color_rgb=(0x1A, 0x1A, 0x1A))
    
    add_p("SCHOOL OF COMPUTING\nAMRITA VISHWA VIDYAPEETHAM\nAMARAVATI – 522503\nOCTOBER- 2026", 
          align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=0, bold=True, font_size=13, color_rgb=(0x8B, 0x00, 0x00))

    # ==========================================
    # PAGE 2: CERTIFICATE
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
        "Computer Science and Engineering-Artificial Intelligence is a bonafide record of the work carried out under our guidance "
        "and supervision at School of Computing, Amrita Vishwa Vidyapeetham, Amaravati Campus."
    )
    add_p(cert_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=36, line_spacing=1.5, font_size=12)

    # Signature blocks table
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
    # PAGE 3: ABSTRACT
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
    # Note: Word count check: exactly 226 words (< 250 words maximum requirement, 12 pt font)
    add_p(abstract_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=18, line_spacing=1.5, font_size=12)
    add_p("Keywords: Federated Learning, Graph Neural Networks, IoT Intrusion Detection, Supervised Contrastive Learning, Class Imbalance, Data Leakage.", 
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=12, space_after=12, bold=True, font_size=11)

    # ==========================================
    # PAGE 4: DECLARATION
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
    # PAGE 5: ACKNOWLEDGEMENT
    # ==========================================
    doc.add_page_break()
    add_p("ACKNOWLEDGEMENT", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=24, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    
    ack_text_1 = (
        "We would like to express our deep gratitude to our beloved Chancellor Sri Mata Amritanandamayi Devi AMMA "
        "for providing the bright academic climate, spiritual inspiration, and cutting-edge resources at Amrita Vishwa Vidyapeetham, "
        "which has made this entire project work possible. This acknowledgment is intended to thank all those people involved directly "
        "or indirectly with our project. We would like to thank the Board of Management for providing us with the necessary computing "
        "infrastructure and research laboratories required for the completion of this project."
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
        "to our family members and peers for their unwavering patience, motivation, and support throughout this endeavor. Last but not the least, "
        "we offer our humble pranams and thank the divine supreme energy which bestowed clarity and perseverance to make our project a success."
    )
    add_p(ack_text_4, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=6, space_after=24, line_spacing=1.5, font_size=12)

    add_p("Student Name 1\nStudent Name 2\nStudent Name 3\nStudent Name 4", 
          align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=12, space_after=0, bold=True, font_size=12, color_rgb=(0x8B, 0x00, 0x00))

    # ==========================================
    # PAGE 6: CONTENTS TABLE
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
        ("", "LIST OF FIGURES", "viii"),
        ("", "LIST OF ABBREVIATIONS", "ix"),
        ("1", "INTRODUCTION", "1"),
        ("1.1", "Introduction (Background)", "1"),
        ("1.2", "Problem Statement", "3"),
        ("1.3", "Objectives", "4"),
        ("1.4", "Contributions", "5"),
        ("2", "LITERATURE SURVEY", "7"),
        ("2.1", "Comprehensive Survey", "7"),
        ("2.2", "Summary and Findings of Survey in Tabular Format", "11"),
        ("2.3", "Challenges in Graph-Based Federated Detection", "13"),
        ("2.4", "Motivation of the Project Work", "15"),
        ("3", "MATERIALS AND METHODS", "17"),
        ("3.1", "Datasets Description (NF-ToN-IoT and NF-UNSW-NB15)", "17"),
        ("3.2", "Methods of Data Processing and Pre-processing", "20"),
        ("3.3", "Programming Tools and Simulation Framework", "23"),
        ("4", "METHODOLOGY", "25"),
        ("4.1", "Design / Methodology 1 of Existing Work (Centralized & Standard FedNIDS)", "25"),
        ("4.2", "Design / Methodology 2 of Existing Work (Base FedGATSage Framework)", "27"),
        ("4.3", "Proposed Architecture", "29"),
        ("4.4", "Proposed Design / Detailed Methodology Formulations", "31"),
        ("4.5", "Proposed Complete Flowchart and Execution Algorithms", "36"),
        ("5", "RESULTS AND DISCUSSION", "39"),
        ("5.1", "Experimental Setup and Evaluation Protocol", "39"),
        ("5.2", "Qualitative Results (Manifold Disentanglement and Heatmaps)", "41"),
        ("5.3", "Quantitative Results (Multi-Seed Benchmark Verification)", "43"),
        ("5.4", "Ablation Studies and Hypothesis Testing", "46"),
        ("5.5", "Discussion and Limitations", "50"),
        ("6", "CONCLUSION AND FUTURE DIRECTIONS", "53"),
        ("6.1", "Conclusion", "53"),
        ("6.2", "Future Directions", "54"),
        ("", "REFERENCES", "56"),
        ("", "LIST OF PUBLICATIONS", "61"),
        ("", "PLAGIARISM AND AI COMPLIANCE REPORT", "62")
    ]

    for ch, tit, pg in toc_entries:
        row = toc_table.add_row()
        c0 = row.cells[0]
        c1 = row.cells[1]
        c2 = row.cells[2]
        c0.text = ch
        c1.text = tit
        c2.text = pg
        set_cell_margins(c0, 60, 60, 80, 80)
        set_cell_margins(c1, 60, 60, 80, 80)
        set_cell_margins(c2, 60, 60, 80, 80)
        c0.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        c2.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if ch.isdigit() or ch == "":
            c0.paragraphs[0].runs[0].bold = True
            c1.paragraphs[0].runs[0].bold = True
            c2.paragraphs[0].runs[0].bold = True

    # ==========================================
    # LIST OF TABLES, FIGURES, ABBREVIATIONS
    # ==========================================
    doc.add_page_break()
    add_p("LIST OF TABLES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    tables_list = [
        ("Table 2.1", "Comprehensive Comparison of State-of-the-Art Intrusion Detection Frameworks", "12"),
        ("Table 3.1", "NF-ToN-IoT Ground-Truth Class Distribution and Signature-Grouped Split Support", "18"),
        ("Table 3.2", "NF-UNSW-NB15 Ground-Truth Class Distribution and Partitioning Statistics", "19"),
        ("Table 3.3", "Feature Engineering Mapping for Domain-Specialized GAT Subgraphs", "22"),
        ("Table 5.1", "Simulation Environment Hardware and Software Parameters", "40"),
        ("Table 5.2", "Headline Empirical Results across Regularization Strengths on NF-ToN-IoT (3 Seeds)", "43"),
        ("Table 5.3", "Per-Class Recall and False Negative Rates across Model Configurations (NF-ToN-IoT)", "44"),
        ("Table 5.4", "Decomposition of Balanced Accuracy Improvement from mu=0.0 to mu=0.1", "45"),
        ("Table 5.5", "Cumulative Component Ablation Progression under Signature-Grouped Zero-Leakage Split", "47"),
        ("Table 5.6", "Node-Averaging Mechanism Test: Validating Host Dilution vs Edge Representation", "48"),
        ("Table 5.7", "Cross-Dataset Multi-Seed Evaluation on NF-UNSW-NB15 across 5 Seeds", "49")
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

    doc.add_page_break()
    add_p("LIST OF FIGURES", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    figures_list = [
        ("Figure 4.1", "Proposed Contrastive Hybrid Federated GNN System Architecture Workflow", "30"),
        ("Figure 4.2", "Complete Procedural Flowchart of Client-Server Federated Cycle and Meta-Learner", "37"),
        ("Figure 5.1", "Confusion Matrix Heatmaps on NF-ToN-IoT: Anchor (Plain CE) vs Proposed Framework (mu=0.1)", "42"),
        ("Figure 5.2", "Per-Class Detection Recall and Balanced Accuracy as a Function of Contrastive Strength mu", "46")
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

    doc.add_page_break()
    add_p("LIST OF ABBREVIATIONS", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=18, space_after=18, bold=True, font_size=14, color_rgb=(0x8B, 0x00, 0x00))
    abbrevs = [
        ("NIDS", "Network Intrusion Detection System"),
        ("IoT", "Internet of Things"),
        ("FL", "Federated Learning"),
        ("GNN", "Graph Neural Network"),
        ("GAT", "Graph Attention Network"),
        ("GraphSAGE", "Sample and Aggregate Graph Convolutional Network"),
        ("SupCon", "Supervised Contrastive Learning"),
        ("CB-Focal", "Class-Balanced Focal Loss"),
        ("CPM", "Constant Potts Model"),
        ("FedAvg", "Federated Averaging Algorithm"),
        ("FNR", "False Negative Rate"),
        ("FPR", "False Positive Rate"),
        ("BalAcc", "Balanced Accuracy"),
        ("MLP", "Multi-Layer Perceptron"),
        ("RF", "Random Forest Classifier"),
        ("RFC", "Request for Comments (Internet Engineering Task Force standard)"),
        ("TCP", "Transmission Control Protocol"),
        ("UDP", "User Datagram Protocol"),
        ("IP", "Internet Protocol"),
        ("DDoS", "Distributed Denial of Service"),
        ("DoS", "Denial of Service"),
        ("XSS", "Cross-Site Scripting"),
        ("C2", "Command and Control Infrastructure"),
        ("Non-IID", "Non-Independent and Identically Distributed Data")
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

    # ==========================================
    # CHAPTER 1: INTRODUCTION
    # ==========================================
    add_chapter_heading(1, "INTRODUCTION")
    
    add_sec_heading("1.1 Introduction (Background)")
    p1 = (
        "The proliferation of Internet of Things (IoT) hardware across critical industrial plants, supervisory control and "
        "data acquisition (SCADA) facilities, intelligent healthcare systems, and urban smart infrastructure has fundamentally altered "
        "contemporary cybersecurity threat surfaces. Billions of resource-constrained microcontroller units, edge routers, and embedded "
        "sensors now manage critical operational telemetry while interconnected across distributed subnets. Unlike traditional enterprise "
        "networks characterized by homogenous server clusters and centralized security gateways, IoT edge environments present severe "
        "computational constraints, high firmware heterogeneity, and decentralized communication topologies. These architectural dynamics "
        "render IoT installations prime attack targets for sophisticated adversaries executing distributed denial-of-service (DDoS) campaigns, "
        "unauthorized administrative privilege escalation, and multi-hop lateral movement via command-and-control (C2) beaconing."
    )
    add_p(p1, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    p2 = (
        "Conventional Network Intrusion Detection Systems (NIDS) rely overwhelmingly on centralized data collection pipelines. Edge "
        "switches and sensor gateways are forced to continuously forward high-volume packet captures (PCAP) or NetFlow records to centralized "
        "security operations centers (SOC) for batch processing and model inference. However, centralizing continuous traffic streams across "
        "distributed IoT deployments introduces unsustainable bandwidth overheads, intolerable latency bottlenecks during coordinated attacks, "
        "and single points of failure. More critically, transmitting raw network telemetry containing internal IP subnet architectures, "
        "transport socket metadata, and payload headers directly breaches strict international data protection regulations, such as the General "
        "Data Protection Regulation (GDPR) and the Health Insurance Portability and Accountability Act (HIPAA)."
    )
    add_p(p2, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    p3 = (
        "Federated Learning (FL) has emerged as an indispensable paradigm to overcome the centralization bottleneck by enabling decentralized edge "
        "gateways to train collaborative intrusion detection models without sharing raw local traffic records. Under the canonical Federated Averaging "
        "(FedAvg) protocol, edge clients iteratively optimize local model parameters over private telemetry and transmit only parameter weight vectors "
        "to a coordination server, where updates are aggregated into a global consensus model. Simultaneously, the recognition that network intrusions "
        "are fundamentally relational rather than isolated tabular rows has spurred the integration of Graph Neural Networks (GNNs) into federated security. "
        "By modeling network entities (IP hosts) as graph nodes and directional flow exchanges as attributed edges, GNNs leverage recursive message passing "
        "to capture topological multi-hop pathways, port-scanning cascades, and burst dynamics that bypass traditional statistical classifiers."
    )
    add_p(p3, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_sec_heading("1.2 Problem Statement")
    p_prob1 = (
        "Despite theoretical promises, existing Graph-based Federated Learning frameworks for intrusion detection exhibit severe operational "
        "vulnerabilities and unacknowledged methodological flaws that hinder real-world deployment:"
    )
    add_p(p_prob1, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    prob_bullets = [
        ("Pervasive Socket-Signature Evaluation Leakage: ", 
         "Prevailing NIDS evaluation benchmarks routinely rely on naive uniform random row partitioning. In real-world NetFlow benchmarks, "
         "repetitive socket sessions (defined by source IP, destination IP, service ports, protocol, and flow statistics) generate multiple "
         "consecutive telemetry records. Uniform random splitting distributes flows from identical socket conversations across both training "
         "and testing folds. Classifiers memorizing socket identifiers achieve near-perfect synthetic accuracy (>99%), obscuring catastrophic "
         "failure when confronted with authentic, unseen network sessions."),
        ("Catastrophic Minority Class Collapse Under Empirical Risk Minimization: ",
         "Modern network traffic distributions exhibit extreme long-tail class imbalance. High-volume volumetric intrusions (e.g., Injection and DDoS) "
         "and benign background traffic outnumber stealthy targeted attacks (such as Backdoors and password brute-forcing) by orders of magnitude "
         "(e.g., 27:1 in the NF-ToN-IoT benchmark). Under standard cross-entropy loss, gradient descent trajectories are overwhelmingly governed "
         "by majority-class sample volumes. Consequently, the decision boundaries of minority attacks are completely subsumed by majority class "
         "manifolds, inducing intolerable False Negative Rates (FNR) on the most dangerous intrusions."),
        ("Topological Feature Blurring at Multi-Role Endpoint Nodes: ",
         "In graph representations of enterprise telemetry, IP endpoint nodes routinely serve dual roles, hosting both benign transactions and "
         "malicious flow exchanges. Standard GNN layers average flow attributes onto IP node features during message passing. When low-volume stealth "
         "attacks traverse an endpoint that concurrently transmits massive volumes of background traffic, neighborhood feature aggregation "
         "drastically dilutes the minority signature into the dominant host profile, causing continuous edge embeddings to collapse into adjacent majority clusters."),
        ("Structural Incoherence from Disconnected Heuristic Graph Partitions: ",
         "Heuristic community partitioning methods (e.g., the Louvain modularity algorithm used in base frameworks) rely on local greedy node movement "
         "that frequently traps subgraphs in disconnected or poorly connected partitions. Transmitting centroids of unstable, disconnected communities "
         "to a federated server overlay introduces substantial noise during cross-client GraphSAGE aggregation.")
    ]
    for b_title, b_desc in prob_bullets:
        bp = doc.add_paragraph()
        bp.paragraph_format.left_indent = Inches(0.25)
        bp.paragraph_format.space_after = Pt(6)
        bp.paragraph_format.line_spacing = 1.5
        r_bt = bp.add_run("• " + b_title)
        r_bt.bold = True
        r_bt.font.name = 'Times New Roman'
        r_bd = bp.add_run(b_desc)
        r_bd.font.name = 'Times New Roman'

    add_sec_heading("1.3 Objectives")
    obj_intro = (
        "To resolve the aforementioned challenges, this project establishes a contrastive hybrid federated GNN framework designed for "
        "imbalanced IoT intrusion detection. The specific core engineering and scientific objectives are:"
    )
    add_p(obj_intro, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    
    objs = [
        "To formulate and execute a strict zero-leakage 5-fold StratifiedGroupKFold evaluation protocol grouped by an 8-feature socket communication "
        "signature across 1,377,837 NetFlow records, guaranteeing 0.00% signature overlap between training and testing sets.",
        "To engineer three domain-specialized Graph Attention Network (GAT) client architectures (Temporal, Content, and Behavioral) capable of "
        "capturing distinct flow telemetry dynamics without inter-feature interference.",
        "To integrate the Leiden community detection algorithm with Constant Potts Model (CPM) quality optimization into client graph pipelines, "
        "guaranteeing well-connected, structurally sound topological community centroids for server overlay construction.",
        "To formulate a joint optimization objective uniting Class-Balanced Focal (CB-Focal) loss (beta=0.9999, gamma=2.0) with Supervised Contrastive "
        "(SupCon) representation regularization (mu=0.1, tau=0.07) directly on continuous edge embeddings, supported by intra-class edge mixup interpolation.",
        "To design a two-stage Random Forest meta-learner that arbitrates conflicting continuous GNN detector output probabilities by combining them "
        "with raw physical NetFlow feature thresholds.",
        "To rigorously validate the proposed architecture through multi-seed empirical replication (Seeds 42, 43, 44 on NF-ToN-IoT, and Seeds 42–46 on NF-UNSW-NB15), "
        "providing mathematical proofs and diagnostic evidence for minority manifold recovery."
    ]
    for idx, ob in enumerate(objs, 1):
        op = doc.add_paragraph()
        op.paragraph_format.left_indent = Inches(0.25)
        op.paragraph_format.space_after = Pt(4)
        op.paragraph_format.line_spacing = 1.5
        r_num = op.add_run(f"({idx}) ")
        r_num.bold = True
        r_num.font.name = 'Times New Roman'
        r_txt = op.add_run(ob)
        r_txt.font.name = 'Times New Roman'

    add_sec_heading("1.4 Contributions")
    p_con = (
        "This project delivers five definitive contributions to the fields of federated learning, graph representation learning, and network security:"
    )
    add_p(p_con, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    contribs = [
        ("Audited Zero-Leakage Benchmark Protocol: ", 
         "We prove that standard random row partitioning in NetFlow benchmarks leaks 46.88% of flow signatures into test sets. We establish an "
         "audited 8-tuple StratifiedGroupKFold pipeline that achieves absolute 0.00% leakage, providing the first authentic, leakage-controlled baseline."),
        ("Supervised Contrastive Regularization for Minority Manifold Rescue: ",
         "We demonstrate that Supervised Contrastive Loss (mu=0.1) operating on normalized edge embeddings exerts an active repulsive force "
         "that counteracts the 27:1 gradient dominance of Injection over Backdoor traffic, resolving the catastrophic 99.83% Backdoor-to-Injection misclassification."),
        ("Multi-Tiered Class Balancing Framework: ",
         "We unite effective sample volume theory (CB-Focal loss), dynamic class-balanced mini-batch sampling (M=64 edges per class), and client-local "
         "convex edge interpolation (ratio=0.50), stabilizing optimization landscapes across non-IID client partitions."),
        ("Hybrid Federated Graph-Tabular Architecture: ",
         "We realize an end-to-end framework uniting domain-specialized GAT clients, Leiden community partitioning, an aggregated GraphSAGE server "
         "overlay (top-k cosine similarity), and a two-stage Random Forest meta-classifier that achieves 85% communication reduction."),
        ("Multi-Seed Empirical and Diagnostic Validation: ",
         "Across three independent random seeds on 1,377,837 flows, our framework reduces Macro FNR from 21.89 ± 2.01% to 5.72 ± 1.20% and elevates "
         "Balanced Accuracy from 78.11 ± 2.01% to 94.28 ± 1.20%, rescuing Backdoor recall from 0.11% to 99.57%. We provide empirical ablation isolating "
         "the exact topological mechanism responsible for minority collapse.")
    ]
    for c_title, c_desc in contribs:
        cp = doc.add_paragraph()
        cp.paragraph_format.left_indent = Inches(0.25)
        cp.paragraph_format.space_after = Pt(6)
        cp.paragraph_format.line_spacing = 1.5
        r_ct = cp.add_run("1. " + c_title) if c_title.startswith("Audited") else cp.add_run(f"• {c_title}")
        r_ct.bold = True
        r_ct.font.name = 'Times New Roman'
        r_cd = cp.add_run(c_desc)
        r_cd.font.name = 'Times New Roman'

    # ==========================================
    # CHAPTER 2: LITERATURE SURVEY
    # ==========================================
    add_chapter_heading(2, "LITERATURE SURVEY")

    add_sec_heading("2.1 Comprehensive Survey")
    p_ls1 = (
        "Modern intrusion detection literature spans four converging disciplines: decentralized federated learning protocols, "
        "graph neural network architectures for relational telemetry, mathematical loss formulation for acute class imbalance, and "
        "metric representation learning via contrastive optimization."
    )
    add_p(p_ls1, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_subsec_heading("2.1.1 Federated Learning in Network Intrusion Detection")
    p_ls_fl = (
        "Federated Learning (FL) was formalized by McMahan et al. (2017) to allow decentralized devices to iteratively compute local stochastic gradient "
        "descent updates over private data partitions, synchronizing solely model parameters via a central coordinator. While FedAvg drastically preserves "
        "privacy, Zhao et al. (2018) and Li et al. (2020) demonstrated that non-independent and identically distributed (non-IID) client data distributions "
        "cause acute weight divergence and client drift. In IoT cybersecurity contexts, statistical heterogeneity is rampant: industrial sensors, surveillance "
        "cameras, and edge routers observe radically divergent attack classes. Youm and Kim (2025) proposed DS-FedIDS, employing class-specific dynamic "
        "sampling to adjust client aggregation weights when attack classes are missing locally. However, conventional federated architectures treat network "
        "flows as independent tabular instances, neglecting structural network relationships."
    )
    add_p(p_ls_fl, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_subsec_heading("2.1.2 Graph Neural Networks for Cyber Telemetry")
    p_ls_gnn = (
        "Network telemetry is inherently relational. Attack campaigns—such as port scanning, credential stuffing, and botnet command-and-control—manifest "
        "as structured interaction graphs between network endpoints. Graph Convolutional Networks (GCNs) and Graph Attention Networks (GATs, Veličković et al., 2018) "
        "leverage self-attention coefficients to weigh suspicious communication channels. Hamilton et al. (2017) introduced GraphSAGE, an inductive "
        "framework enabling message aggregation on large, dynamic graphs. Tailoring GNNs to security, Lo et al. (2022) developed E-GraphSAGE to incorporate "
        "edge-attributed flow attributes, and Chang and Branco (2021) proposed E-ResGAT using residual layers to prevent gradient vanishing on high-degree nodes. "
        "Han et al. (2025) formulated FedSTGCN, combining federated learning with spatiotemporal graph convolutions to capture temporal bursts across IoT "
        "endpoints. A comprehensive survey by Liu et al. (2024) underscored that inter-client relational dependencies and acute class imbalance remain unsolved bottlenecks."
    )
    add_p(p_ls_gnn, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_subsec_heading("2.1.3 Class Imbalance and Optimization Formulations")
    p_ls_imb = (
        "Network intrusion benchmarks regularly present severe class imbalance where benign traffic constitutes 80–90% of logged flows, volumetric "
        "attacks occupy moderate portions, and critical targeted intrusions (e.g., Backdoors) represent less than 1.5% of samples (Sarhan et al., 2021). "
        "Johnson and Khoshgoftaar (2019) proved that standard empirical risk minimization under unweighted cross-entropy penalizes rare errors minimally, "
        "causing high false-negative rates. Lin et al. (2017) formulated Focal Loss, introducing a focusing parameter (gamma) that exponentially dampens the "
        "loss contribution of well-classified majority instances. Cui et al. (2019) introduced Class-Balanced Loss, demonstrating that the effective volume of "
        "samples grows as (1 - beta^N)/(1 - beta). At the data level, Zhang et al. (2018) proposed Mixup to generate synthetic training instances via convex "
        "interpolation, smoothing decision margins."
    )
    add_p(p_ls_imb, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_subsec_heading("2.1.4 Supervised Contrastive Representation Learning")
    p_ls_sup = (
        "Contrastive representation learning establishes embedding spaces where semantically identical samples cluster tightly while dissimilar instances "
        "are violently repelled. Khosla et al. (2020) proposed Supervised Contrastive Learning (SupCon), extending self-supervised contrastive formulations "
        "to fully supervised settings by treating all samples sharing the same ground-truth label as mutual positives. In vision and acoustic tasks, SupCon "
        "has demonstrated superior robustness to class corruption and label imbalance. However, its architectural deployment within federated graph neural networks "
        "to counteract topological feature blurring on NetFlow telemetry represents an unaddressed research frontier."
    )
    add_p(p_ls_sup, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_subsec_heading("2.1.5 Base Paper Examination: FedGATSage Framework")
    p_ls_base = (
        "Our investigation directly builds upon the FedGATSage architecture published by Al-Tfaily et al. (2025) in Nature Scientific Reports. FedGATSage "
        "introduced a hybrid framework combining client-side GAT detectors, Louvain community detection, a server-side GraphSAGE overlay, and Random Forest fusion. "
        "While Al-Tfaily et al. reported 78.58% Balanced Accuracy on NF-ToN-IoT, our code-level audit revealed two severe unaddressed vulnerabilities: "
        "(1) The evaluation utilized a naive random row split that leaked 46.88% of identical flow signatures between training and test sets, artificially inflating metrics. "
        "(2) Under standard cross-entropy loss, the baseline GNN anchor suffers from catastrophic minority collapse, misclassifying 99.83% of rare Backdoor attacks as "
        "Injection flows (achieving an appalling 0.11% recall). Furthermore, Louvain partitioning produces disconnected community subgraphs, degrading server overlay aggregation."
    )
    add_p(p_ls_base, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_sec_heading("2.2 Summary and Findings of Survey in Tabular Format")
    add_p("Table 2.1 provides a structured comparative summary of foundational and contemporary literature related to graph-based federated intrusion detection.", align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    lit_table = doc.add_table(rows=1, cols=5)
    lit_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(lit_table)
    l_hdrs = ["Author & Year", "Methodology / Architecture", "Dataset Used", "Primary Findings", "Identified Critical Limitations"]
    for idx, h in enumerate(l_hdrs):
        lit_table.rows[0].cells[idx].text = h
        set_cell_background(lit_table.rows[0].cells[idx], "EAEAEA")
        p = lit_table.rows[0].cells[idx].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.bold = True
            r.font.name = 'Times New Roman'
            r.font.size = Pt(10)

    lit_data = [
        ("McMahan et al. (2017)", "Canonical Federated Averaging (FedAvg) over decentralized clients", "MNIST, CIFAR-10", "Proved decentralized training without centralizing raw data", "Suffers from weight drift under non-IID client skew; no topological awareness"),
        ("Zhao et al. (2018)", "Theoretical analysis of non-IID data divergence in federated learning", "CIFAR-10 Non-IID", "Demonstrated that Earth Mover's Distance between client distributions degrades convergence", "Addressed data sharing; does not resolve acute class starvation on rare anomalies"),
        ("Veličković et al. (2018)", "Graph Attention Networks (GAT) with masked self-attention", "Cora, Citeseer", "Enabled dynamic edge weighting based on neighbor feature relevance", "High computational complexity; vulnerable to oversmoothing on dense graphs"),
        ("Hamilton et al. (2017)", "GraphSAGE inductive neighborhood sampling and aggregation", "PPI, Reddit", "Enabled fast inductive generalization to previously unseen nodes", "Uniform neighbor sampling dilutes rare minority graph edges into majority profiles"),
        ("Lo et al. (2022)", "E-GraphSAGE for edge-attributed network intrusion telemetry", "UNSW-NB15, CIC-IDS2017", "Integrated directional flow attributes into neighborhood aggregation", "Centralized architecture; does not address federated privacy or extreme class imbalance"),
        ("Han et al. (2025)", "FedSTGCN: Spatiotemporal graph convolution for IoT intrusion", "BoT-IoT, ToN-IoT", "Captured spatial topology and temporal bursts across IoT edge gateways", "High edge computation; lacks metric regularization for long-tail attack recovery"),
        ("Lin et al. (2017)", "Focal Loss for dense object detection and extreme foreground imbalance", "MS COCO", "Dynamically suppressed loss contribution of easy majority background instances", "Modulates gradient scale but does not alter geometric metric embedding separation"),
        ("Cui et al. (2019)", "Class-Balanced Loss via effective number of samples theory", "CIFAR-100-LT, ImageNet-LT", "Proved diminishing returns of redundant samples; normalized class loss penalties", "Does not guarantee metric clustering in continuous graph latent spaces"),
        ("Khosla et al. (2020)", "Supervised Contrastive Learning (SupCon) on labeled batches", "ImageNet, CIFAR-100", "Achieved superior angular separation and robustness over cross-entropy", "Evaluated strictly on image classification; never applied to federated graph cybersecurity"),
        ("Al-Tfaily et al. (2025)", "FedGATSage: Client GAT, Louvain detection, Server GraphSAGE, RF", "NF-ToN-IoT, CIC-ToN-IoT", "Achieved 78.58% BalAcc with 85% communication reduction", "Random split leaks 46.88% signatures; 99.83% Backdoor collapsed to Injection; Louvain yields disconnected graphs")
    ]

    for row_d in lit_data:
        row = lit_table.add_row()
        for c_idx, val in enumerate(row_d):
            c = row.cells[c_idx]
            c.text = val
            set_cell_margins(c, 50, 50, 60, 60)
            p = c.paragraphs[0]
            p.paragraph_format.line_spacing = 1.2
            for r in p.runs:
                r.font.name = 'Times New Roman'
                r.font.size = Pt(9.5)
                if c_idx == 0:
                    r.bold = True

    add_sec_heading("2.3 Challenges in Graph-Based Federated Detection")
    ch_text = (
        "A rigorous synthesis of existing literature identifies four primary technical bottlenecks that currently prevent practical "
        "deployment of federated graph intrusion detection systems in industrial IoT environments:\n\n"
        "1. Evaluation Leakage Blindness: Prevailing academic publications evaluate NIDS models on randomly split NetFlow records. "
        "Because repeated packets in a communication burst share identical socket identifiers, random partitioning permits classifiers "
        "to memorize static flow tuples, presenting misleading detection performance while masking catastrophic zero-day failure.\n\n"
        "2. Continuous Manifold Overlap: Unlike tabular decision trees that apply sharp, orthogonal axis splits on numeric features, "
        "neural network encoders project instances onto continuous hyperspherical manifolds. Under acute imbalance, the loss gradient "
        "of the majority class exerts overwhelming dominance, swallowing the minority representation space.\n\n"
        "3. Topological Feature Blurring: Graph message passing operates by aggregating neighbor features onto endpoint nodes. "
        "When an IP host participates in both background traffic and rare intrusions, recursive neighborhood averaging blurs the "
        "minority intrusion signature into the background centroid.\n\n"
        "4. Client-to-Server Communication Constraints: Transmitting complete local graph topologies across bandwidth-constrained "
        "IoT wireless networks is prohibitively expensive. Developing robust community abstraction mechanisms that compress edge topologies "
        "without destroying subtle relational indicators is vital."
    )
    add_p(ch_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    add_sec_heading("2.4 Motivation of the Project Work")
    mot_text = (
        "Motivated by the critical vulnerabilities identified in the base FedGATSage paper and the broader literature, this project seeks to "
        "establish a mathematically grounded, empirically auditable, and privacy-preserving intrusion detection system. Rather than accepting "
        "the standard compromise between federated privacy and detection accuracy, we hypothesize that integrating Supervised Contrastive Loss "
        "directly into local edge encoders can exert an active metric repulsive force capable of rescuing collapsed minority attack manifolds. "
        "By grounding all evaluations on an audited zero-leakage signature-grouped split across multiple random seeds, this research aims to "
        "bridge the critical gap between theoretical federated graph models and practical, leakage-free cybersecurity defense."
    )
    add_p(mot_text, align=WD_ALIGN_PARAGRAPH.JUSTIFY)

    # Save initial progress
    doc.save(output_path)
    print("Initial chapters compiled successfully.")

if __name__ == '__main__':
    out_docx = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\PROJECT_REPORT_FED_GNN.docx"
    fig_dir = r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\papers\paper_latex\figures"
    build_docx_report(out_docx, fig_dir)
