# -*- coding: utf-8 -*-
"""
Generates the complete monolithic dissertation_overleaf.tex file.
"""

import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

import text_ch1
import text_ch2
import text_ch3
import text_ch4
import text_ch5
import text_ch6

def build_full_latex():
    # Read existing chapters from build_overleaf_tex.py
    with open("build_overleaf_tex.py", "r", encoding="utf-8") as f:
        orig = f.read()

    idx_ch1 = orig.find(r"\chapter{Introduction}")
    idx_ch2 = orig.find(r"\chapter{Literature Survey}")
    idx_ch3 = orig.find(r"\chapter{Materials and Methods}")
    idx_ch4 = orig.find(r"\chapter{Methodology}")
    idx_ch5 = orig.find(r"\chapter{Results and Discussion}")
    idx_ch6 = orig.find(r"\chapter{Conclusion and Future Directions}")
    idx_bib = orig.find(r"\begin{thebibliography}")
    idx_end_bib = orig.find(r"\end{thebibliography}") + len(r"\end{thebibliography}")
    idx_pub = orig.find(r"% LIST OF PUBLICATIONS")
    idx_end_doc = orig.rfind(r"\end{document}")

    ch1_body = orig[idx_ch1:idx_ch2]
    ch2_body = orig[idx_ch2:idx_ch3]
    ch3_body = orig[idx_ch3:idx_ch4]
    ch4_body = orig[idx_ch4:idx_ch5]
    ch5_body = orig[idx_ch5:idx_ch6]
    ch6_body = orig[idx_ch6:idx_bib]
    bib_body = orig[idx_bib:idx_end_bib]
    back_body = orig[idx_pub:idx_end_doc]

    # Build Preamble
    preamble = r"""\documentclass[12pt,a4paper]{report}

% =========================================================================
% Academic Packages
% =========================================================================
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb,amsfonts,bm,mathtools}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage{array}
\usepackage{longtable}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{float}
\usepackage{algorithm}
\usepackage{algpseudocode}
\usepackage{setspace}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{eso-pic}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{enumitem}
\usepackage[hidelinks,pdfusetitle]{hyperref}

% =========================================================================
% Page Geometry & Margins (1.0 inch all around)
% =========================================================================
\usepackage[a4paper,top=1.0in,bottom=1.0in,left=1.0in,right=1.0in,headheight=15pt,headsep=12pt,footskip=0pt]{geometry}

% =========================================================================
% Institutional Color Palette
% =========================================================================
\definecolor{amritared}{RGB}{179, 0, 0}       % University Crimson
\definecolor{crimson}{RGB}{179, 0, 0}         % Matching template text in red
\definecolor{charcoal}{RGB}{30, 41, 59}        % Heading Charcoal
\definecolor{tableheader}{RGB}{241, 245, 249}  % Subtle Table Header Fill
\definecolor{lightgrayline}{RGB}{203, 213, 225}% Subtle Divider Lines

% =========================================================================
% Professional Academic Page Border (Single-Line Border on Every Page)
% =========================================================================
\AddToShipoutPictureBG{%
  \begin{tikzpicture}[remember picture, overlay]
    \draw[line width=1.0pt, draw=black] 
      ([xshift=10mm, yshift=-10mm]current page.north west) 
      rectangle 
      ([xshift=-10mm, yshift=10mm]current page.south east);
  \end{tikzpicture}%
}

% =========================================================================
% Typography & Spacing Configuration
% =========================================================================
\onehalfspacing
\setlength{\parskip}{8pt plus 2pt minus 1pt}
\setlength{\parindent}{0pt}
\setlist{itemsep=3pt, topsep=2pt, parsep=0pt, leftmargin=22pt}

% =========================================================================
% Chapter and Section Heading Styling
% =========================================================================
\titleformat{\chapter}[display]
  {\normalfont\bfseries\centering}
  {\fontsize{16}{18}\selectfont\color{charcoal}CHAPTER \thechapter}
  {4pt}
  {\fontsize{14}{17}\selectfont\color{charcoal}\MakeUppercase}
\titlespacing*{\chapter}{0pt}{-10pt}{20pt}

\titleformat{\section}
  {\normalfont\fontsize{13}{16}\selectfont\bfseries\color{charcoal}}
  {\thesection}{1em}{}
\titlespacing*{\section}{0pt}{14pt}{6pt}

\titleformat{\subsection}
  {\normalfont\fontsize{12}{15}\selectfont\bfseries\itshape\color{charcoal}}
  {\thesubsection}{1em}{}
\titlespacing*{\subsection}{0pt}{10pt}{4pt}

\titleformat{\subsubsection}
  {\normalfont\fontsize{11}{14}\selectfont\bfseries\color{charcoal}}
  {\thesubsubsection}{1em}{}
\titlespacing*{\subsubsection}{0pt}{8pt}{3pt}

% =========================================================================
% Header and Footer Styling (NO running headers, NO footers, NO lines)
% Only bare page number at top right of every page
% =========================================================================
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\fancypagestyle{plain}{
  \fancyhf{}
  \rhead{\thepage}
  \renewcommand{\headrulewidth}{0pt}
  \renewcommand{\footrulewidth}{0pt}
}

% =========================================================================
% University Emblem Macro
% =========================================================================
\newcommand{\amritaemblem}[1][2.2cm]{%
  \IfFileExists{amrita_logo.png}{%
    \includegraphics[width=#1]{amrita_logo.png}%
  }{%
    \begin{tikzpicture}[scale=0.5]
      \draw[line width=1.5pt, draw=amritared, fill=amritared!5] (0,0) circle (2.0cm);
      \draw[line width=0.8pt, draw=amritared] (0,0) circle (1.8cm);
      \draw[line width=0.8pt, draw=amritared, fill=white] (0,0) circle (1.1cm);
      % Lotus petal stylization
      \foreach \ang in {0, 45, 90, 135, 180, 225, 270, 315} {
        \draw[draw=amritared, fill=amritared!20] (\ang:0.4) circle (0.2cm);
      }
      \node[align=center] at (0,0) {\color{amritared}\fontsize{11}{12}\selectfont\bfseries A};
      \node[align=center, font=\fontsize{4.5}{5.5}\selectfont\bfseries] at (0,1.45) {\color{amritared}AMRITA VISHWA VIDYAPEETHAM};
      \node[align=center, font=\fontsize{4.5}{5.5}\selectfont\bfseries] at (0,-1.45) {\color{amritared}श्रद्धावान् लभते ज्ञानम्};
    \end{tikzpicture}%
  }%
}

% Path for figures
\graphicspath{{figures/}{./}}

\begin{document}
"""

    # Build Front Matter (Pages 1 to 7 strictly matching screenshots)
    front_matter = r"""
% =========================================================================
% PAGE 1: TITLE PAGE (Exact Institutional Layout from Template Screenshot 1)
% =========================================================================
\thispagestyle{plain}
\begin{center}
    \vspace*{0.2cm}
    {\fontsize{15}{19}\selectfont \textbf{\color{amritared} A CONTRASTIVE HYBRID FEDERATED GRAPH NEURAL NETWORK ARCHITECTURE WITH LEAKAGE-CONTROLLED EVALUATION FOR IOT INTRUSION DETECTION}\par}
    
    \vspace{0.8cm}
    {\fontsize{12}{14}\selectfont Submitted by\par}
    
    \vspace{0.4cm}
    {\fontsize{12}{16}\selectfont \textbf{\color{amritared}
    S.~Mithul \quad [AM.EN.U4AIE21001]\\
    Student~2~Name \quad [AM.EN.U4AIE21002]\\
    Student~3~Name \quad [AM.EN.U4AIE21003]\\
    Student~4~Name \quad [AM.EN.U4AIE21004]
    }\par}
    
    \vspace{0.6cm}
    {\fontsize{12}{14}\selectfont \textit{Under the guidance of}\par}
    
    \vspace{0.2cm}
    {\fontsize{12}{15}\selectfont \textbf{\color{amritared} Guide Name, Ph.D.}\par}
    
    \vspace{0.6cm}
    {\fontsize{11}{13}\selectfont \textit{in partial fulfilment of the requirements for the degree of}\par}
    
    \vspace{0.4cm}
    {\fontsize{13}{16}\selectfont \textbf{BACHELOR OF TECHNOLOGY}\\\textbf{IN}\par}
    
    \vspace{0.2cm}
    {\fontsize{11}{14}\selectfont \textbf{\color{amritared} COMPUTER SCIENCE AND ENGINEERING/ COMPUTER SCIENCE AND\\ENGINEERING-ARTIFICIAL INTELLIGENCE}\par}
    
    \vspace{0.5cm}
    \amritaemblem[2.3cm]
    
    \vspace{0.1cm}
    {\fontsize{10}{12}\selectfont \textbf{\color{amritared} श्रद्धावान् लभते ज्ञानम्}\par}
    
    \vspace{0.3cm}
    {\fontsize{12}{15}\selectfont \textbf{SCHOOL OF COMPUTING\\AMRITA VISHWA VIDYAPEETHAM\\AMARAVATI -- 522503}\par}
    
    \vspace{0.4cm}
    {\fontsize{12}{15}\selectfont \textbf{\color{amritared} OCTOBER- 2026}\par}
\end{center}
\clearpage

% =========================================================================
% PAGE 2: CERTIFICATE (Exact Institutional Layout from Template Screenshot 2)
% =========================================================================
\thispagestyle{plain}
\begin{center}
    \amritaemblem[1.8cm]\\[4pt]
    {\fontsize{13}{16}\selectfont \textbf{\color{amritared}AMRITA VISHWA VIDYAPEETHAM}}\\[2pt]
    {\fontsize{12}{15}\selectfont \textbf{SCHOOL OF COMPUTING, AMARAVATI -- 522503}}\\[14pt]
    {\fontsize{13}{16}\selectfont \textbf{CERTIFICATE}}\\[14pt]
\end{center}

This is to certify that the project report entitled \textbf{\color{amritared}``A Contrastive Hybrid Federated Graph Neural Network Architecture with Leakage-Controlled Evaluation for IoT Intrusion Detection''} submitted by \textbf{\color{amritared}Student1 name (Roll no), Student2 name (Roll no), Student 3 name( Roll no) and Student4 name( Roll no)} in partial fulfillment of the requirements for the award of Degree \textbf{Bachelor of Technology in} \textbf{\color{amritared}Computer Science and Engineering/ Computer Science and Engineering-Artificial Intelligence} is a Bonafide record of the work carried out under our guidance and supervision at School of Computing, Amrita Vishwa Vidyapeetham, Amaravati.

\vspace{2.2cm}
\noindent
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l r}
\textbf{\color{amritared}Name of the Guide} & \textbf{Dr. M. Nageswara Rao} \\
B.Tech. Project Guide & Chairperson \\
\textbf{\color{amritared}Designation :} & School of Computing \\
School of Computing & \\
\end{tabular*}

\vspace{1.8cm}
\noindent\textbf{Project Review Panel:}
\begin{enumerate}[leftmargin=20pt, label=\arabic*.]
    \item \textcolor{crimson}{Name/designation/sign with date}
    \item \textcolor{crimson}{Name/designation/sign with date}
    \item \textcolor{crimson}{Name/designation/sign with date}
    \item \textcolor{crimson}{Name/designation/sign with date}
\end{enumerate}
\clearpage

% =========================================================================
% PAGE 3: ABSTRACT (Exact Institutional Layout from Template Screenshot 3)
% =========================================================================
\thispagestyle{plain}
\begin{center}
    {\fontsize{14}{17}\selectfont \textbf{ABSTRACT}}\\[12pt]
    \colorbox{yellow}{\textbf{MAXIMUM OF 250 WORDS}}\\[10pt]
    \textbf{WITH FONT SIZE 12}\\[16pt]
\end{center}

Network Intrusion Detection Systems (NIDS) deployed across Internet of Things (IoT) ecosystems face severe operational hurdles arising from decentralized edge topologies, acute class imbalance, and pervasive evaluation data leakage. Although Federated Graph Neural Networks (FedGNNs) offer a compelling framework for relational anomaly modeling without centralizing sensitive NetFlow records, standard architectures frequently suffer from catastrophic false-negative collapse on rare intrusion vectors under empirical risk minimization. In this dissertation, we propose a contrastive hybrid federated GNN architecture evaluated under a rigorous signature-grouped, zero-leakage protocol on the official NF-ToN-IoT benchmark. 

Our framework combines three domain-specialized Graph Attention Network (GAT) client models, Leiden community partitioning, community centroid pooling, an aggregated GraphSAGE server overlay, and Random Forest feature fusion. To overcome severe minority class degradation, we formulate a joint optimization objective uniting Class-Balanced Focal (CB-Focal) loss ($\beta=0.9999, \gamma=2.0$) with Supervised Contrastive (SupCon) representation regularization ($\mu = 0.1$), supported by dynamic class-balanced sampling ($M=64$) and intra-class edge interpolation. Across three independent random seeds on 1,377,837 NetFlow records, our proposed framework reduces Macro False Negative Rate (FNR) from $21.89 \pm 2.01\%$ to $5.72 \pm 1.20\%$, elevating Balanced Accuracy from $78.11 \pm 2.01\%$ to $94.28 \pm 1.20\%$. Crucially, contrastive metric regularization resolves a catastrophic topological collapse wherein $99.83\%$ of rare Backdoor attacks were misclassified as Injection flows by baseline GNNs, rescuing Backdoor detection recall from $0.11 \pm 0.08\%$ to $99.57 \pm 0.16\%$.

\vspace{12pt}
\noindent\textbf{Keywords:} Federated Learning, Graph Attention Networks, IoT Intrusion Detection, Supervised Contrastive Learning, Class Imbalance, Data Leakage, Leiden Community Detection.
\clearpage

% =========================================================================
% PAGE 4: DECLARATION (Exact Institutional Layout from Template Screenshot 4)
% =========================================================================
\thispagestyle{plain}
\begin{center}
    {\fontsize{14}{17}\selectfont \textbf{DECLARATION}}\\[18pt]
\end{center}

We the undersigned solemnly declare that the project report entitled \textbf{\color{amritared}<Title of the Project>} is based on our own work carried out during the course of our study under the guidance of \textbf{\color{amritared}Guide Name, Designation, Computer Science and Engineering/ Computer Science and Engineering-Artificial Intelligence}, and has not formed the basis for the award of any other degree or diploma, in this or any other Institution or University. In keeping with the ethical practice in reporting scientific information, due acknowledgement has been made wherever the findings of others have been cited.

\vspace{3.5cm}
\noindent
\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}l r}
Student name1 & Signature of the Student1 \\[1.2cm]
Student name2 & Signature of the Student2 \\[1.2cm]
Student name3 & Signature of the Student3 \\[1.2cm]
Student name4 & Signature of the Student4 \\
\end{tabular*}
\clearpage

% =========================================================================
% PAGE 5: ACKNOWLEDGEMENT (Exact Institutional Layout from Template Screenshot 5)
% =========================================================================
\thispagestyle{plain}
\begin{center}
    {\fontsize{14}{17}\selectfont \textbf{ACKNOWLEDGEMENT}}\\[16pt]
\end{center}

We would like to express our deep gratitude to our beloved chancellor \textbf{Sri Mata Amritanandamayi Devi AMMA} for providing the bright academic climate at this university, which has made entire project work possible. This acknowledgment is intended to thank all those people involved directly or indirectly with our project. We would like to thank the Board of Management for providing us with the necessary infrastructure required for the completion of the project. We would like to express our heartfelt gratitude to \textbf{Mr. M. S. Vijayendra}, \textit{Executive Director}, Amaravati Campus, \textbf{Prof. C. K. Jayashankar}, \textit{Associate Dean}, Amaravati Campus, \textbf{Prof. Shiva Pratap Gopakumar}, \textit{Principal}, Amaravati Campus and \textbf{Prof. M. Nageswara Rao}, \textit{Chairperson}, Amrita School of Computing, for their constant encouragement, guidance, and support, and all the faculty members of the School of Computing for their valuable guidance and support during our project work.

We wish to record our deep sense of gratitude and profound thanks to our project guide \textbf{\color{amritared}Guide Name, Designation}, Amrita School of Computing, for \textbf{\color{amritared}his / her} keen interest, inspiring guidance, constant encouragement with our work during all stages, to bring this project into fruition. We feel extremely grateful to \textbf{\color{amritared}<all Panel members Name, Designation>} for their feedback and encouragement which helped me to complete the project.

We would also like to thank the entire fraternity of the School of Computing. We would like to extend our sincere thanks to family and friends for helping and motivating us during the project work. Last but not the least, we thank blessings of supreme energy which made our project a success.

\vspace{2.2cm}
\begin{flushright}
\textbf{\color{amritared}STUDENT1 NAME}\\[6pt]
\textbf{\color{amritared}STUDENT2 NAME}\\[6pt]
\textbf{\color{amritared}STUDENT3 NAME}\\[6pt]
\textbf{\color{amritared}STUDENT4 NAME}
\end{flushright}
\clearpage

% =========================================================================
% PAGES 6 & 7: CONTENTS (Exact Institutional Layout from Template Screenshots 6 & 7)
% =========================================================================
\thispagestyle{plain}
\begin{center}
    {\fontsize{14}{17}\selectfont \textbf{CONTENTS}}\\[10pt]
\end{center}

\begin{center}
\renewcommand{\arraystretch}{1.28}
\begin{tabular}{|>{\centering\arraybackslash}p{2.2cm}|p{11.2cm}|>{\centering\arraybackslash}p{2.0cm}|}
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
\end{tabular}
\end{center}
\clearpage

% CONTENTS PAGE 2 (Screenshot 7)
\thispagestyle{plain}
\begin{center}
\renewcommand{\arraystretch}{1.22}
\begin{tabular}{|>{\centering\arraybackslash}p{2.2cm}|p{11.2cm}|>{\centering\arraybackslash}p{2.0cm}|}
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
\end{tabular}
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
\end{enumerate}
\clearpage

% =========================================================================
% PAGE 8: LIST OF TABLES
% =========================================================================
\thispagestyle{plain}
\addcontentsline{toc}{chapter}{List of Tables}
\listoftables
\clearpage

% =========================================================================
% PAGE 9: LIST OF FIGURES
% =========================================================================
\thispagestyle{plain}
\addcontentsline{toc}{chapter}{List of Figures}
\listoffigures
\clearpage

% =========================================================================
% PAGE 10: LIST OF ABBREVIATIONS
% =========================================================================
\thispagestyle{plain}
\begin{center}
    {\fontsize{14}{17}\selectfont \textbf{LIST OF ABBREVIATIONS}}\\[16pt]
\end{center}

\begin{table}[H]
\centering
\begin{tabular}{ll}
\toprule
\textbf{Abbreviation} & \textbf{Full Expansion} \\
\midrule
IoT & Internet of Things \\
IIoT & Industrial Internet of Things \\
NIDS & Network Intrusion Detection System \\
FL & Federated Learning \\
GNN & Graph Neural Network \\
GAT & Graph Attention Network \\
GraphSAGE & SAmple and aggreGatE Graph Convolutional Network \\
CB-Focal & Class-Balanced Focal Loss \\
SupCon & Supervised Contrastive Learning \\
ERM & Empirical Risk Minimization \\
FNR & False Negative Rate \\
FPR & False Positive Rate \\
Non-IID & Non-Independent and Identically Distributed \\
RFC & Request for Comments (Internet Engineering Task Force) \\
TCP & Transmission Control Protocol \\
IP & Internet Protocol \\
GPU & Graphics Processing Unit \\
VRAM & Video Random Access Memory \\
CUDA & Compute Unified Device Architecture \\
ROC-AUC & Receiver Operating Characteristic - Area Under Curve \\
PR-AUC & Precision-Recall Area Under Curve \\
SMOTE & Synthetic Minority Over-sampling Technique \\
MLP & Multi-Layer Perceptron \\
RF & Random Forest \\
TGN & Temporal Graph Network \\
Dir($\alpha$) & Dirichlet Distribution with concentration parameter $\alpha$ \\
\bottomrule
\end{tabular}
\end{table}
\clearpage
"""

    # Format Table 2.1
    table_2_1_tex = r"""
\begin{longtable}{|p{2.5cm}|p{2.8cm}|p{2.0cm}|p{4.2cm}|p{3.8cm}|}
\caption{Comprehensive Scholarly Survey of 15 Foundational and Contemporary Research Works in IoT Intrusion Detection.}\label{tab:lit_survey}\\
\hline
\textbf{Authors \& Year} & \textbf{Proposed Model} & \textbf{Benchmark Dataset} & \textbf{Key Empirical Findings} & \textbf{Critical Architectural Shortcoming} \\
\hline
\endfirsthead
\hline
\textbf{Authors \& Year} & \textbf{Proposed Model} & \textbf{Benchmark Dataset} & \textbf{Key Empirical Findings} & \textbf{Critical Architectural Shortcoming} \\
\hline
\endhead
\hline \multicolumn{5}{r}{\footnotesize Continued on next page\dots} \\
\endfoot
\hline
\endlastfoot
"""
    for row in text_ch2.LIT_TABLE_ROWS:
        authors, model, dataset, findings, shortcomings = row
        def clean(s):
            return s.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
        table_2_1_tex += f"{clean(authors)} & {clean(model)} & {clean(dataset)} & {clean(findings)} & {clean(shortcomings)} \\\\\n\\hline\n"
    table_2_1_tex += r"\end{longtable}"

    # Format Algorithm 4.2
    algo_4_2_tex = r"""
\begin{algorithm}[H]
\caption{Dynamic Class-Balanced Sampling and SupCon Loss Evaluation}\label{alg:dynamic_sampling}
\begin{algorithmic}[1]
\Require Client edge set $\mathcal{E}_k$, ground-truth labels $\mathcal{Y}_k$, samples per class $M=64$, temperature $\tau=0.07$, local model $\Theta^{(d)}$.
\Ensure Mini-batch loss $\mathcal{L}_{\text{batch}}$ and backpropagated gradients.
\State Initialize empty mini-batch edge index set $\mathcal{B} \gets \emptyset$.
\For{each class $c \in \{1, \dots, C\}$}
    \State Identify edge indices belonging to class $c$: $\mathcal{E}_c = \{e \in \mathcal{E}_k : y_e = c\}$.
    \If{$|\mathcal{E}_c| \ge M$}
        \State Sample $M$ edge indices uniformly at random without replacement from $\mathcal{E}_c$.
        \State $\mathcal{B} \gets \mathcal{B} \cup \text{Sample}(\mathcal{E}_c, M)$.
    \ElsIf{$|\mathcal{E}_c| > 0$}
        \State Sample all available instances $\mathcal{E}_c$.
        \State Synthesize remaining $M - |\mathcal{E}_c|$ virtual edges via intra-class interpolation:
        \State $\tilde{\mathbf{e}} = \lambda \mathbf{e}_i + (1 - \lambda) \mathbf{e}_j, \quad \lambda \sim \text{Beta}(0.5, 0.5), \quad i, j \in \mathcal{E}_c$.
        \State $\mathcal{B} \gets \mathcal{B} \cup \mathcal{E}_c \cup \{\tilde{\mathbf{e}}\}$.
    \EndIf
\EndFor
\State Extract node-pair representations $\{\mathbf{z}_i\}_{i \in \mathcal{B}}$ via forward pass through GAT encoder $\Theta^{(d)}$.
\State Normalize representations to unit hypersphere: $\tilde{\mathbf{z}}_i = \mathbf{z}_i / \|\mathbf{z}_i\|_2$.
\State Compute Class-Balanced Focal loss $\mathcal{L}_{\text{CB-Focal}}$ over sampled batch $\mathcal{B}$.
\State Compute Supervised Contrastive regularizer:
\State $\mathcal{L}_{\text{SupCon}} = \sum_{i \in \mathcal{B}} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(\tilde{\mathbf{z}}_i \cdot \tilde{\mathbf{z}}_p / \tau)}{\sum_{a \in A(i)} \exp(\tilde{\mathbf{z}}_i \cdot \tilde{\mathbf{z}}_a / \tau)}$.
\State Formulate joint objective: $\mathcal{L}_{\text{batch}} = \mathcal{L}_{\text{CB-Focal}} + \mu \, \mathcal{L}_{\text{SupCon}}$.
\State \Return $\mathcal{L}_{\text{batch}}$.
\end{algorithmic}
\end{algorithm}
"""

    # Process Chapters to add labels and insert tables/algorithms
    # Chapter 1
    ch1_processed = ch1_body
    ch1_processed = ch1_processed.replace(r"\chapter{Introduction}", r"\chapter{Introduction}\label{ch:intro}")
    ch1_processed = ch1_processed.replace(r"\section{Introduction (Background)}", r"\section{Introduction (Background)}\label{sec:background}")
    ch1_processed = ch1_processed.replace(r"\section{Problem Statement}", r"\section{Problem Statement}\label{sec:problem}")
    ch1_processed = ch1_processed.replace(r"\section{Objectives of the Dissertation}", r"\section{Objectives}\label{sec:objectives}")
    ch1_processed = ch1_processed.replace(r"\section{Research Contributions}", r"\section{Contributions}\label{sec:contributions}")

    # Chapter 2
    ch2_processed = ch2_body
    ch2_processed = ch2_processed.replace(r"\chapter{Literature Survey}", r"\chapter{Literature Survey}\label{ch:literature}")
    ch2_processed = ch2_processed.replace(r"\section{Comprehensive Survey}", r"\section{Comprehensive Survey}\label{sec:comprehensive_survey}")
    ch2_processed = ch2_processed.replace(
        r"\section{Summary and Findings of Survey in Tabular Format}",
        r"\section{Summary and Findings of 2.1 in Tabular format}\label{sec:lit_table}\n" + table_2_1_tex
    )
    ch2_processed = ch2_processed.replace(r"\section{Challenges in Graph-Based Federated Detection}", r"\section{Challenges}\label{sec:challenges}")
    ch2_processed = ch2_processed.replace(r"\section{Motivation of the Project Work}", r"\section{Motivation of the Project Work}\label{sec:motivation}")

    # Chapter 3
    ch3_processed = ch3_body
    ch3_processed = ch3_processed.replace(r"\chapter{Materials and Methods}", r"\chapter{Materials and Methods}\label{ch:materials}")
    ch3_processed = ch3_processed.replace(r"\section{Datasets Description}", r"\section{Datasets Description}\label{sec:datasets}")
    ch3_processed = ch3_processed.replace(r"\section{Methods of Data Processing and Pre-processing}", r"\section{Methods of Data Processing and Pre-processing}\label{sec:preprocessing}")
    ch3_processed = ch3_processed.replace(r"\section{Programming Tools and Simulation Framework}", r"\section{Programming Tools Details}\label{sec:tools}")

    # Chapter 4
    ch4_processed = ch4_body
    ch4_processed = ch4_processed.replace(r"\chapter{Methodology}", r"\chapter{Methodology}\label{ch:methodology}")
    ch4_processed = ch4_processed.replace(r"\section{Design / Methodology 1 of Existing Work (Centralized \& Standard FedNIDS)}", r"\section{Design / Methodology 1 of Existing Work}\label{sec:existing1}")
    ch4_processed = ch4_processed.replace(r"\section{Design / Methodology 2 of Existing Work (Base FedGATSage Framework)}", r"\section{Design / Methodology 2 of Existing Work}\label{sec:existing2}")
    ch4_processed = ch4_processed.replace(r"\section{Proposed Architecture}", r"\section{Proposed Architecture}\label{sec:proposed_arch}")
    ch4_processed = ch4_processed.replace(r"\section{Proposed Design / Detailed Methodology Formulations}", r"\section{Proposed Design / Methodology}\label{sec:proposed_method}")
    ch4_processed = ch4_processed.replace(
        r"\section{Proposed Execution Algorithms and Procedural Flowchart}",
        r"\section{Proposed Complete Flowchart}\label{sec:flowchart}\n" + algo_4_2_tex
    )

    # Chapter 5
    ch5_processed = ch5_body
    ch5_processed = ch5_processed.replace(r"\chapter{Results and Discussion}", r"\chapter{Results and Discussion}\label{ch:results}")
    ch5_processed = ch5_processed.replace(r"\section{Experimental Setup and Evaluation Protocol}", r"\section{Experimental Setup}\label{sec:setup}")
    ch5_processed = ch5_processed.replace(r"\section{Qualitative Results (Manifold Disentanglement and Heatmaps)}", r"\section{Qualitative Results}\label{sec:qualitative}")
    ch5_processed = ch5_processed.replace(r"\section{Quantitative Results (Multi-Seed Benchmark Verification)}", r"\section{Quantitative Results}\label{sec:quantitative}")
    ch5_processed = ch5_processed.replace(r"\section{Discussion and Limitations}", r"\section{Discussion}\label{sec:discussion}")

    # Chapter 6
    ch6_processed = ch6_body
    ch6_processed = ch6_processed.replace(r"\chapter{Conclusion and Future Directions}", r"\chapter{Conclusion and Future Directions}\label{ch:conclusion}")
    ch6_processed = ch6_processed.replace(r"\section{Conclusion}", r"\section{Conclusion}\label{sec:conclusion_summary}")
    ch6_processed = ch6_processed.replace(r"\section{Future Directions}", r"\section{Future Directions}\label{sec:future_directions}")

    # Back matter
    bib_processed = r"\clearpage\addcontentsline{toc}{chapter}{References}\label{ch:references}" + "\n" + bib_body
    back_processed = back_body.replace(r"% LIST OF PUBLICATIONS", r"\clearpage\label{sec:publications}% LIST OF PUBLICATIONS")
    back_processed = back_processed.replace(r"% PLAGIARISM AND AI INTEGRITY COMPLIANCE REPORT", r"\clearpage\label{sec:plagiarism}% PLAGIARISM AND AI INTEGRITY COMPLIANCE REPORT")

    full_tex = (
        preamble +
        front_matter +
        ch1_processed +
        ch2_processed +
        ch3_processed +
        ch4_processed +
        ch5_processed +
        ch6_processed +
        bib_processed +
        back_processed +
        "\n\\end{document}\n"
    )

    with open(r"C:\Users\musun\.gemini\antigravity-ide\scratch\FED_GNN\dissertation_overleaf.tex", "w", encoding="utf-8") as f:
        f.write(full_tex)

    print("dissertation_overleaf.tex built successfully!")
    print(f"Total characters: {len(full_tex)}")
    print(f"Total lines: {len(full_tex.splitlines())}")
    print(f"Total words: {len(full_tex.split())}")

if __name__ == "__main__":
    build_full_latex()
