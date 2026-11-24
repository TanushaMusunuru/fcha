# text_ch2.py
# Chapter 2: Literature Survey

CHAPTER_2_TITLE = "LITERATURE SURVEY"

SEC_2_1_TITLE = "2.1 Comprehensive Survey"
SEC_2_1_PARAS = [
    (
        "Network Intrusion Detection Systems (NIDS) operating within distributed Internet of Things (IoT) ecosystems "
        "have evolved through multiple distinct paradigms over the past two decades. Modern intrusion detection sits at the convergence "
        "of four major foundational domains: decentralized federated learning protocols, graph representation learning for network "
        "telemetry, optimization and loss formulation for acute class imbalance, and metric representation learning via contrastive objectives. "
        "This section delivers a comprehensive, rigorous examination of foundational literature and state-of-the-art developments across each of these pillars."
    )
]

SUBSEC_2_1_1_TITLE = "2.1.1 Classical Machine Learning and Deep Learning in Intrusion Detection"
SUBSEC_2_1_1_PARAS = [
    (
        "Early research in automated network intrusion detection focused predominantly on signature-based matching algorithms and classical "
        "shallow machine learning classifiers. Signature-based systems (e.g., Snort, Suricata) inspect packet payloads against curated databases "
        "of known malicious patterns. While computationally efficient for well-characterized attacks, signature engines are fundamentally incapable "
        "of detecting zero-day exploits, polymorphism, or obfuscated network behaviors. To achieve generalized anomaly detection, researchers turned "
        "to statistical machine learning models trained on network flow telemetry, notably Random Forests (Breiman, 2001), Support Vector Machines (SVMs), "
        "and k-Nearest Neighbors (k-NN)."
    ),
    (
        "Random Forest classifiers, in particular, demonstrated outstanding performance across historical cybersecurity benchmarks such as KDD-Cup 99 "
        "and NSL-KDD. By constructing ensembles of unpruned decision trees over bootstrap samples and evaluating random feature subsets at each split, "
        "Random Forests exhibit remarkable resilience to tabular noise and establish sharp, non-linear decision thresholds along orthogonal continuous "
        "dimensions. However, classical shallow classifiers rely heavily on manual feature engineering and require all training records to be centralized "
        "within a single computing repository, conflicting with data privacy constraints in multi-tenant enterprise networks."
    ),
    (
        "With the advent of deep learning, researchers explored deep feedforward networks, Deep Autoencoders, Convolutional Neural Networks (CNNs), "
        "and Recurrent Neural Networks (RNNs), including Long Short-Term Memory (LSTM) and Gated Recurrent Units (GRUs), for cyber telemetry analysis. "
        "Deep Autoencoders reconstruct benign traffic patterns and flag high reconstruction errors as anomalies, whereas LSTMs model the temporal progression "
        "of packet inter-arrival times. Nevertheless, these deep learning architectures continue to treat network telemetry as flat, independent, and "
        "identically distributed (IID) tabular vectors. They remain fundamentally blind to the underlying topological relationships between network "
        "hosts, unable to correlate multi-point reconnaissance with subsequent lateral movement across enterprise subnets."
    )
]

SUBSEC_2_1_2_TITLE = "2.1.2 Federated Learning Paradigms in Network Security"
SUBSEC_2_1_2_PARAS = [
    (
        "To reconcile collaborative threat intelligence with strict data privacy mandates (such as GDPR and HIPAA), Federated Learning (FL) "
        "was introduced by McMahan et al. (2017) through the canonical Federated Averaging (FedAvg) algorithm. In FedAvg, a global coordination server "
        "maintains a shared model parameter vector. Across iterative communication rounds, a subset of decentralized client nodes downloads the global "
        "parameters, performs local stochastic gradient descent (SGD) over private data partitions, and transmits the resulting parameter deltas back "
        "to the server. The server aggregates local updates proportionally to each client's dataset volume: W_{t+1} = sum_{k=1}^K (n_k / n) W_{t+1}^k. "
        "By transmitting model parameters rather than raw packet captures, FedAvg significantly reduces raw bandwidth overhead and prevents the direct "
        "exposure of sensitive internal network metadata."
    ),
    (
        "Despite its privacy advantages, deploying federated learning across edge IoT environments introduces severe statistical challenges stemming "
        "from non-independent and identically distributed (non-IID) data distributions. Zhao et al. (2018) provided foundational theoretical and "
        "empirical evidence demonstrating that statistical divergence between client data distributions introduces significant weight drift during "
        "local training rounds. As client parameter trajectories diverge, standard FedAvg aggregation produces sub-optimal global consensus models, "
        "substantially slowing convergence rates and degrading overall accuracy. Li et al. (2020) analyzed optimization challenges under system and "
        "statistical heterogeneity, proposing FedProx, which introduces an explicit proximal regularization term (mu / 2) ||W - W_t||^2 to constrain "
        "local parameter drift relative to the global model."
    ),
    (
        "In network intrusion detection contexts, statistical heterogeneity is exacerbated by the highly specialized nature of IoT deployments. "
        "An edge gateway supervising environmental industrial sensors experiences a traffic profile radically different from an administrative edge "
        "router handling corporate communications. Specific attack categories—such as specialized SCADA command injection or industrial backdoor "
        "beacons—may be observed exclusively by a single client while remaining completely absent from other nodes. To combat this extreme class absence, "
        "Youm and Kim (2025) proposed DS-FedIDS, employing class-specific dynamic sampling techniques to adjust client loss weighting based on local "
        "class distributions. Similarly, Hsu et al. (2019) demonstrated that Dirichlet distribution modeling Dir(alpha) accurately captures extreme "
        "non-IID partitioning in federated benchmarks. However, standard federated intrusion detection architectures remain vulnerable when minority "
        "attack classes are non-uniformly distributed among participating clients."
    )
]

SUBSEC_2_1_3_TITLE = "2.1.3 Graph Neural Networks for Relational Network Telemetry"
SUBSEC_2_1_3_PARAS = [
    (
        "Recognizing that cyber attacks are inherently relational events executed over structured communication topologies, the security community "
        "has increasingly embraced Graph Neural Networks (GNNs). Unlike Euclidean convolutional networks designed for regular grids (e.g., images), "
        "GNNs operate over arbitrary non-Euclidean graphs G = (V, E) by executing recursive neighborhood message-passing convolutions. In network security "
        "formulations, unique IP addresses represent vertices V, while communication flows represent directed edges E connecting interacting endpoints."
    ),
    (
        "Veličković et al. (2018) introduced Graph Attention Networks (GAT), which revolutionized representation learning on graphs by incorporating "
        "self-attention mechanisms into node convolutions. Rather than assigning static or degree-normalized weights to adjacent vertices (as in Graph "
        "Convolutional Networks, Kipf and Welling, 2016), GAT computes dynamic attention coefficients alpha_{uv} that quantify the relative importance "
        "of node v's features to node u. This self-attentive weighting enables GAT to dynamically prioritize suspicious, bursty communication channels "
        "while down-weighting routine benign background transactions."
    ),
    (
        "To enable scalable inductive representation learning over massive, dynamically expanding graphs, Hamilton et al. (2017) formulated GraphSAGE. "
        "Instead of operating over the full graph Laplacian matrix, GraphSAGE samples a fixed-size local neighborhood for each target node and aggregates "
        "representations via learnable pooling functions (e.g., mean, LSTM, or max pooling). GraphSAGE's inductive capability enables it to generate "
        "meaningful embeddings for previously unseen IP hosts without requiring retraining over the entire network topology."
    ),
    (
        "Several researchers have tailored GNN architectures specifically to edge-attributed network telemetry. Lo et al. (2022) developed E-GraphSAGE, "
        "extending GraphSAGE to accommodate edge attributes directly by embedding directional flow features into the message-passing phase. Chang and "
        "Branco (2021) formulated E-ResGAT, integrating residual skip connections into graph attention networks to preserve edge-level statistical "
        "attributes across deep message-passing layers and prevent oversmoothing on high-degree nodes. Han et al. (2025) formulated FedSTGCN, uniting "
        "federated learning with spatiotemporal graph convolutions to capture temporal packet bursts and relational topology simultaneously across IoT "
        "sensor gateways. A comprehensive survey by Liu et al. (2024) systematically categorized federated GNN frameworks, emphasizing that structural "
        "heterogeneity, scalability, and acute class imbalance remain unresolved bottlenecks in decentralized graph learning."
    )
]

SUBSEC_2_1_4_TITLE = "2.1.4 Class Imbalance and Optimization Loss Formulations"
SUBSEC_2_1_4_PARAS = [
    (
        "Network intrusion benchmarks are notoriously characterized by extreme class imbalance. Benign background transactions typically constitute "
        "80% to 90% of total logged traffic, volumetric denial-of-service and web injection attacks occupy moderate proportions (10% to 20%), while critical "
        "targeted intrusions—such as stealthy Backdoors, administrative Password guessing, and Shellcode exploits—represent less than 1.5% of total recorded "
        "events (Sarhan et al., 2021; Alsaedi et al., 2020). Johnson and Khoshgoftaar (2019) surveyed deep learning techniques for imbalanced domains, "
        "proving mathematically that standard empirical risk minimization under unweighted Cross-Entropy loss heavily biases parameter optimization toward "
        "majority classes. In unweighted optimization, gradient updates from massive majority classes completely overwhelm the sparse gradients generated "
        "by rare intrusions, causing high False Negative Rates (FNR) on critical security anomalies."
    ),
    (
        "To address class imbalance without discarding valuable majority data via random undersampling, researchers have investigated loss re-weighting "
        "and focal modulation strategies. Lin et al. (2017) formulated Focal Loss, introducing a dynamic modulating factor (1 - p_t)^gamma to standard "
        "cross-entropy: L_{FL} = - (1 - p_t)^gamma log(p_t). When an instance is well-classified (p_t -> 1, typical for easy majority benign flows), "
        "the modulating factor approaches zero, exponentially suppressing its contribution to the gradient. Consequently, optimization focuses "
        "predominantly on ambiguous boundary instances and hard-to-classify minority samples."
    ),
    (
        "Cui et al. (2019) introduced Class-Balanced Loss based on effective sample volume theory. Cui et al. proved that as sample volume increases, the "
        "marginal information gain of additional instances diminishes exponentially due to data overlap in the feature space. By defining the effective "
        "number of samples as E_n = (1 - beta^n) / (1 - beta) (where beta in [0, 1) represents a volume hyperparameter), Cui et al. designed class-balancing "
        "weights that scale inversely with effective sample space rather than raw counts: alpha_c proportional to (1 - beta) / (1 - beta^{n_c}). This prevents "
        "massive majority classes from dominating optimization while preventing the over-penalization of moderate classes. At the data level, Zhang et al. (2018) "
        "introduced Mixup, which synthesizes virtual training instances via convex feature interpolations: x_tilde = lambda x_i + (1 - lambda) x_j. "
        "Interpolating features regularizes deep neural networks, promoting linear behavior in intermediate representations and smoothing decision margins."
    )
]

SUBSEC_2_1_5_TITLE = "2.1.5 Contrastive Representation Learning"
SUBSEC_2_1_5_PARAS = [
    (
        "Contrastive representation learning establishes embedding spaces by explicitly pulling representations of semantically similar instances together "
        "while pushing dissimilar instances apart. In self-supervised learning, contrastive frameworks (e.g., SimCLR, Chen et al., 2020; MoCo, He et al., 2020) "
        "construct positive pairs through stochastic data augmentations of the same unlabeled instance, while treating all other instances in a mini-batch as negatives."
    ),
    (
        "Khosla et al. (2020) proposed Supervised Contrastive Learning (SupCon), extending contrastive representation learning to fully labeled datasets. "
        "In SupCon, all instances sharing the same ground-truth class label within a mini-batch are treated as mutual positive anchors, while instances from "
        "differing classes serve as mutual negatives. Khosla et al. demonstrated that SupCon achieves superior angular separation between class manifolds, "
        "exhibits greater robustness to label corruption, and eliminates the hyperparameter sensitivity associated with standard cross-entropy training. "
        "However, despite its extraordinary success in computer vision, the integration of Supervised Contrastive learning as an architectural regularizer "
        "within federated graph neural networks to combat topological oversmoothing on imbalanced NetFlow telemetry represents an unaddressed research frontier."
    )
]

SUBSEC_2_1_6_TITLE = "2.1.6 Critical Re-Examination and Audit of the Base FedGATSage Framework"
SUBSEC_2_1_6_PARAS = [
    (
        "Our investigation takes as its foundational baseline the FedGATSage architecture recently proposed by Al-Tfaily et al. (2025) in Nature Scientific "
        "Reports (vol. 15, no. 1, p. 41264). FedGATSage introduced a hybrid federated architecture combining client-side Graph Attention Networks (GAT), "
        "Louvain community detection, an aggregated server GraphSAGE overlay, and an ensemble Random Forest meta-classifier. While Al-Tfaily et al. "
        "reported an aggregate Balanced Accuracy of 78.58% and Macro FNR of 22.34% on NF-ToN-IoT, our extensive code-level audit revealed two critical "
        "structural vulnerabilities and unaddressed methodological pathologies:"
    ),
    (
        "1. Catastrophic Minority Class Collapse Under Empirical Risk Minimization: In the base FedGATSage pipeline, local client GAT models are trained "
        "strictly using unweighted Cross-Entropy loss. Our multi-seed empirical replication on the official NF-ToN-IoT benchmark revealed that the reported "
        "22.34% Macro FNR is driven almost entirely by the near-total collapse of rare attack classes. Specifically, for the stealthy Backdoor class "
        "(3,436 test flows), the baseline anchor achieves an appalling recall of only 0.11 ± 0.08% across three random seeds. Confusion matrix auditing "
        "revealed that 99.83% (3,430 out of 3,436) of Backdoor flows are erroneously classified as Injection traffic. Because Injection outnumbers Backdoor "
        "by 27:1 in training (374,831 vs. 13,797 flows), cross-entropy gradient descent allows the Injection class manifold to swallow the Backdoor boundary."
    ),
    (
        "2. Evaluation Data Leakage in Benchmark Row Splitting: In the published FedGATSage study, the experimental evaluation utilized a naive uniform "
        "random row split of NetFlow records. Our empirical leakage audit revealed that this random split leaked 46.88% of identical flow communication "
        "signatures between the training and testing partitions. Consequently, the baseline model achieved artificially inflated detection accuracy by "
        "memorizing recurring socket identifiers, masking its catastrophic failure on unseen network sessions."
    ),
    (
        "3. Topological Incoherence from Louvain Partitioning: FedGATSage relies on the Louvain algorithm to partition client graphs into communities. "
        "Traag et al. (2019) proved that Louvain systematically generates internally disconnected or poorly connected subgraphs. Transmitting centroids "
        "of disconnected subgraphs to a federated server overlay introduces significant noise during cross-client GraphSAGE aggregation."
    )
]

SEC_2_2_TITLE = "2.2 Summary and Findings of Survey in Tabular Format"
SEC_2_2_PARAS = [
    (
        "Table 2.1 provides an exhaustive comparative synthesis of fifteen foundational and contemporary research works across federated learning, "
        "graph representation learning, class imbalance mitigation, and network intrusion detection, highlighting methodologies, benchmarks, primary findings, "
        "and critical identified limitations."
    )
]

LIT_TABLE_ROWS = [
    ("McMahan et al. (2017)", "Canonical Federated Averaging (FedAvg) over decentralized clients", "MNIST, CIFAR-10", "Established decentralized collaborative training without centralizing raw telemetry", "Suffers from weight drift under non-IID client skew; completely lacks topological awareness"),
    ("Zhao et al. (2018)", "Theoretical analysis of non-IID data divergence in federated learning", "CIFAR-10 Non-IID", "Proved that Earth Mover's Distance between client distributions degrades convergence", "Proposed public data sharing; does not resolve acute class starvation on rare anomalies"),
    ("Li et al. (2020)", "FedProx: Proximal term regularization for heterogeneous federated learning", "Synthetic, FEMNIST", "Constrained local client drift by penalizing parameter divergence from global model", "Requires fine-tuning proximal hyperparameter; does not address relational graph structures"),
    ("Veličković et al. (2018)", "Graph Attention Networks (GAT) with masked self-attention", "Cora, Citeseer, PPI", "Enabled dynamic edge weighting based on neighbor feature relevance", "High quadratic computational complexity; vulnerable to oversmoothing on dense graphs"),
    ("Hamilton et al. (2017)", "GraphSAGE: Inductive representation learning via neighborhood sampling", "PPI, Reddit", "Enabled fast inductive generalization to previously unseen nodes", "Uniform neighbor sampling dilutes rare minority graph edges into majority profiles"),
    ("Lo et al. (2022)", "E-GraphSAGE for edge-attributed network intrusion telemetry", "UNSW-NB15, CIC-IDS2017", "Integrated directional flow attributes into neighborhood aggregation", "Centralized architecture; does not address federated privacy or extreme class imbalance"),
    ("Chang & Branco (2021)", "E-ResGAT: Edge-aggregated GAT with residual skip connections", "NSL-KDD, CIC-IDS2017", "Preserved edge attributes and mitigated gradient vanishing on high-degree nodes", "Evaluated on outdated KDD benchmarks; lacks federated aggregation mechanisms"),
    ("Han et al. (2025)", "FedSTGCN: Spatiotemporal graph convolution for IoT intrusion", "BoT-IoT, ToN-IoT", "Captured spatial topology and temporal bursts across IoT edge gateways", "Extremely high edge computation; lacks metric regularization for long-tail attack recovery"),
    ("Lin et al. (2017)", "Focal Loss for dense object detection and extreme foreground imbalance", "MS COCO", "Dynamically suppressed loss contribution of easy majority background instances", "Modulates gradient magnitude but does not alter geometric metric embedding separation"),
    ("Cui et al. (2019)", "Class-Balanced Loss via effective number of samples theory", "CIFAR-100-LT, ImageNet-LT", "Proved diminishing returns of redundant samples; normalized class loss penalties", "Does not guarantee metric clustering in continuous graph latent spaces"),
    ("Zhang et al. (2018)", "mixup: Beyond empirical risk minimization via convex interpolation", "ImageNet, CIFAR-10", "Enforced linear behavior in intermediate representations and smoothed boundaries", "Random cross-class interpolation corrupts subtle intrusion boundary semantics"),
    ("Khosla et al. (2020)", "Supervised Contrastive Learning (SupCon) on labeled batches", "ImageNet, CIFAR-100", "Achieved superior angular separation and robustness over cross-entropy", "Evaluated strictly on image classification; never applied to federated graph cybersecurity"),
    ("Youm & Kim (2025)", "DS-FedIDS: Class-specific dynamic sampling in federated intrusion detection", "CSE-CIC-IDS2018", "Adjusted client aggregation weights when attack classes are missing locally", "Evaluated on flat tabular features; blind to relational multi-hop attack graphs"),
    ("Sarhan et al. (2021)", "Towards a standard feature set of NetFlow NIDS datasets", "NF-ToN-IoT, NF-UNSW-NB15", "Standardized NetFlow V9 feature extraction across multiple raw PCAP benchmarks", "Highlighted high class imbalance; did not address socket signature evaluation leakage"),
    ("Al-Tfaily et al. (2025)", "FedGATSage: Client GAT, Louvain detection, Server GraphSAGE, RF", "NF-ToN-IoT, CIC-ToN-IoT", "Achieved 78.58% BalAcc with 85% communication reduction", "Random split leaks 46.88% signatures; 99.83% Backdoor collapsed to Injection; Louvain yields disconnected graphs")
]

SEC_2_3_TITLE = "2.3 Challenges in Graph-Based Federated Detection"
SEC_2_3_PARAS = [
    (
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
]

SEC_2_4_TITLE = "2.4 Motivation of the Project Work"
SEC_2_4_PARAS = [
    (
        "Motivated by the critical vulnerabilities identified in the base FedGATSage paper and the broader literature, this dissertation seeks to "
        "establish a mathematically grounded, empirically auditable, and privacy-preserving intrusion detection system. Rather than accepting "
        "the standard compromise between federated privacy and detection accuracy, we hypothesize that integrating Supervised Contrastive Loss "
        "directly into local edge encoders can exert an active metric repulsive force capable of rescuing collapsed minority attack manifolds. "
        "By grounding all evaluations on an audited zero-leakage signature-grouped split across multiple random seeds, this research aims to "
        "bridge the critical gap between theoretical federated graph models and practical, leakage-free cybersecurity defense."
    )
]
