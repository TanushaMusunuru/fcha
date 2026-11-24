# text_ch1.py
# Chapter 1: Introduction

CHAPTER_1_TITLE = "INTRODUCTION"

SEC_1_1_TITLE = "1.1 Introduction (Background)"
SEC_1_1_PARAS = [
    (
        "The exponential proliferation of Internet of Things (IoT) technologies and cyber-physical systems has "
        "radically transformed global computing infrastructure across critical sectors including industrial supervisory control, "
        "smart electrical power distribution grids, intelligent healthcare patient telemetry, urban municipal transport management, "
        "and connected defense installations. Contemporary operational networks no longer consist of homogenous enterprise workstations "
        "situated behind well-defined physical network perimeters. Instead, modern edge architectures incorporate billions of heterogeneous, "
        "spatially dispersed edge nodes ranging from ultra-low-power microcontrollers and environmental field sensors to programmable logic "
        "controllers (PLCs), edge cellular gateways, and embedded industrial robotic endpoints. While this distributed paradigm provides "
        "unprecedented operational visibility, automation, and real-time telemetry processing, it simultaneously expands the attack surface "
        "of enterprise networks to unprecedented dimensions."
    ),
    (
        "Unlike conventional data-center servers equipped with dedicated hardware security modules, multi-core processing engines, and "
        "continuous administrative oversight, IoT edge devices operate under severe physical and architectural constraints. These devices "
        "possess limited computational throughput, restricted memory capacities (frequently measured in kilobytes or megabytes), constrained "
        "battery reserves, and intermittent wireless connectivity over lossy communication channels. Furthermore, the extensive firmware "
        "heterogeneity and prolonged deployment lifecycles of IoT hardware severely impede standard software maintenance practices. Edge devices "
        "frequently operate with outdated cryptographic libraries, hardcoded vendor credentials, and unpatched operating system vulnerabilities, "
        "transforming them into lucrative targets for adversarial exploitation."
    ),
    (
        "The threat landscape confronting IoT networks is marked by an alarming evolution in adversarial sophistication. Modern cyber "
        "adversaries routinely execute coordinated, multi-stage campaigns that exploit decentralized topologies. Botnets such as Mirai, "
        "Mozi, and their contemporary variants systematically compromise thousands of insecure edge nodes via automated vulnerability scanning "
        "and credential brute-forcing, weaponizing them into distributed denial-of-service (DDoS) reflection armies capable of generating "
        "terabits-per-second of disruptive traffic. Simultaneously, state-sponsored Advanced Persistent Threat (APT) groups deploy stealthy "
        "backdoor command-and-control (C2) channels and credential theft mechanisms to achieve silent administrative privilege escalation and "
        "lateral network traversal within industrial operational technology (OT) environments."
    ),
    (
        "To safeguard connected networks against these persistent threats, Network Intrusion Detection Systems (NIDS) serve as an indispensable "
        "defensive layer. Traditional NIDS architectures rely predominantly on centralized data ingestion models. In these legacy frameworks, "
        "distributed edge gateways and packet sensors are tasked with continuously capturing raw packet payloads (PCAP) or aggregate NetFlow/IPFIX "
        "flow records and forwarding this voluminous telemetry across wide-area networks to a centralized Security Operations Center (SOC) or cloud-hosted "
        "analytics platform. Within the centralized repository, machine learning and deep learning models process aggregated telemetry in batch mode "
        "to identify anomalous patterns and signature deviations."
    ),
    (
        "However, the centralized NIDS paradigm is rendered fundamentally unviable by the operational realities of modern IoT ecosystems. "
        "First, continuous transmission of multi-gigabyte traffic telemetry from millions of edge endpoints introduces prohibitive communication "
        "bandwidth overhead and induces severe congestion across wireless backhaul links, directly depleting the limited energy reserves of "
        "battery-powered sensor gateways. Second, centralized ingestion introduces unacceptable processing latencies, preventing timely detection "
        "and automated mitigation of volumetric denial-of-service surges or rapid worm propagation in safety-critical industrial loops. Third, "
        "centralizing internal enterprise telemetry creates a monolithic single point of failure and an extraordinarily high-value target for "
        "adversarial surveillance."
    ),
    (
        "Most critically, transmitting raw packet captures and granular flow records across institutional boundaries directly breaches stringent "
        "international data privacy regulations and organizational data sovereignty mandates. Contemporary regulatory frameworks—such as the "
        "European Union General Data Protection Regulation (GDPR), the Health Insurance Portability and Accountability Act (HIPAA), and the California "
        "Consumer Privacy Act (CCPA)—strictly penalize the unauthorized centralization and exposure of personally identifiable information (PII) "
        "and internal network architectural metadata. Raw NetFlow records reveal internal IP addressing schemes, subnet segmentation policies, "
        "service port architectures, user communication timelines, and payload metadata, exposing institutions to severe legal penalties and "
        "confidentiality breaches."
    ),
    (
        "Federated Learning (FL) has emerged as a revolutionary paradigm to resolve the fundamental conflict between collaborative threat "
        "intelligence and decentralized data privacy. Formulated by McMahan et al. in 2017, federated learning enables a consortium of decentralized "
        "edge clients to collaboratively train a shared global model while retaining all raw training telemetry strictly on local storage. In a "
        "federated intrusion detection workflow, local edge gateways optimize local model parameters over private traffic captures and transmit "
        "only parameterized model weights or gradient updates to a central federated aggregation server. The server combines these local parameters "
        "via algorithms such as Federated Averaging (FedAvg) to synthesize an updated global consensus model, which is subsequently redistributed "
        "to participating clients for local inference."
    ),
    (
        "Simultaneously, the cybersecurity research community has increasingly recognized that network communication events are inherently "
        "relational and topological rather than isolated, independent tabular records. Traditional machine learning approaches treat network "
        "telemetry as flat tabular vectors, ignoring the underlying graph structure of network conversations. However, network intrusions—including "
        "distributed denial-of-service, multi-target port scanning, botnet beaconing, and lateral movement—exhibit explicit relational topologies "
        "governed by source-destination IP interactions, communication density, and multi-hop routing paths. Graph Neural Networks (GNNs), such as "
        "Graph Convolutional Networks (GCNs), Graph Attention Networks (GATs), and GraphSAGE, provide an expressive mathematical foundation to model "
        "network interactions by representing IP hosts as graph vertices and directional communication flows as attributed edges, capturing complex "
        "topological dependencies that completely elude non-relational statistical classifiers."
    )
]

SEC_1_2_TITLE = "1.2 Problem Statement"
SEC_1_2_PARAS = [
    (
        "Despite the compelling theoretical promise of combining Federated Learning with Graph Neural Networks for decentralized cybersecurity, "
        "existing Federated Graph Neural Network (FedGNN) architectures exhibit four severe operational pathologies and pervasive methodological "
        "vulnerabilities that critically compromise their real-world efficacy:"
    )
]
SEC_1_2_BULLETS = [
    (
        "Pervasive Socket-Signature Evaluation Data Leakage in Academic Benchmarks: ",
        "A critical vulnerability in contemporary intrusion detection literature is the pervasive reliance on naive uniform random row partitioning "
        "during experimental evaluation. In real-world enterprise NetFlow telemetry, repeated packets belonging to the same application session or "
        "automated intrusion burst share identical communication socket signatures—defined by source IP, destination IP, Layer 4 service ports, "
        "transport protocol, and flow volume attributes. When benchmarks apply standard random row splits, flows originating from the exact same "
        "socket conversation are simultaneously distributed across both training and testing folds. Classifiers evaluated under this compromised "
        "setup achieve artificially inflated detection accuracy (>99%) by simply memorizing static socket tuples, masking catastrophic failure "
        "when deployed against authentic, previously unseen network sessions."
    ),
    (
        "Catastrophic Minority Class Collapse Under Empirical Risk Minimization: ",
        "Real-world network traffic distributions are characterized by acute, long-tail class imbalance. Benign background transactions and "
        "high-volume volumetric attacks (such as DDoS and Injection) outnumber critical targeted intrusions (such as stealthy Backdoors and administrative "
        "password guessing) by multiple orders of magnitude (exceeding a 27:1 ratio in benchmarks like NF-ToN-IoT). Under standard cross-entropy loss "
        "optimized via empirical risk minimization, gradient update trajectories are overwhelmingly dictated by majority-class sample volumes. "
        "Consequently, the decision boundaries of rare minority attacks are completely subsumed by adjacent majority manifolds, precipitating "
        "intolerable False Negative Rates (FNR) exceeding 99% on the most damaging and stealthy network intrusions."
    ),
    (
        "Topological Feature Blurring and Oversmoothing on Multi-Role Endpoint Nodes: ",
        "In graph representations of enterprise network telemetry, IP endpoint nodes routinely serve dual operational roles, concurrently participating "
        "in legitimate high-volume transactions and rare malicious flow exchanges. Standard GNN message-passing formulations initialize node representations "
        "by computing the mean of all incident flow attributes. When low-volume stealth attacks (such as a C2 backdoor) traverse an endpoint that "
        "simultaneously handles massive volumes of background or web injection traffic, recursive neighborhood feature averaging severely dilutes "
        "and erases the subtle minority attack signature into the dominant host profile. This topological oversmoothing causes continuous edge embeddings "
        "to collapse entirely into adjacent majority clusters."
    ),
    (
        "Structural Incoherence from Disconnected Heuristic Graph Partitions: ",
        "Prior federated graph frameworks rely on heuristic community detection algorithms, notably the Louvain modularity optimization algorithm, "
        "to cluster client graphs and abstract topology before server transmission. However, Louvain relies on greedy local node moves that "
        "frequently trap community discovery in suboptimal local maxima, mathematically generating internally disconnected or arbitrarily poorly connected "
        "community subgraphs. Transmitting the centroids of disconnected community artifacts to a federated server overlay introduces substantial "
        "structural noise, degrading the stability and convergence of cross-client GraphSAGE aggregation."
    )
]

SEC_1_3_TITLE = "1.3 Objectives of the Dissertation"
SEC_1_3_PARAS = [
    (
        "To comprehensively overcome the technical vulnerabilities identified above, this dissertation develops, audits, and validates a "
        "contrastive hybrid federated Graph Neural Network framework engineered specifically for highly imbalanced IoT network intrusion detection. "
        "The primary engineering and scientific objectives of this research are formulated as follows:"
    )
]
SEC_1_3_OBJS = [
    (
        "Formulation of an Audited Zero-Leakage Benchmark Protocol: ",
        "Establish and mathematically verify a rigorous 5-fold StratifiedGroupKFold evaluation protocol grouped by an 8-feature socket communication "
        "signature across 1,377,837 NetFlow records of the official NF-ToN-IoT benchmark, proving absolute 0.00% signature overlap between training "
        "and testing folds to eliminate evaluation leakage."
    ),
    (
        "Engineering of Domain-Specialized Client GAT Subgraphs: ",
        "Design and construct three dedicated, domain-specialized Graph Attention Network (GAT) client detectors—Temporal GAT, Content GAT, and "
        "Behavioral GAT—capable of isolating dynamic flow duration, payload volumetric asymmetry, and port protocol behaviors without inter-feature "
        "interference."
    ),
    (
        "Integration of Leiden Constant Potts Model Community Partitioning: ",
        "Incorporate the Leiden community detection algorithm optimizing the Constant Potts Model (CPM) quality function into client graph pipelines, "
        "mathematically guaranteeing that all discovered community subgraphs are strictly connected, robust, and topologically sound for server abstraction."
    ),
    (
        "Formulation of Supervised Contrastive Metric Regularization (SupCon): ",
        "Formulate a joint multi-task optimization objective uniting Class-Balanced Focal (CB-Focal) loss (beta=0.9999, gamma=2.0) with Supervised "
        "Contrastive (SupCon) representation regularization (mu=0.1, tau=0.07) directly on normalized edge embeddings, mathematically driving "
        "active metric repulsion between overlapping attack manifolds."
    ),
    (
        "Implementation of Multi-Tiered Class Balancing Strategies: ",
        "Incorporate client-local intra-class convex edge interpolation (Mixup along flow feature dimensions with Beta distribution) and a dynamic "
        "class-balanced batch sampler guaranteeing M=64 samples per class per step, stabilizing the optimization landscape under extreme imbalance."
    ),
    (
        "Design of a Two-Stage Random Forest Meta-Learner: ",
        "Develop an ensemble Random Forest meta-classifier that arbitrates conflicting continuous GNN detector output probabilities by combining them "
        "with normalized raw physical NetFlow attribute thresholds."
    ),
    (
        "Multi-Seed Statistical Replication and Diagnostic Auditing: ",
        "Rigorously evaluate and verify the proposed framework across three independent random initialization seeds (42, 43, 44) on NF-ToN-IoT and five "
        "seeds (42 to 46) on NF-UNSW-NB15, establishing reproducible empirical evidence and isolating the exact topological mechanism responsible for minority recovery."
    )
]

SEC_1_4_TITLE = "1.4 Research Contributions"
SEC_1_4_PARAS = [
    (
        "This dissertation delivers five major scientific and technological contributions to the fields of federated learning, graph representation "
        "learning, and network security:"
    )
]
SEC_1_4_CONTRIBS = [
    (
        "1. Audited Zero-Leakage Benchmark Methodology: ",
        "We conduct an empirical audit of prevailing NIDS evaluation practices, demonstrating that standard random row partitioning induces a massive "
        "46.88% identical signature leakage in the NF-ToN-IoT benchmark. We establish an audited 8-tuple StratifiedGroupKFold protocol that achieves "
        "strictly 0.00% leakage, providing the first authentic, leakage-controlled baseline for relational intrusion detection."
    ),
    (
        "2. Resolution of Minority Class Collapse via Supervised Contrastive Regularization: ",
        "We formulate an architectural Supervised Contrastive loss mechanism (mu=0.1) operating on normalized edge embeddings within local GAT encoders. "
        "We prove mathematically and empirically that contrastive metric repulsion counteracts the overwhelming 27:1 gradient dominance of Injection over "
        "Backdoor flows, completely resolving a catastrophic collapse wherein baseline GNNs misclassified 99.83% of Backdoor intrusions as Injection."
    ),
    (
        "3. Multi-Tiered Class Balancing and Manifold Interpolation: ",
        "We unite effective sample volume theory (CB-Focal loss with beta=0.9999, gamma=2.0), dynamic class-balanced mini-batch sampling (M=64 edges per class), "
        "and client-local convex edge interpolation (ratio=0.50), smoothing decision boundaries and stabilizing multi-seed optimization under non-IID conditions."
    ),
    (
        "4. Hybrid Federated Graph-Tabular Pipeline with 85% Communication Reduction: ",
        "We realize an integrated system architecture combining three specialized client GAT detectors, Leiden community partitioning, an aggregated "
        "GraphSAGE server overlay (top-k cosine similarity), and a downstream Random Forest meta-classifier. Community abstraction compresses client telemetry "
        "by 85% (reducing transmission from ~25 KB to 3.2 KB per round) while preserving structural attack context."
    ),
    (
        "5. Rigorous Multi-Seed Empirical and Diagnostic Validation: ",
        "Across three independent random seeds on 1,377,837 NetFlow records, our proposed framework reduces Macro FNR from 21.89 ± 2.01% to 5.72 ± 1.20% "
        "and elevates Balanced Accuracy from 78.11 ± 2.01% to 94.28 ± 1.20%, rescuing Backdoor recall from 0.11% to 99.57%. We provide empirical ablation "
        "isolating the host node dilution mechanism and confirm cross-dataset dynamics across five seeds on NF-UNSW-NB15."
    )
]

SEC_1_5_TITLE = "1.5 Organization of the Report"
SEC_1_5_PARAS = [
    (
        "The remainder of this dissertation is systematically structured into five subsequent chapters:\n\n"
        "• Chapter 2 (Literature Survey) provides an exhaustive scholarly review of foundational and contemporary literature spanning federated learning, "
        "graph neural networks for cybersecurity, mathematical loss formulations for class imbalance, and contrastive representation learning. It presents "
        "a structured comparative table of 15 benchmark studies, identifies critical technical bottlenecks, and articulates the project motivation.\n\n"
        "• Chapter 3 (Materials and Methods) details the NF-ToN-IoT and NF-UNSW-NB15 benchmark datasets, the NetFlow V9 attribute dictionary, RFC 793 bitwise "
        "TCP flag decoding, specialized feature engineering, graph topological formulation, the zero-leakage 8-tuple grouped split protocol, and programming tools.\n\n"
        "• Chapter 4 (Methodology) presents an in-depth examination of existing baselines (centralized models and base FedGATSage), followed by the complete "
        "formulation of our proposed contrastive hybrid federated architecture. It includes full mathematical derivations of specialized GATs, Leiden CPM "
        "partitioning, CB-Focal loss, SupCon gradient dynamics, server GraphSAGE overlay, two-stage Random Forest fusion, algorithmic specifications, and system flowcharts.\n\n"
        "• Chapter 5 (Results and Discussion) delivers comprehensive empirical findings across multi-seed runs, qualitative manifold visualizations, full "
        "confusion matrix diagnostics, headline metric tables, mathematical gain decomposition, systematic ablation progressions, node-averaging hypothesis testing, "
        "cross-dataset validation on NF-UNSW-NB15, and deep discussions on gradient mechanics, privacy trade-offs, and threats to validity.\n\n"
        "• Chapter 6 (Conclusion and Future Directions) summarizes the achieved scientific milestones, key empirical takeaways, and outlines four concrete "
        "future research trajectories extending this work toward adaptive temperature scheduling, zero-day subnet transfer, formal differential privacy, "
        "and hardware-in-the-loop edge deployment."
    )
]
