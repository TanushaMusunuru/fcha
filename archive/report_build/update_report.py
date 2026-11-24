import re

with open('dissertation_overleaf.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Title on Title Page
old_title_page = r'''    {\fontsize{15}{19}\selectfont \textbf{\color{amritared} A CONTRASTIVE HYBRID FEDERATED GRAPH NEURAL NETWORK ARCHITECTURE WITH LEAKAGE-CONTROLLED EVALUATION FOR IOT INTRUSION DETECTION}\par}'''
new_title_page = r'''    {\fontsize{14}{18}\selectfont \textbf{\color{amritared} SUPERVISED CONTRASTIVE LEARNING RECOVERS MINORITY ATTACK CLASSES IN FEDERATED GRAPH-BASED IOT INTRUSION DETECTION UNDER LEAKAGE-FREE EVALUATION}\par}'''
assert old_title_page in content, 'Title on Title page not found'
content = content.replace(old_title_page, new_title_page)

# 2. Authors on Title Page
old_authors = r'''    {\fontsize{12}{16}\selectfont \textbf{\color{amritared}
    S.~Mithul \quad [AM.EN.U4AIE21001]\\
    Student~2~Name \quad [AM.EN.U4AIE21002]\\
    Student~3~Name \quad [AM.EN.U4AIE21003]\\
    Student~4~Name \quad [AM.EN.U4AIE21004]
    }\par}'''
new_authors = r'''    {\fontsize{12}{16}\selectfont \textbf{\color{amritared}
    M.~Tanusha \quad [AV.SC.U4AIE23030]\\
    K.~Mithul \quad [AV.SC.U4AIE23025]\\
    G.~Suresh Reddy \quad [AV.SC.U4AIE23014]\\
    D.~Raj Kumar \quad [AV.SC.U4AIE23010]
    }\par}'''
assert old_authors in content, 'Authors on Title page not found'
content = content.replace(old_authors, new_authors)

# 3. Guide on Title Page
old_guide = r'''    {\fontsize{12}{15}\selectfont \textbf{\color{amritared} Guide Name, Ph.D.}\par}'''
new_guide = r'''    {\fontsize{12}{15}\selectfont \textbf{\color{amritared} Dr. Bidyapati Thiyam}\par}'''
assert old_guide in content, 'Guide on Title page not found'
content = content.replace(old_guide, new_guide)

# 4. Degree on Title Page
old_degree = r'''    {\fontsize{11}{14}\selectfont \textbf{\color{amritared} COMPUTER SCIENCE AND ENGINEERING/ COMPUTER SCIENCE AND\\ENGINEERING-ARTIFICIAL INTELLIGENCE}\par}'''
new_degree = r'''    {\fontsize{11}{14}\selectfont \textbf{\color{amritared} COMPUTER SCIENCE AND ENGINEERING\\(ARTIFICIAL INTELLIGENCE)}\par}'''
assert old_degree in content, 'Degree on Title page not found'
content = content.replace(old_degree, new_degree)

# 5. Month & Year on Title Page
content = content.replace('OCTOBER- 2026', 'OCTOBER 2026')

# 6. Certificate Text
old_cert = r'''This is to certify that the project report entitled \textbf{\color{amritared}``A Contrastive Hybrid Federated Graph Neural Network Architecture with Leakage-Controlled Evaluation for IoT Intrusion Detection''} submitted by \textbf{\color{amritared}Student1 name (Roll no), Student2 name (Roll no), Student 3 name( Roll no) and Student4 name( Roll no)} in partial fulfillment of the requirements for the award of Degree \textbf{Bachelor of Technology in} \textbf{\color{amritared}Computer Science and Engineering/ Computer Science and Engineering-Artificial Intelligence} is a Bonafide record of the work carried out under our guidance and supervision at School of Computing, Amrita Vishwa Vidyapeetham, Amaravati.'''

new_cert = r'''This is to certify that the project report entitled \textbf{\color{amritared}``Supervised Contrastive Learning Recovers Minority Attack Classes in Federated Graph-Based IoT Intrusion Detection under Leakage-Free Evaluation''} submitted by \textbf{\color{amritared}M.~Tanusha (AV.SC.U4AIE23030), K.~Mithul (AV.SC.U4AIE23025), G.~Suresh Reddy (AV.SC.U4AIE23014), and D.~Raj Kumar (AV.SC.U4AIE23010)} in partial fulfillment of the requirements for the award of the Degree of \textbf{Bachelor of Technology in} \textbf{\color{amritared}Computer Science and Engineering (Artificial Intelligence)} is a bonafide record of the work carried out under our guidance and supervision at School of Computing, Amrita Vishwa Vidyapeetham, Amaravati.'''
assert old_cert in content, 'Certificate text not found'
content = content.replace(old_cert, new_cert)

# 7. Certificate Guide Table
old_cert_table = r'''\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l r}
\textbf{\color{amritared}Name of the Guide} & \textbf{Dr. M. Nageswara Rao} \\
B.Tech. Project Guide & Chairperson \\
\textbf{\color{amritared}Designation :} & School of Computing \\
School of Computing & \\
\end{tabular*}'''

new_cert_table = r'''\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l r}
\textbf{\color{amritared}Dr. Bidyapati Thiyam} & \textbf{Dr. M. Nageswara Rao} \\
B.Tech. Project Guide & Chairperson \\
\textbf{\color{amritared}Assistant Professor} & School of Computing \\
School of Computing & \\
\end{tabular*}'''
assert old_cert_table in content, 'Certificate table not found'
content = content.replace(old_cert_table, new_cert_table)

# 8. Certificate Review Panel
old_panel = r'''\noindent\textbf{Project Review Panel:}
\begin{enumerate}[leftmargin=20pt, label=\arabic*.]
    \item \textcolor{crimson}{Name/designation/sign with date}
    \item \textcolor{crimson}{Name/designation/sign with date}
    \item \textcolor{crimson}{Name/designation/sign with date}
    \item \textcolor{crimson}{Name/designation/sign with date}
\end{enumerate}'''

new_panel = r'''\noindent\textbf{Project Review Panel:}
\vspace{0.4cm}
\begin{enumerate}[leftmargin=20pt, label=\arabic*.]
    \item \rule{6.5cm}{0.4pt} \hfill Date: \rule{2.5cm}{0.4pt}
    \item \rule{6.5cm}{0.4pt} \hfill Date: \rule{2.5cm}{0.4pt}
    \item \rule{6.5cm}{0.4pt} \hfill Date: \rule{2.5cm}{0.4pt}
\end{enumerate}'''
assert old_panel in content, 'Project Review Panel not found'
content = content.replace(old_panel, new_panel)

# 9. Abstract Header instructions removal
old_abs_hdr = r'''\begin{center}
    {\fontsize{14}{17}\selectfont \textbf{ABSTRACT}}\\[12pt]
    \colorbox{yellow}{\textbf{MAXIMUM OF 250 WORDS}}\\[10pt]
    \textbf{WITH FONT SIZE 12}\\[16pt]
\end{center}'''

new_abs_hdr = r'''\begin{center}
    {\fontsize{14}{17}\selectfont \textbf{ABSTRACT}}\\[16pt]
\end{center}'''
assert old_abs_hdr in content, 'Abstract header not found'
content = content.replace(old_abs_hdr, new_abs_hdr)

# 10. Declaration Text
old_decl = r'''We the undersigned solemnly declare that the project report entitled \textbf{\color{amritared}<Title of the Project>} is based on our own work carried out during the course of our study under the guidance of \textbf{\color{amritared}Guide Name, Designation, Computer Science and Engineering/ Computer Science and Engineering-Artificial Intelligence}, and has not formed the basis for the award of any other degree or diploma, in this or any other Institution or University. In keeping with the ethical practice in reporting scientific information, due acknowledgement has been made wherever the findings of others have been cited.'''

new_decl = r'''We the undersigned solemnly declare that the project report entitled \textbf{\color{amritared}``Supervised Contrastive Learning Recovers Minority Attack Classes in Federated Graph-Based IoT Intrusion Detection under Leakage-Free Evaluation''} is based on our own work carried out during the course of our study under the guidance of \textbf{\color{amritared}Dr.~Bidyapati Thiyam, Assistant Professor, Department of Computer Science and Engineering (Artificial Intelligence)}, and has not formed the basis for the award of any other degree or diploma, in this or any other Institution or University. In keeping with ethical practice in reporting scientific information, due acknowledgement has been made wherever the findings of others have been cited.'''
assert old_decl in content, 'Declaration text not found'
content = content.replace(old_decl, new_decl)

# 11. Declaration Signatures Table
old_decl_table = r'''\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l r}
Student name1 & Signature of the Student1 \\[1.2cm]
Student name2 & Signature of the Student2 \\[1.2cm]
Student name3 & Signature of the Student3 \\[1.2cm]
Student name4 & Signature of the Student4 \\
\end{tabular*}'''

new_decl_table = r'''\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l r}
M.~Tanusha \quad [AV.SC.U4AIE23030] & \rule{5.0cm}{0.4pt} \\[1.2cm]
K.~Mithul \quad [AV.SC.U4AIE23025] & \rule{5.0cm}{0.4pt} \\[1.2cm]
G.~Suresh Reddy \quad [AV.SC.U4AIE23014] & \rule{5.0cm}{0.4pt} \\[1.2cm]
D.~Raj Kumar \quad [AV.SC.U4AIE23010] & \rule{5.0cm}{0.4pt} \\
\end{tabular*}'''
assert old_decl_table in content, 'Declaration table not found'
content = content.replace(old_decl_table, new_decl_table)

# 12. Acknowledgement Text
old_ack = r'''We wish to record our deep sense of gratitude and profound thanks to our project guide \textbf{\color{amritared}Guide Name, Designation}, Amrita School of Computing, for \textbf{\color{amritared}his / her} keen interest, inspiring guidance, constant encouragement with our work during all stages, to bring this project into fruition. We feel extremely grateful to \textbf{\color{amritared}<all Panel members Name, Designation>} for their feedback and encouragement which helped me to complete the project.'''

new_ack = r'''We wish to record our deep sense of gratitude and profound thanks to our project guide \textbf{\color{amritared}Dr.~Bidyapati Thiyam, Assistant Professor}, School of Computing, for his keen interest, inspiring guidance, and constant encouragement with our work during all stages, to bring this project into fruition. We feel extremely grateful to the members of the Project Review Panel for their constructive feedback and encouragement which helped us to complete the project.'''
assert old_ack in content, 'Acknowledgement text not found'
content = content.replace(old_ack, new_ack)

# 13. Acknowledgement Signatures
old_ack_sigs = r'''\begin{flushright}
\textbf{\color{amritared}STUDENT1 NAME}\\[6pt]
\textbf{\color{amritared}STUDENT2 NAME}\\[6pt]
\textbf{\color{amritared}STUDENT3 NAME}\\[6pt]
\textbf{\color{amritared}STUDENT4 NAME}
\end{flushright}'''

new_ack_sigs = r'''\begin{flushright}
\textbf{M.~Tanusha \quad [AV.SC.U4AIE23030]}\\[6pt]
\textbf{K.~Mithul \quad [AV.SC.U4AIE23025]}\\[6pt]
\textbf{G.~Suresh Reddy \quad [AV.SC.U4AIE23014]}\\[6pt]
\textbf{D.~Raj Kumar \quad [AV.SC.U4AIE23010]}
\end{flushright}'''
assert old_ack_sigs in content, 'Acknowledgement signatures not found'
content = content.replace(old_ack_sigs, new_ack_sigs)

# 14. Table of Contents - Part 1
old_toc_p1 = r'''\begin{center}
\renewcommand{\arraystretch}{1.28}
\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{2.0cm}|X|>{\centering\arraybackslash}p{2.0cm}|}
\hline
\textbf{CHAPTER} & \textbf{TITLE} & \textbf{PAGE NOs} \\
\hline
 & \textbf{ABSTRACT} & 3 \\
\hline
 & \textbf{LIST OF TABLES} & 8 \\
\hline
 & \textbf{LIST OF FIGURES} & 9 \\
\hline
 & \textbf{LIST OF ABBREVIATIONS} & 10 \\
\hline
\textbf{1} & \textbf{INTRODUCTION} & \pageref{ch:intro} \\
\hline
1.1 & \textcolor{crimson}{Introduction (Background)} & \pageref{sec:background} \\
\hline
1.2 & \textcolor{crimson}{Problem Statement} & \pageref{sec:problem} \\
\hline
1.3 & \textcolor{crimson}{Objectives} & \pageref{sec:objectives} \\
\hline
1.4 & \textcolor{crimson}{Contributions} & \pageref{sec:contributions} \\
\hline
\textbf{2} & \textbf{LITERATURE SURVEY} & \pageref{ch:literature} \\
\hline
2.1 & \textcolor{crimson}{Comprehensive Survey} & \pageref{sec:comprehensive_survey} \\
\hline
2.2 & \textcolor{crimson}{Summary and Findings of 2.1 in Tabular format} & \pageref{sec:lit_table} \\
\hline
2.3 & \textcolor{crimson}{Challenges} & \pageref{sec:challenges} \\
\hline
2.4 & \textcolor{crimson}{Motivation of the Project Work} & \pageref{sec:motivation} \\
\hline
\textbf{3} & \textbf{MATERIALS AND METHODS} & \pageref{ch:materials} \\
\hline
3.1 & \textcolor{crimson}{Datasets Description} & \pageref{sec:datasets} \\
\hline
3.2 & \textcolor{crimson}{Methods of Data Processing and Pre-processing} & \pageref{sec:preprocessing} \\
\hline
3.3 & \textcolor{crimson}{Programming Tools Details} & \pageref{sec:tools} \\
\hline
\end{tabularx}
\end{center}'''

new_toc_p1 = r'''\begin{center}
\renewcommand{\arraystretch}{1.28}
\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{2.0cm}|X|>{\centering\arraybackslash}p{2.0cm}|}
\hline
\textbf{CHAPTER} & \textbf{TITLE} & \textbf{PAGE NOs} \\
\hline
 & \textbf{ABSTRACT} & 3 \\
\hline
 & \textbf{LIST OF TABLES} & 8 \\
\hline
 & \textbf{LIST OF FIGURES} & 9 \\
\hline
 & \textbf{LIST OF ABBREVIATIONS} & 10 \\
\hline
\textbf{1} & \textbf{INTRODUCTION} & \pageref{ch:intro} \\
\hline
1.1 & Introduction and Background & \pageref{sec:background} \\
\hline
1.2 & Problem Statement & \pageref{sec:problem} \\
\hline
1.3 & Research Objectives & \pageref{sec:objectives} \\
\hline
1.4 & Research Contributions & \pageref{sec:contributions} \\
\hline
\textbf{2} & \textbf{LITERATURE SURVEY} & \pageref{ch:literature} \\
\hline
2.1 & Comprehensive Survey & \pageref{sec:comprehensive_survey} \\
\hline
2.2 & Summary of Literature Survey in Tabular Format & \pageref{sec:lit_table} \\
\hline
2.3 & Open Research Challenges & \pageref{sec:challenges} \\
\hline
2.4 & Motivation of the Project Work & \pageref{sec:motivation} \\
\hline
\textbf{3} & \textbf{MATERIALS AND METHODS} & \pageref{ch:materials} \\
\hline
3.1 & Benchmark Datasets Description & \pageref{sec:datasets} \\
\hline
3.2 & Methods of Data Processing and Pre-processing & \pageref{sec:preprocessing} \\
\hline
3.3 & Programming Tools and Simulation Environment & \pageref{sec:tools} \\
\hline
\end{tabularx}
\end{center}'''
assert old_toc_p1 in content, 'TOC Part 1 not found'
content = content.replace(old_toc_p1, new_toc_p1)

# 15. Table of Contents - Part 2 + Instructions Box Removal
old_toc_p2_and_box = r'''\begin{center}
\renewcommand{\arraystretch}{1.22}
\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{2.0cm}|X|>{\centering\arraybackslash}p{2.0cm}|}
\hline
\textbf{4} & \textbf{METHODOLOGY} & \pageref{ch:methodology} \\
\hline
4.1 & \textcolor{crimson}{Design / Methodology 1 of Existing Work} & \pageref{sec:existing1} \\
\hline
4.2 & \textcolor{crimson}{Design / Methodology 2 of Existing Work} & \pageref{sec:existing2} \\
\hline
4.3 & \textcolor{crimson}{Proposed Architecture} & \pageref{sec:proposed_arch} \\
\hline
4.4 & \textcolor{crimson}{Proposed Design / Methodology} & \pageref{sec:proposed_method} \\
\hline
4.5 & \textcolor{crimson}{Proposed Complete Flowchart} & \pageref{sec:flowchart} \\
\hline
\textbf{5} & \textbf{RESULTS AND DISCUSSION} & \pageref{ch:results} \\
\hline
5.1 & \textcolor{crimson}{Experimental Setup} & \pageref{sec:setup} \\
\hline
5.2 & \textcolor{crimson}{Qualitative Results} & \pageref{sec:qualitative} \\
\hline
5.3 & \textcolor{crimson}{Quantitative Results} & \pageref{sec:quantitative} \\
\hline
5.4 & \textcolor{crimson}{Discussion} & \pageref{sec:discussion} \\
\hline
\textbf{6} & \textbf{CONCLUSION AND FUTURE DIRECTIONS} & \pageref{ch:conclusion} \\
\hline
6.1 & \textcolor{crimson}{Conclusion} & \pageref{sec:conclusion_summary} \\
\hline
6.2 & \textcolor{crimson}{Future Directions} & \pageref{sec:future_directions} \\
\hline
\textbf{7} & \textbf{REFERENCES} & \pageref{ch:references} \\
\hline
 & \textbf{LIST OF PUBLICATIONS}\newline \textcolor{crimson}{\small (Details of Published/Presented/Accepted/Submitted/to be submitted)} & \pageref{sec:publications} \\
\hline
 & \textbf{Plagiarism report with AI (First Page only)} & \pageref{sec:plagiarism} \\
\hline
\end{tabularx}
\end{center}

\vspace{0.3cm}
\noindent\colorbox{yellow}{\textbf{Note : INSTRUCTIONS:}}\par
\vspace{0.15cm}
\begin{enumerate}[leftmargin=22pt, label=\arabic*.]
    \item \colorbox{yellow}{The dissertation report should be between 50 and 100 pages with foam/box binding.}
    \item \colorbox{yellow}{Your guide must verify this report before attending and submitting to the final review.}
    \item \colorbox{yellow}{Proposed work can be modified as per your requirements.}
    \item \colorbox{yellow}{Plagiarism report including AI must be less than 20\%.}
    \item New chapter should start with the new page.
\end{enumerate}'''

new_toc_p2 = r'''\begin{center}
\renewcommand{\arraystretch}{1.28}
\begin{tabularx}{\textwidth}{|>{\centering\arraybackslash}p{2.0cm}|X|>{\centering\arraybackslash}p{2.0cm}|}
\hline
\textbf{4} & \textbf{METHODOLOGY} & \pageref{ch:methodology} \\
\hline
4.1 & Design / Methodology 1 of Existing Work: Centralized Baselines & \pageref{sec:existing1} \\
\hline
4.2 & Design / Methodology 2 of Existing Work: Base FedGATSage Framework & \pageref{sec:existing2} \\
\hline
4.3 & Proposed System Architecture & \pageref{sec:proposed_arch} \\
\hline
4.4 & Proposed Design and Mathematical Methodology & \pageref{sec:proposed_method} \\
\hline
4.5 & Proposed Complete Flowchart and Algorithmic Workflows & \pageref{sec:flowchart} \\
\hline
\textbf{5} & \textbf{RESULTS AND DISCUSSION} & \pageref{ch:results} \\
\hline
5.1 & Experimental Setup & \pageref{sec:setup} \\
\hline
5.2 & Qualitative Results & \pageref{sec:qualitative} \\
\hline
5.3 & Quantitative Results & \pageref{sec:quantitative} \\
\hline
5.4 & Analytical Discussion & \pageref{sec:discussion} \\
\hline
\textbf{6} & \textbf{CONCLUSION AND FUTURE DIRECTIONS} & \pageref{ch:conclusion} \\
\hline
6.1 & Conclusion & \pageref{sec:conclusion_summary} \\
\hline
6.2 & Future Directions & \pageref{sec:future_directions} \\
\hline
\textbf{7} & \textbf{REFERENCES} & \pageref{ch:references} \\
\hline
 & \textbf{LIST OF RESEARCH PUBLICATIONS} & \pageref{sec:publications} \\
\hline
 & \textbf{PLAGIARISM AND AI COMPLIANCE REPORT} & \pageref{sec:plagiarism} \\
\hline
\end{tabularx}
\end{center}'''
assert old_toc_p2_and_box in content, 'TOC Part 2 and instructions box not found'
content = content.replace(old_toc_p2_and_box, new_toc_p2)

# 16. Fix Chapter 1 section header
content = content.replace(r'\section{Introduction (Background)}\label{sec:background}', r'\section{Introduction and Background}\label{sec:background}')

# 17. Fix Chapter 2 section headers and remove stray literal \n
content = content.replace(r'\section{Summary and Findings of 2.1 in Tabular format}\label{sec:lit_table}\n', r'\section{Summary of Literature Survey in Tabular Format}\label{sec:lit_table}')
content = content.replace(r'\section{Challenges}\label{sec:challenges}', r'\section{Open Research Challenges}\label{sec:challenges}')

# 18. Fix Chapter 4 section headers and remove stray literal \n
content = content.replace(r'\section{Design / Methodology 1 of Existing Work}\label{sec:existing1}', r'\section{Design / Methodology 1 of Existing Work: Centralized Baselines}\label{sec:existing1}')
content = content.replace(r'\section{Design / Methodology 2 of Existing Work}\label{sec:existing2}', r'\section{Design / Methodology 2 of Existing Work: Base FedGATSage Framework}\label{sec:existing2}')
content = content.replace(r'\section{Proposed Architecture}\label{sec:proposed_arch}', r'\section{Proposed System Architecture}\label{sec:proposed_arch}')
content = content.replace(r'\section{Proposed Design / Methodology}\label{sec:proposed_method}', r'\section{Proposed Design and Mathematical Methodology}\label{sec:proposed_method}')
content = content.replace(r'\section{Proposed Complete Flowchart}\label{sec:flowchart}\n', r'\section{Proposed Complete Flowchart and Algorithmic Workflows}\label{sec:flowchart}')

# 19. Fix Chapter 5 discussion header
content = content.replace(r'\section{Discussion}\label{sec:discussion}', r'\section{Analytical Discussion}\label{sec:discussion}')

# 20. Publications Section update
old_pubs = r'''\begin{enumerate}
    \item \textbf{S.~Mithul}, Student~2~Name, Student~3~Name, Student~4~Name, and Project~Guide~Name, ``A Contrastive Hybrid Federated Graph Neural Network Architecture with Leakage-Controlled Evaluation for IoT Intrusion Detection,'' prepared for submission to \emph{IEEE Transactions on Information Forensics and Security} (IEEE TIFS), Manuscript Completed \& Verified, October 2026.
    \item \textbf{S.~Mithul}, Student~2~Name, Student~3~Name, and Project~Guide~Name, ``Resolving Majority-Manifold Collapse in Decentralized Graph Neural Networks for Cyber Telemetry,'' presented at \emph{Amrita Research Symposium on Emerging Computing Technologies (ARSECT-2026)}, School of Computing, Amrita Vishwa Vidyapeetham, Amaravati Campus.
\end{enumerate}'''

new_pubs = r'''\begin{enumerate}
    \item \textbf{M.~Tanusha}, \textbf{K.~Mithul}, \textbf{G.~Suresh Reddy}, \textbf{D.~Raj Kumar}, and \textbf{Dr.~Bidyapati Thiyam}, ``Supervised Contrastive Learning Recovers Minority Attack Classes in Federated Graph-Based IoT Intrusion Detection under Leakage-Free Evaluation,'' prepared for submission to \emph{IEEE Transactions on Information Forensics and Security} (IEEE TIFS), Manuscript Completed \& Verified, October 2026.
    \item \textbf{K.~Mithul}, \textbf{M.~Tanusha}, \textbf{G.~Suresh Reddy}, \textbf{D.~Raj Kumar}, and \textbf{Dr.~Bidyapati Thiyam}, ``Resolving Majority-Manifold Collapse in Decentralized Graph Neural Networks for Cyber Telemetry,'' presented at \emph{Amrita Research Symposium on Emerging Computing Technologies (ARSECT-2026)}, School of Computing, Amrita Vishwa Vidyapeetham, Amaravati Campus.
\end{enumerate}'''
assert old_pubs in content, 'Publications not found'
content = content.replace(old_pubs, new_pubs)

# Save updated content
with open('dissertation_overleaf.tex', 'w', encoding='utf-8') as f:
    f.write(content)

print('ALL 20 UPDATES APPLIED SUCCESSFULLY TO dissertation_overleaf.tex!')
