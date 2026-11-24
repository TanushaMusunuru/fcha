import re

with open('dissertation_overleaf.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# Catalog of (original_passage, revised_passage)
replacements = [
    # ==========================================
    # 1. ABSTRACT (Page 5)
    # ==========================================
    (
r'''In this dissertation, we propose a contrastive hybrid federated GNN architecture evaluated under a rigorous signature-grouped, zero-leakage protocol on the official NF-ToN-IoT benchmark. 

Our framework combines three domain-specialized Graph Attention Network (GAT) client models, Leiden community partitioning, community centroid pooling, an aggregated GraphSAGE server overlay, and Random Forest feature fusion.''',
r'''To address these challenges, we develop a contrastive hybrid federated GNN architecture and benchmark it using an audited, signature-grouped evaluation protocol on the official NF-ToN-IoT dataset that guarantees zero flow-signature leakage. The system integrates three domain-specialized Graph Attention Network (GAT) client encoders, Leiden-based community partitioning, centroid pooling, an aggregated GraphSAGE server overlay, and downstream Random Forest feature fusion.'''
    ),

    # ==========================================
    # 2. CHAPTER 1: BACKGROUND (Pages 13-14)
    # ==========================================
    (
r'''Instead, modern edge architectures incorporate billions of heterogeneous, spatially dispersed edge nodes ranging from ultra-low-power microcontrollers and environmental field sensors to programmable logic controllers (PLCs), edge cellular gateways, and embedded industrial robotic endpoints. While this distributed paradigm provides unprecedented operational visibility, automation, and real-time telemetry processing, it simultaneously expands the attack surface of enterprise networks to unprecedented dimensions.''',
r'''Rather, operational networks now span diverse, geographically distributed edge nodes, encompassing low-power field microcontrollers, environmental sensors, programmable logic controllers (PLCs), cellular gateways, and robotic actuators. Although this decentralized infrastructure enables real-time sensing, localized automation, and broad operational visibility, it dramatically widens network perimeter exposure and introduces numerous unmonitored entry vectors.'''
    ),

    (
r'''Unlike conventional data-center servers equipped with dedicated hardware security modules, multi-core processing engines, and continuous administrative oversight, IoT edge devices operate under severe physical and architectural constraints. These devices possess limited computational throughput, restricted memory capacities (frequently measured in kilobytes or megabytes), constrained battery reserves, and intermittent wireless connectivity over lossy communication channels. Furthermore, the extensive firmware heterogeneity and prolonged deployment lifecycles of IoT hardware severely impede standard software maintenance practices. Edge devices frequently operate with outdated cryptographic libraries, hardcoded vendor credentials, and unpatched operating system vulnerabilities, transforming them into lucrative targets for adversarial exploitation.''',
r'''In contrast to enterprise servers that benefit from dedicated cryptographic co-processors, high-throughput compute clusters, and proactive administrative patching, edge IoT endpoints function under tight hardware constraints. Microcontrollers and embedded gateways typically operate with restricted processing budgets, kilobyte- or megabyte-scale memory, battery limitations, and unreliable wireless links. Compounding these constraints, long operational lifecycles and fragmented vendor ecosystems make systematic firmware updates rare in field deployments. As a result, endpoints frequently run deprecated cryptographic routines, rely on default or static credentials, and harbor unmitigated firmware vulnerabilities, rendering them susceptible to automated exploitation.'''
    ),

    (
r'''Modern cyber adversaries routinely execute coordinated, multi-stage campaigns that exploit decentralized topologies. Botnets such as Mirai, Mozi, and their contemporary variants systematically compromise thousands of insecure edge nodes via automated vulnerability scanning and credential brute-forcing, weaponizing them into distributed denial-of-service (DDoS) reflection armies capable of generating terabits-per-second of disruptive traffic. Simultaneously, state-sponsored Advanced Persistent Threat (APT) groups deploy stealthy backdoor command-and-control (C2) channels and credential theft mechanisms to achieve silent administrative privilege escalation and lateral network traversal within industrial operational technology (OT) environments.''',
r'''Adversaries increasingly launch structured, multi-phase intrusions tailored to distributed topologies. High-profile botnet strains, including Mirai and Mozi derivatives, routinely sweep subnets using automated port probes and credential dictionary attacks, aggregating vulnerable endpoints into distributed denial-of-service (DDoS) botnets capable of saturating core infrastructure with terabit-scale floods. In parallel, advanced persistent threat (APT) actors establish low-frequency backdoor command-and-control (C2) sessions, using credential harvesting and living-off-the-land techniques to move laterally within operational technology (OT) subnets without triggering volumetric alarms.'''
    ),

    (
r'''Within the centralized repository, machine learning and deep learning models process aggregated telemetry in batch mode to identify anomalous patterns and signature deviations.

However, the centralized NIDS paradigm is rendered fundamentally unviable by the operational realities of modern IoT ecosystems:''',
r'''Once aggregated, central analytics engines apply machine learning and deep neural models in batch pipelines to flag anomalous flow signatures.

Nevertheless, relying on centralized telemetry collection introduces fundamental operational and architectural roadblocks in distributed IoT environments:'''
    ),

    (
r'''\item \textbf{Prohibitive Bandwidth and Energy Overhead}: Continuous transmission of multi-gigabyte traffic telemetry from millions of edge endpoints introduces severe congestion across wireless backhaul links, directly depleting the energy reserves of battery-powered sensor gateways.''',
r'''\item \textbf{Prohibitive Bandwidth and Energy Overhead}: Continuously streaming raw NetFlow logs or packet traces across wide-area links saturates constrained cellular or LPWAN backhauls and rapidly drains the battery life of remote sensor nodes.'''
    ),

    (
r'''\item \textbf{Single Point of Failure and Surveillance Target}: Centralizing internal enterprise telemetry creates a monolithic single point of failure and an extraordinarily high-value target for adversarial reconnaissance.''',
r'''\item \textbf{Single Point of Failure and Surveillance Target}: Maintaining a centralized telemetry repository establishes an attractive single point of compromise, allowing an adversary who breaches the central store to inspect complete internal communication patterns.'''
    ),

    (
r'''\item \textbf{Breach of Data Privacy and Sovereignty Mandates}: Transmitting raw packet captures and granular NetFlow records across institutional boundaries directly breaches stringent international regulations---such as GDPR, HIPAA, and CCPA. NetFlow records reveal internal IP schemes, subnet segmentation policies, service port layouts, and communication timelines, exposing organizations to substantial legal liabilities.''',
r'''\item \textbf{Breach of Data Privacy and Sovereignty Mandates}: Exporting raw NetFlow or IPFIX records across administrative boundaries risks violating regulatory frameworks such as GDPR, HIPAA, and CCPA. Flow attributes expose private subnet topologies, server port allocations, and workstation activity timelines, creating organizational compliance liabilities.'''
    ),

    (
r'''Federated Learning (FL) has emerged as a revolutionary paradigm to resolve the fundamental conflict between collaborative threat intelligence and decentralized data privacy~\cite{mcmahan2017federated}. Formulated by McMahan et al. in 2017, federated learning enables a consortium of decentralized edge clients to collaboratively train a shared global model while retaining all raw training telemetry strictly on local storage. In a federated intrusion detection workflow, local edge gateways optimize local model parameters over private traffic captures and transmit only parameterized model weights or gradient updates to a central federated aggregation server. The server combines these local parameters via algorithms such as Federated Averaging (FedAvg) to synthesize an updated global consensus model, which is subsequently redistributed to participating clients for local inference.''',
r'''To reconcile collaborative model training with institutional data containment, Federated Learning (FL) establishes a framework where participating edge clients optimize a shared model collaboratively without centralizing raw traffic logs~\cite{mcmahan2017federated}. Under the Federated Averaging (\texttt{FedAvg}) protocol introduced by McMahan et al. (2017), client nodes train local models on private flow captures and upload only parameter weights or gradient updates to an aggregation coordinator. The coordinator synthesizes these contributions into a consensus global parameter vector, which is distributed back to edge nodes for local intrusion classification.'''
    ),

    (
r'''Traditional machine learning approaches treat network telemetry as flat tabular vectors, ignoring the underlying graph structure of network conversations.''',
r'''Standard classifiers typically treat flow records as independent feature vectors, omitting the rich topological interactions that govern host-to-host conversations.'''
    ),

    (
r'''Graph Neural Networks (GNNs), such as Graph Convolutional Networks (GCNs), Graph Attention Networks (GATs), and GraphSAGE, provide an expressive mathematical foundation to model network interactions by representing IP hosts as graph vertices and directional communication flows as attributed edges, capturing complex topological dependencies that completely elude non-relational statistical classifiers~\cite{velickovic2018gat, hamilton2017graphsage}.''',
r'''Graph Neural Networks (GNNs)---such as Graph Attention Networks (GAT) and GraphSAGE---natively represent these relational dynamics by treating IP addresses as graph vertices and NetFlow sessions as attributed directed edges, extracting structural interdependencies that flat tabular models overlook~\cite{velickovic2018gat, hamilton2017graphsage}.'''
    ),

    # ==========================================
    # 3. CHAPTER 1: PROBLEM STATEMENT (Pages 15-16)
    # ==========================================
    (
r'''Despite the compelling theoretical promise of combining Federated Learning with Graph Neural Networks for decentralized cybersecurity, existing Federated Graph Neural Network (FedGNN) architectures exhibit four severe operational pathologies and pervasive methodological vulnerabilities that critically compromise their real-world efficacy:''',
r'''Although integrating Federated Learning with Graph Neural Networks provides clear privacy and structural benefits, existing FedGNN intrusion detection designs face four major methodological and structural bottlenecks:'''
    ),

    (
r'''    \item \textbf{Pervasive Socket-Signature Evaluation Data Leakage in Academic Benchmarks}: A critical vulnerability in contemporary intrusion detection literature is the pervasive reliance on naive uniform random row partitioning during experimental evaluation. In real-world enterprise NetFlow telemetry, repeated packets belonging to the same application session or automated intrusion burst share identical communication socket signatures---defined by source IP, destination IP, Layer 4 service ports, transport protocol, and flow volume attributes. When benchmarks apply standard random row splits, flows originating from the exact same socket conversation are simultaneously distributed across both training and testing folds. Classifiers evaluated under this compromised setup achieve artificially inflated detection accuracy ($>99\%$) by simply memorizing static socket tuples, masking catastrophic failure when deployed against authentic, previously unseen network sessions.''',
r'''    \item \textbf{Pervasive Socket-Signature Evaluation Data Leakage in Academic Benchmarks}: Many intrusion detection evaluations rely on uniform random train-test row splits. In flow-based datasets, repeated packets from a single attack run or application session generate identical socket signatures (source/destination IPs, Layer 4 ports, transport protocol, and flow metrics). Standard row splitting allocates records from the same flow signature into both training and evaluation subsets simultaneously. This allows models to achieve high apparent test accuracy ($>99\%$) through memorizing static socket combinations, hiding severe performance degradation on genuinely unseen sessions.'''
    ),

    (
r'''    \item \textbf{Structural Incoherence from Disconnected Heuristic Graph Partitions}: Prior federated graph frameworks rely on heuristic community detection algorithms, notably the Louvain modularity optimization algorithm, to cluster client graphs and abstract topology before server transmission. However, Louvain relies on greedy local node moves that frequently trap community discovery in suboptimal local maxima, mathematically generating internally disconnected or arbitrarily poorly connected community subgraphs. Transmitting the centroids of disconnected community artifacts to a federated server overlay introduces substantial structural noise, degrading the stability and convergence of cross-client GraphSAGE aggregation.''',
r'''    \item \textbf{Structural Incoherence from Disconnected Heuristic Graph Partitions}: Existing federated graph systems often utilize Louvain modularity clustering to abstract client subgraphs before transmitting representations to the coordinator. However, Louvain's heuristic aggregation can produce communities that are internally disconnected or weakly cohesive. Forwarding the pooled centroids of fragmented subgraphs introduces structural noise into the server's inter-community overlay, impeding GraphSAGE aggregation across clients.'''
    ),

    # ==========================================
    # 4. CHAPTER 1: OBJECTIVES & CONTRIBUTIONS (Pages 16-18)
    # ==========================================
    (
r'''To comprehensively overcome the technical vulnerabilities identified above, this dissertation develops, audits, and validates a contrastive hybrid federated Graph Neural Network framework engineered specifically for highly imbalanced IoT network intrusion detection. The primary engineering and scientific objectives of this research are formulated as follows:''',
r'''To resolve these methodological and structural limitations, this investigation designs and validates a contrastive hybrid federated GNN framework tailored for highly skewed IoT traffic telemetry. The study pursues the following core technical objectives:'''
    ),

    (
r'''\item \textbf{Formulation of an Audited Zero-Leakage Benchmark Protocol}: Establish and mathematically verify a rigorous 5-fold \texttt{StratifiedGroupKFold} evaluation protocol grouped by an 8-feature socket communication signature across 1,377,837 NetFlow records of the official NF-ToN-IoT benchmark, proving absolute $0.00\%$ signature overlap between training and testing folds to eliminate evaluation leakage.''',
r'''\item \textbf{Formulation of an Audited Zero-Leakage Benchmark Protocol}: Implement and verify a 5-fold \texttt{StratifiedGroupKFold} partitioning scheme grouped on an 8-tuple socket signature across 1,377,837 NetFlow records in NF-ToN-IoT, confirming $0.00\%$ signature leakage between folds to ensure realistic evaluation.'''
    ),

    (
r'''\item \textbf{Engineering of Domain-Specialized Client GAT Subgraphs}: Design and construct three dedicated, domain-specialized Graph Attention Network (GAT) client detectors---Temporal GAT, Content GAT, and Behavioral GAT---capable of isolating''',
r'''\item \textbf{Engineering of Domain-Specialized Client GAT Subgraphs}: Construct three specialized Graph Attention Network (GAT) encoders---Temporal, Content, and Behavioral---to decouple'''
    ),

    (
r'''\item \textbf{Integration of Leiden Constant Potts Model Community Partitioning}: Incorporate the Leiden community detection algorithm optimizing the Constant Potts Model (CPM) quality function into client graph pipelines, mathematically guaranteeing that all discovered community subgraphs are strictly connected, robust, and topologically sound for server abstraction.''',
r'''\item \textbf{Integration of Leiden Constant Potts Model Community Partitioning}: Apply the Leiden algorithm under the Constant Potts Model (CPM) to partition client graphs, ensuring discovered communities remain strictly connected and structurally well-formed prior to server pooling.'''
    ),

    (
r'''\item \textbf{Formulation of Supervised Contrastive Metric Regularization (SupCon)}: Formulate a joint multi-task optimization objective uniting Class-Balanced Focal (CB-Focal) loss ($\beta=0.9999, \gamma=2.0$) with Supervised Contrastive (SupCon) representation regularization ($\mu=0.1, \tau=0.07$) directly on normalized edge embeddings, mathematically driving active metric repulsion between overlapping attack manifolds.''',
r'''\item \textbf{Formulation of Supervised Contrastive Metric Regularization (SupCon)}: Formulate a dual-objective training loss combining Class-Balanced Focal loss ($\beta=0.9999, \gamma=2.0$) with Supervised Contrastive (SupCon) regularization ($\mu=0.1, \tau=0.07$) on normalized flow embeddings, generating geometric repulsion between overlapping attack classes.'''
    ),

    (
r'''\item \textbf{Implementation of Multi-Tiered Class Balancing Strategies}: Incorporate client-local intra-class convex edge interpolation (Mixup along flow feature dimensions with Beta distribution) and a dynamic class-balanced batch sampler guaranteeing $M=64$ samples per class per step, stabilizing the optimization landscape under extreme imbalance.''',
r'''\item \textbf{Implementation of Multi-Tiered Class Balancing Strategies}: Integrate client-level intra-class convex interpolation and dynamic batch sampling ($M=64$ edges per class per step) to provide balanced gradient signals under severe label scarcity.'''
    ),

    (
r'''\item \textbf{Multi-Seed Statistical Replication and Diagnostic Auditing}: Rigorously evaluate and verify the proposed framework across three independent random initialization seeds ($42, 43, 44$) on NF-ToN-IoT and five seeds ($42$ to $46$) on NF-UNSW-NB15, establishing reproducible empirical evidence and isolating the exact topological mechanism responsible for minority recovery.''',
r'''\item \textbf{Multi-Seed Statistical Replication and Diagnostic Auditing}: Evaluate the complete system across multiple random initialization seeds (seeds 42--44 on NF-ToN-IoT and seeds 42--46 on NF-UNSW-NB15) to ensure statistical rigor and empirically trace the mechanism behind minority-class recovery.'''
    ),

    (
r'''This dissertation delivers five major scientific and technological contributions to the fields of federated learning, graph representation learning, and network security:''',
r'''This work provides five primary methodological and empirical contributions to decentralized graph-based network security:'''
    ),

    # ==========================================
    # 5. CHAPTER 1: ORGANIZATION (Pages 18-19)
    # ==========================================
    (
r'''The remainder of this dissertation is systematically structured into five subsequent chapters:''',
r'''The dissertation is organized as follows:'''
    ),

    (
r'''It presents a structured comparative table of 15 benchmark studies, identifies critical technical bottlenecks, and articulates the project motivation.''',
r'''It categorizes 15 key benchmark investigations in a comparative matrix, highlights technical challenges, and outlines the rationale for this research.'''
    ),

    (
r'''\item \textbf{Chapter 4 (Methodology)} presents an in-depth examination of existing baselines (centralized models and base FedGATSage), followed by the complete formulation of our proposed contrastive hybrid federated architecture. It includes full mathematical derivations of specialized GATs, Leiden CPM partitioning, CB-Focal loss, SupCon gradient dynamics, server GraphSAGE overlay, two-stage Random Forest fusion, algorithmic specifications, and system flowcharts.''',
r'''\item \textbf{Chapter 4 (Methodology)} reviews baseline centralized and federated graph pipelines before presenting the mathematical formulation of our contrastive architecture, including specialized GAT layers, Leiden partitioning, loss equations, server aggregation, and the Random Forest meta-classifier.'''
    ),

    (
r'''\item \textbf{Chapter 5 (Results and Discussion)} delivers comprehensive empirical findings across multi-seed runs, qualitative manifold visualizations, full confusion matrix diagnostics, headline metric tables, mathematical gain decomposition, systematic ablation progressions, node-averaging hypothesis testing, cross-dataset validation on NF-UNSW-NB15, and deep discussions on gradient mechanics, privacy trade-offs, and threats to validity.''',
r'''\item \textbf{Chapter 5 (Results and Discussion)} reports experimental findings across multiple random seeds, including confusion matrix diagnostics, ablation studies, gain decompositions, node-averaging mechanism validation, cross-dataset evaluations, and discussions on operational trade-offs.'''
    ),

    (
r'''\item \textbf{Chapter 6 (Conclusion and Future Directions)} summarizes the achieved scientific milestones, key empirical takeaways, and outlines four concrete future research trajectories extending this work toward adaptive temperature scheduling, zero-day subnet transfer, formal differential privacy, and hardware-in-the-loop edge deployment.''',
r'''\item \textbf{Chapter 6 (Conclusion and Future Directions)} synthesizes primary findings, discusses broader architectural implications, and outlines future research directions in adaptive temperature scheduling, cross-subnet generalization, formal privacy bounds, and edge hardware deployment.'''
    ),

    # ==========================================
    # 6. CHAPTER 2: LITERATURE SURVEY (Pages 20-28)
    # ==========================================
    (
r'''decentralized federated learning protocols, graph representation learning for network telemetry, optimization and loss formulation for acute class imbalance, and metric representation learning via contrastive objectives. This section delivers a comprehensive, rigorous examination of foundational literature and state-of-the-art developments across each of these pillars.''',
r'''decentralized federated protocols, graph neural architectures for network telemetry, loss formulations for heavy class imbalance, and contrastive metric learning. This section reviews core theoretical foundations and recent empirical studies across each area.'''
    ),

    (
r'''Signature-based systems (e.g., Snort, Suricata) inspect packet payloads against curated databases of known malicious patterns. While computationally efficient for well-characterized attacks, signature engines are fundamentally incapable of detecting zero-day exploits, polymorphism, or obfuscated network behaviors. To achieve generalized anomaly detection, researchers turned to statistical machine learning models trained on network flow telemetry, notably Random Forests~\cite{breiman2001randomforests}, Support Vector Machines (SVMs), and $k$-Nearest Neighbors ($k$-NN).''',
r'''Signature-based intrusion detection tools (such as Snort and Suricata) match packet payloads against rulesets of known attack fingerprints. While fast and precise for recognized exploits, signature approaches struggle against polymorphic variants, evasion techniques, and zero-day threats. To improve detection breadth, research transitioned toward statistical and machine learning classifiers trained on flow summaries, including Random Forests~\cite{breiman2001randomforests}, Support Vector Machines (SVMs), and $k$-Nearest Neighbors ($k$-NN).'''
    ),

    (
r'''Random Forest classifiers, in particular, demonstrated outstanding performance across historical cybersecurity benchmarks such as KDD-Cup 99 and NSL-KDD. By constructing ensembles of unpruned decision trees over bootstrap samples and evaluating random feature subsets at each split, Random Forests exhibit remarkable resilience to tabular noise and establish sharp, non-linear decision thresholds along orthogonal continuous dimensions. However, classical shallow classifiers rely heavily on manual feature engineering and require all training records to be centralized within a single computing repository, conflicting with data privacy constraints in multi-tenant enterprise networks.''',
r'''Random Forest models in particular have shown strong baseline efficacy on tabular benchmark datasets such as KDD-Cup 99 and NSL-KDD. By aggregating decision trees over bootstrap samples with random feature selection, tree ensembles form sharp, axis-aligned boundaries that handle noisy tabular metrics effectively. Nonetheless, standard tabular classifiers require aggregating data into a centralized store, raising regulatory and privacy challenges, and depend heavily on feature engineering without capturing host communication structure.'''
    ),

    (
r'''for cyber telemetry analysis. Deep Autoencoders reconstruct benign traffic patterns and flag high reconstruction errors as anomalies, whereas LSTMs model the temporal progression of packet inter-arrival times. Nevertheless, these deep learning architectures continue to treat network telemetry as flat, independent, and identically distributed (IID) tabular vectors. They remain fundamentally blind to the underlying topological relationships between network hosts, unable to correlate multi-point reconnaissance with subsequent lateral movement across enterprise subnets.''',
r'''to analyze traffic streams. Deep autoencoders learn normal baseline reconstructions to flag deviations, while recurrent models capture sequence dynamics in packet arrival timing. Even so, these deep architectures largely process flows as independent records, neglecting host-to-host interaction graphs and hindering the correlation of coordinated reconnaissance or lateral movement across enterprise segments.'''
    ),

    (
r'''To reconcile collaborative threat intelligence with strict data privacy mandates (such as GDPR and HIPAA), Federated Learning (FL) was introduced by McMahan et al. (2017) through the canonical Federated Averaging (\texttt{FedAvg}) algorithm~\cite{mcmahan2017federated}. In \texttt{FedAvg}, a global coordination server maintains a shared model parameter vector. Across iterative communication rounds, a subset of decentralized client nodes downloads the global parameters, performs local stochastic gradient descent (SGD) over private data partitions, and transmits the resulting parameter deltas back to the server. The server aggregates local updates proportionally to each client's dataset volume:
\begin{equation}
W_{t+1} = \sum_{k=1}^K \left( \frac{n_k}{n} \right) W_{t+1}^k
\label{eq:fedavg_theory}
\end{equation}
By transmitting model parameters rather than raw packet captures, \texttt{FedAvg} significantly reduces raw bandwidth overhead and prevents the direct exposure of sensitive internal network metadata.''',
r'''To support multi-institutional model training under privacy requirements such as GDPR and HIPAA, Federated Learning (FL) coordinates decentralized model optimization without transferring raw network traffic~\cite{mcmahan2017federated}. Under the standard Federated Averaging (\texttt{FedAvg}) method, a coordination server orchestrates iterative training rounds: participating clients download current global weights, update them locally via stochastic gradient descent on private data, and report their updated parameters back to the server. The central coordinator then averages client weights based on sample size:
\begin{equation}
W_{t+1} = \sum_{k=1}^K \left( \frac{n_k}{n} \right) W_{t+1}^k
\label{eq:fedavg_theory}
\end{equation}
Exchanging model weights rather than flow logs substantially lowers wide-area bandwidth consumption while preventing direct exposure of internal host identifiers.'''
    ),

    (
r'''Despite its privacy advantages, deploying federated learning across edge IoT environments introduces severe statistical challenges stemming from non-independent and identically distributed (non-IID) data distributions. Zhao et al. (2018) provided foundational theoretical and empirical evidence demonstrating that statistical divergence between client data distributions introduces significant weight drift during local training rounds~\cite{zhao2018federated}. As client parameter trajectories diverge, standard \texttt{FedAvg} aggregation produces sub-optimal global consensus models, substantially slowing convergence rates and degrading overall accuracy. Li et al. (2020) analyzed optimization challenges under system and statistical heterogeneity, proposing \texttt{FedProx}, which introduces an explicit proximal regularization term to constrain local parameter drift relative to the global model~\cite{li2020federatedchallenges}:
\begin{equation}
\mathcal{R}_{\text{prox}} = \frac{\mu}{2} \left\| W - W_t \right\|^2
\end{equation}''',
r'''However, real-world edge IoT networks present non-independent and identically distributed (non-IID) conditions that degrade standard federated workflows. Zhao et al. (2018) showed that distribution divergence among clients induces parameter drift during local training epochs, slowing global convergence and degrading test performance~\cite{zhao2018federated}. To stabilize training across heterogeneous clients, Li et al. (2020) proposed \texttt{FedProx}, adding a proximal penalty that limits local model deviations from the global consensus~\cite{li2020federatedchallenges}:
\begin{equation}
\mathcal{R}_{\text{prox}} = \frac{\mu}{2} \left\| W - W_t \right\|^2
\end{equation}'''
    ),

    (
r'''Specific attack categories---such as specialized SCADA command injection or industrial backdoor beacons---may be observed exclusively by a single client while remaining completely absent from other nodes. To combat this extreme class absence, Youm and Kim (2025) proposed \texttt{DS-FedIDS}, employing class-specific dynamic sampling techniques to adjust client loss weighting based on local class distributions~\cite{youm2025dsfedids}. Similarly, Hsu et al. (2019) demonstrated that Dirichlet distribution modeling $\text{Dir}(\alpha)$ accurately captures extreme non-IID partitioning in federated benchmarks~\cite{hsu2019noniid}. However, standard federated intrusion detection architectures remain vulnerable when minority attack classes are non-uniformly distributed among participating clients.''',
r'''Certain intrusion types---such as industrial protocol manipulation or targeted backdoor beaconing---may appear only on specific subnets while remaining unobserved by others. Addressing this client-level imbalance, Youm and Kim (2025) introduced \texttt{DS-FedIDS}, which dynamically adjusts client loss weights according to local class representations~\cite{youm2025dsfedids}. Partitioning with Dirichlet distributions $\text{Dir}(\alpha)$ has likewise become standard for modeling realistic client label skew~\cite{hsu2019noniid}. Even so, conventional aggregation often degrades when rare intrusions are entirely absent from most participating nodes.'''
    ),

    (
r'''In network security formulations, unique IP addresses represent vertices $\mathcal{V}$, while communication flows represent directed edges $\mathcal{E}$ connecting interacting endpoints.''',
r'''In cybersecurity graph formulations, unique IP addresses form vertices $\mathcal{V}$, while individual NetFlow communication records form directed attributed edges $\mathcal{E}$.'''
    ),

    (
r'''Veli\v{c}kovi\'{c} et al. (2018) introduced Graph Attention Networks (GAT), which revolutionized representation learning on graphs by incorporating self-attention mechanisms into node convolutions~\cite{velickovic2018gat}. Rather than assigning static or degree-normalized weights to adjacent vertices (as in Graph Convolutional Networks, Kipf and Welling, 2016), GAT computes dynamic attention coefficients $\alpha_{uv}$ that quantify the relative importance of node $v$'s features to node $u$. This self-attentive weighting enables GAT to dynamically prioritize suspicious, bursty communication channels while down-weighting routine benign background transactions.''',
r'''Graph Attention Networks (GAT), proposed by Veli\v{c}kovi\'{c} et al. (2018), introduced learnable self-attention over node neighborhoods~\cite{velickovic2018gat}. Instead of relying on static degree normalizations (as in standard Graph Convolutional Networks), GAT computes dynamic pairwise attention coefficients $\alpha_{uv}$ reflecting neighbor relevance. In network telemetry, this attention mechanism allows encoders to focus on anomalous or bursty edge exchanges while suppressing routine background traffic.'''
    ),

    (
r'''To enable scalable inductive representation learning over massive, dynamically expanding graphs, Hamilton et al. (2017) formulated GraphSAGE~\cite{hamilton2017graphsage}. Instead of operating over the full graph Laplacian matrix, GraphSAGE samples a fixed-size local neighborhood for each target node and aggregates representations via learnable pooling functions (e.g., mean, LSTM, or max pooling). GraphSAGE's inductive capability enables it to generate meaningful embeddings for previously unseen IP hosts without requiring retraining over the entire network topology.''',
r'''To scale representation learning to large evolving topologies, Hamilton et al. (2017) designed GraphSAGE, an inductive framework that samples localized neighborhoods and pools features through learnable aggregators~\cite{hamilton2017graphsage}. Because it learns aggregation functions rather than fixed node embeddings, GraphSAGE readily generalizes to newly observed network hosts without retraining the full graph topology.'''
    ),

    (
r'''to accommodate edge attributes directly by embedding directional flow features into the message-passing phase~\cite{lo2022egraphsage}. Chang and Branco (2021) formulated E-ResGAT, integrating residual skip connections into graph attention networks to preserve edge-level statistical attributes across deep message-passing layers and prevent oversmoothing on high-degree nodes~\cite{chang2021eresgat}. Han et al. (2025) formulated FedSTGCN, uniting federated learning with spatiotemporal graph convolutions to capture temporal packet bursts and relational topology simultaneously across IoT sensor gateways~\cite{han2025fedstgcn}. A comprehensive survey by Liu et al. (2024) systematically categorized federated GNN frameworks, emphasizing that structural heterogeneity, scalability, and acute class imbalance remain unresolved bottlenecks in decentralized graph learning~\cite{liu2024fedgnn}.''',
r'''to handle flow-specific attributes directly during message aggregation~\cite{lo2022egraphsage}. Chang and Branco (2021) introduced E-ResGAT, combining residual connections with edge-aware attention to retain flow statistics and prevent feature oversmoothing across dense nodes~\cite{chang2021eresgat}. Similarly, Han et al. (2025) proposed FedSTGCN, coupling spatiotemporal graph convolutions with federated learning to capture temporal bursts across IoT edge devices~\cite{han2025fedstgcn}. As highlighted in a recent survey by Liu et al. (2024), scaling federated GNNs under extreme class imbalance and non-IID graph topologies remains an open challenge~\cite{liu2024fedgnn}.'''
    ),

    (
r'''Benign background transactions typically constitute $80\%$ to $90\%$ of total logged traffic, volumetric denial-of-service and web injection attacks occupy moderate proportions ($10\%$ to $20\%$), while critical targeted intrusions---such as stealthy Backdoors, administrative Password guessing, and Shellcode exploits---represent less than $1.5\%$ of total recorded events~\cite{sarhan2021netflow, alsaedi2020toniot}. Johnson and Khoshgoftaar (2019) surveyed deep learning techniques for imbalanced domains, proving mathematically that standard empirical risk minimization under unweighted Cross-Entropy loss heavily biases parameter optimization toward majority classes~\cite{johnson2019survey}. In unweighted optimization, gradient updates from massive majority classes completely overwhelm the sparse gradients generated by rare intrusions, causing high False Negative Rates (FNR) on critical security anomalies.''',
r'''Normal background flows commonly account for $80\%$ to $90\%$ of records, volumetric attacks (such as DDoS or web injection) comprise moderate shares ($10\%$ to $20\%$), and targeted intrusions (such as backdoor persistence, brute-force password guessing, and shellcode exploits) make up less than $1.5\%$ of total traffic~\cite{sarhan2021netflow, alsaedi2020toniot}. As Johnson and Khoshgoftaar (2019) documented, optimizing standard unweighted cross-entropy loss under severe skew causes gradient updates to be dominated by high-frequency majority flows~\cite{johnson2019survey}. Consequently, the decision boundaries of rare attacks are easily compromised, leading to elevated False Negative Rates (FNR) on critical security threats.'''
    ),

    (
r'''To address class imbalance without discarding valuable majority data via random undersampling, researchers have investigated loss re-weighting and focal modulation strategies. Lin et al. (2017) formulated Focal Loss, introducing a dynamic modulating factor $(1 - p_t)^\gamma$ to standard cross-entropy~\cite{lin2017focal}:
\begin{equation}
\mathcal{L}_{\text{FL}} = - (1 - p_t)^\gamma \log(p_t)
\end{equation}
When an instance is well-classified ($p_t \to 1$, typical for easy majority benign flows), the modulating factor approaches zero, exponentially suppressing its contribution to the gradient. Consequently, optimization focuses predominantly on ambiguous boundary instances and hard-to-classify minority samples.''',
r'''To avoid data loss from undersampling, loss-reweighting and focal modulation techniques have been widely studied. Lin et al. (2017) formulated Focal Loss, applying a modulating term $(1 - p_t)^\gamma$ to standard cross-entropy~\cite{lin2017focal}:
\begin{equation}
\mathcal{L}_{\text{FL}} = - (1 - p_t)^\gamma \log(p_t)
\end{equation}
For confident predictions ($p_t \to 1$, common among majority benign traffic), this modulating term downscales gradient magnitude, redirecting model capacity toward ambiguous boundary examples and rare minority instances.'''
    ),

    (
r'''Cui et al. (2019) introduced Class-Balanced Loss based on effective sample volume theory~\cite{cui2019cbloss}. Cui et al. proved that as sample volume increases, the marginal information gain of additional instances diminishes exponentially due to data overlap in the feature space. By defining the effective number of samples as:
\begin{equation}
E_n = \frac{1 - \beta^n}{1 - \beta}, \quad \text{where } \beta \in [0, 1)
\end{equation}
Cui et al. designed class-balancing weights that scale inversely with effective sample space rather than raw counts:
\begin{equation}
\alpha_c \propto \frac{1 - \beta}{1 - \beta^{n_c}}
\end{equation}
This prevents massive majority classes from dominating optimization while preventing the over-penalization of moderate classes. At the data level, Zhang et al. (2018) introduced Mixup, which synthesizes virtual training instances via convex feature interpolations~\cite{zhang2018mixup}:
\begin{equation}
\tilde{x} = \lambda x_i + (1 - \lambda) x_j
\end{equation}
Interpolating features regularizes deep neural networks, promoting linear behavior in intermediate representations and smoothing decision margins.''',
r'''Addressing the diminishing returns of redundant instances, Cui et al. (2019) formulated Class-Balanced Loss using effective sample volume theory~\cite{cui2019cbloss}. By modeling data overlap, the effective sample volume is defined as:
\begin{equation}
E_n = \frac{1 - \beta^n}{1 - \beta}, \quad \text{where } \beta \in [0, 1)
\end{equation}
Weighting loss terms inversely by effective volume rather than raw frequencies:
\begin{equation}
\alpha_c \propto \frac{1 - \beta}{1 - \beta^{n_c}}
\end{equation}
prevents dominant classes from driving the gradient while avoiding excessive penalties on moderate classes. At the data level, Zhang et al. (2018) proposed Mixup, generating virtual examples via convex feature interpolation~\cite{zhang2018mixup}:
\begin{equation}
\tilde{x} = \lambda x_i + (1 - \lambda) x_j
\end{equation}
which regularizes neural networks by encouraging smoother transition regions between classes.'''
    ),

    (
r'''Contrastive representation learning establishes embedding spaces by explicitly pulling representations of semantically similar instances together while pushing dissimilar instances apart. In self-supervised learning, contrastive frameworks (e.g., SimCLR, Chen et al., 2020; MoCo, He et al., 2020) construct positive pairs through stochastic data augmentations of the same unlabeled instance, while treating all other instances in a mini-batch as negatives.''',
r'''Contrastive representation learning structures latent spaces by drawing embeddings of similar samples closer while repelling dissimilar samples. In self-supervised frameworks such as SimCLR (Chen et al., 2020) and MoCo (He et al., 2020), positive pairs originate from different augmentations of the same unlabeled sample, while all other batch elements act as negative distractors.'''
    ),

    (
r'''Khosla et al. (2020) proposed Supervised Contrastive Learning (SupCon), extending contrastive representation learning to fully labeled datasets~\cite{khosla2020supcon}. In SupCon, all instances sharing the same ground-truth class label within a mini-batch are treated as mutual positive anchors, while instances from differing classes serve as mutual negatives. Khosla et al. demonstrated that SupCon achieves superior angular separation between class manifolds, exhibits greater robustness to label corruption, and eliminates the hyperparameter sensitivity associated with standard cross-entropy training. However, despite its extraordinary success in computer vision, the integration of Supervised Contrastive learning as an architectural regularizer within federated graph neural networks to combat topological oversmoothing on imbalanced NetFlow telemetry represents an unaddressed research frontier.''',
r'''Khosla et al. (2020) generalized this concept to labeled datasets through Supervised Contrastive Learning (SupCon)~\cite{khosla2020supcon}. In SupCon, all instances sharing a class label within a mini-batch serve as mutual positives, while instances with differing labels act as negatives. Khosla et al. demonstrated that SupCon yields clearer angular separation between class manifolds and demonstrates greater stability than unweighted cross-entropy. However, incorporating SupCon as an architectural regularizer in federated GNNs to counteract topological dilution on skewed NetFlow data remains largely unexplored.'''
    ),

    (
r'''Our investigation takes as its foundational baseline the FedGATSage architecture recently proposed by Al-Tfaily et al. (2025) in Nature Scientific Reports~\cite{altfaily2025fedgatsage}. FedGATSage introduced a hybrid federated architecture combining client-side Graph Attention Networks (GAT), Louvain community detection, an aggregated server GraphSAGE overlay, and an ensemble Random Forest meta-classifier. While Al-Tfaily et al. reported an aggregate Balanced Accuracy of $78.58\%$ and Macro FNR of $22.34\%$ on NF-ToN-IoT, our extensive code-level audit revealed two critical structural vulnerabilities and unaddressed methodological pathologies:''',
r'''This research builds upon the FedGATSage pipeline introduced by Al-Tfaily et al. (2025) in Nature Scientific Reports~\cite{altfaily2025fedgatsage}. FedGATSage combines client-side Graph Attention Networks (GAT), Louvain community clustering, an aggregated server GraphSAGE overlay, and a Random Forest meta-learner, reporting a Balanced Accuracy of $78.58\%$ and Macro FNR of $22.34\%$ on NF-ToN-IoT. However, an empirical code audit uncovered several methodological and structural limitations in this baseline:'''
    ),

    (
r'''Traag et al. (2019) proved that Louvain systematically generates internally disconnected or poorly connected subgraphs~\cite{traag2019leiden}. Transmitting centroids of disconnected subgraphs to a federated server overlay introduces significant noise during cross-client GraphSAGE aggregation.''',
r'''As Traag et al. (2019) established, Louvain clustering can yield communities containing disconnected components~\cite{traag2019leiden}. Passing centroids from fragmented subgraphs into the server overlay introduces geometric noise during cross-client GraphSAGE aggregation.'''
    ),

    (
r'''Table~\ref{tab:lit_survey} provides an exhaustive comparative synthesis of fifteen foundational and contemporary research works across federated learning, graph representation learning, class imbalance mitigation, and network intrusion detection, highlighting methodologies, benchmarks, primary findings, and critical identified limitations.''',
r'''Table~\ref{tab:lit_survey} summarizes fifteen key studies across federated learning, graph representation methods, class-imbalance formulations, and intrusion detection, detailing their methodologies, datasets, findings, and identified limitations.'''
    ),

    (
r'''A rigorous synthesis of existing literature identifies four primary technical bottlenecks that currently prevent practical deployment of federated graph intrusion detection systems in industrial IoT environments:
\begin{enumerate}
    \item \textbf{Evaluation Leakage Blindness}: Prevailing academic publications evaluate NIDS models on randomly split NetFlow records. Because repeated packets in a communication burst share identical socket identifiers, random partitioning permits classifiers to memorize static flow tuples, presenting misleading detection performance while masking catastrophic zero-day failure.
    \item \textbf{Continuous Manifold Overlap}: Unlike tabular decision trees that apply sharp, orthogonal axis splits on numeric features, neural network encoders project instances onto continuous hyperspherical manifolds. Under acute imbalance, the loss gradient of the majority class exerts overwhelming dominance, swallowing the minority representation space.
    \item \textbf{Topological Feature Blurring}: Graph message passing operates by aggregating neighbor features onto endpoint nodes. When an IP host participates in both background traffic and rare intrusions, recursive neighborhood averaging blurs the minority intrusion signature into the background centroid.
    \item \textbf{Client-to-Server Communication Constraints}: Transmitting complete local graph topologies across bandwidth-constrained IoT wireless networks is prohibitively expensive. Developing robust community abstraction mechanisms that compress edge topologies without destroying subtle relational indicators is vital.
\end{enumerate}''',
r'''Reviewing existing literature reveals four primary technical bottlenecks that limit the operational reliability of federated graph intrusion detection in IoT deployments:
\begin{enumerate}
    \item \textbf{Evaluation Leakage Blindness}: Many published NIDS studies evaluate models using uniform random row splits. Because repeated packets in a single communication burst share identical socket identifiers, random partitioning allows models to memorize static flow tuples, inflating evaluation metrics while obscuring failure on novel sessions.
    \item \textbf{Continuous Manifold Overlap}: Whereas decision tree algorithms partition feature space with orthogonal threshold planes, neural network encoders project flows into continuous latent embeddings. Under severe class imbalance, majority-class gradients dominate parameter updates, absorbing minority-class manifolds into adjacent majority clusters.
    \item \textbf{Topological Feature Blurring}: GNN convolutions pool adjacent edge attributes onto endpoint vertices. When a network host handles high-volume benign traffic alongside sparse attack flows, neighborhood averaging dilutes rare attack features into the dominant host profile.
    \item \textbf{Client-to-Server Communication Constraints}: Transmitting complete edge graphs from distributed IoT clients creates unsustainable communication overhead. Effective community abstraction is necessary to compress local topologies without erasing relational indicators.
\end{enumerate}'''
    ),

    (
r'''Motivated by the critical vulnerabilities identified in the base FedGATSage paper and the broader literature, this dissertation seeks to establish a mathematically grounded, empirically auditable, and privacy-preserving intrusion detection system. Rather than accepting the standard compromise between federated privacy and detection accuracy, we hypothesize that integrating Supervised Contrastive Loss directly into local edge encoders can exert an active metric repulsive force capable of rescuing collapsed minority attack manifolds. By grounding all evaluations on an audited zero-leakage signature-grouped split across multiple random seeds, this research aims to bridge the critical gap between theoretical federated graph models and practical, leakage-free cybersecurity defense.''',
r'''Motivated by these vulnerabilities in the base FedGATSage model and wider literature, this dissertation investigates a mathematically regularized and empirically audited federated intrusion detection framework. We hypothesize that introducing Supervised Contrastive Loss into local graph encoders creates an active metric repulsive force that prevents minority-manifold collapse under severe class skew. By conducting all evaluations under an audited zero-leakage signature-grouped protocol across multiple random seeds, this research demonstrates that federated privacy and high minority-class recall can be achieved simultaneously.'''
    ),

    # ==========================================
    # 7. CHAPTER 3: MATERIALS AND METHODS (Pages 29-36)
    # ==========================================
    (
r'''To guarantee empirical reproducibility and evaluate the proposed framework under authentic cybersecurity telemetry, all investigations in this dissertation utilize standardized NetFlow-v1 benchmarks developed by Sarhan et al. (2021)~\cite{sarhan2021netflow}. The primary benchmark employed for architectural optimization, component ablation, and multi-seed evaluation is the official NF-ToN-IoT dataset. In addition, the NF-UNSW-NB15 dataset is utilized as a secondary benchmark to rigorously assess the generalizability of contrastive metric regularization across divergent network topologies.''',
r'''To ensure experimental reproducibility on realistic telemetry, our evaluations use standardized NetFlow-v1 datasets curated by Sarhan et al. (2021)~\cite{sarhan2021netflow}. The primary testbed for architectural optimization, component ablation, and multi-seed testing is NF-ToN-IoT. In addition, we evaluate NF-UNSW-NB15 as a secondary benchmark to assess cross-dataset generalization across alternative enterprise graph structures.'''
    ),

    (
r'''The resulting cleaned benchmark comprises exactly 1,377,837 NetFlow flow records.''',
r'''Following this filtering step, the cleaned evaluation benchmark contains exactly 1,377,837 NetFlow records.'''
    ),

    (
r'''NF-UNSW-NB15 contains 1,550,712 NetFlow V9 records spanning ten distinct categories: one benign class and nine intrusion classes.''',
r'''The NF-UNSW-NB15 benchmark encompasses 1,550,712 NetFlow V9 flow records divided across ten categories: one benign baseline and nine distinct attack categories.'''
    ),

    (
r'''\caption{NF-UNSW-NB15 Benchmark Class Distribution across 5-Fold Signature-Grouped Split.}''',
r'''\caption{NF-UNSW-NB15 Class Distribution under 5-Fold Signature-Grouped Partitioning.}'''
    ),

    (
r'''Raw network telemetry logs cumulative TCP connection flags as a single integer (\texttt{TCP\_FLAGS}) representing the bitwise OR of all control bits observed across the flow. In raw form, integer representation conceals critical connection handshake dynamics. For example, a \texttt{TCP\_FLAGS} value of 18 corresponds to $\text{SYN} + \text{ACK}$ ($16 + 2$), while a value of 24 corresponds to $\text{PSH} + \text{ACK}$ ($16 + 8$). Treating \texttt{TCP\_FLAGS} as a continuous scalar introduces erroneous numeric distance metrics into neural network convolutions.''',
r'''Raw flow telemetry stores cumulative TCP control flags as an aggregate integer (\texttt{TCP\_FLAGS}) computed via the bitwise OR of individual packet headers. In this raw form, connection handshake states are obscured: for instance, a value of 18 indicates $\text{SYN} + \text{ACK}$ ($16 + 2$), while 24 denotes $\text{PSH} + \text{ACK}$ ($16 + 8$). Interpreting \texttt{TCP\_FLAGS} as a continuous scalar imposes artificial metric distances that distort neural network learning.'''
    ),

    (
r'''To expose granular transport layer state semantics, we implement bitwise mask extraction in accordance with RFC 793 specifications~\cite{postel1981tcp}. The integer field is mapped to six discrete binary indicator features:
\begin{itemize}
    \item \textbf{FIN} (bit 0, mask \texttt{0x01}): Connection teardown flag
    \item \textbf{SYN} (bit 1, mask \texttt{0x02}): Connection synchronization handshake flag
    \item \textbf{RST} (bit 2, mask \texttt{0x04}): Connection reset abort flag
    \item \textbf{PSH} (bit 3, mask \texttt{0x08}): Push data buffer to application layer flag
    \item \textbf{ACK} (bit 4, mask \texttt{0x10}): Acknowledgment received flag
    \item \textbf{URG} (bit 5, mask \texttt{0x20}): Urgent pointer field significant flag
\end{itemize}''',
r'''To represent transport-layer protocol semantics explicitly, we extract binary flag indicators following RFC 793 standards~\cite{postel1981tcp}, decomposing the integer into six distinct indicator flags:
\begin{itemize}
    \item \textbf{FIN} (bit 0, mask \texttt{0x01}): Connection termination indicator
    \item \textbf{SYN} (bit 1, mask \texttt{0x02}): Synchronization handshake initiator
    \item \textbf{RST} (bit 2, mask \texttt{0x04}): Connection reset notification
    \item \textbf{PSH} (bit 3, mask \texttt{0x08}): Immediate application buffer push
    \item \textbf{ACK} (bit 4, mask \texttt{0x10}): Acknowledgment verification flag
    \item \textbf{URG} (bit 5, mask \texttt{0x20}): Urgent pointer data indicator
\end{itemize}'''
    ),

    (
r'''Continuous flow attributes---such as \texttt{IN\_BYTES}, \texttt{OUT\_BYTES}, \texttt{IN\_PKTS}, \texttt{OUT\_PKTS}, and \texttt{FLOW\_DURATION\_MS}---exhibit extreme positive skewness, with values spanning up to eight orders of magnitude. To stabilize stochastic gradient optimization, we apply a logarithmic transformation:
\begin{equation}
x_{\text{scaled}} = \log(x + 1), \quad z = \frac{x_{\text{scaled}} - \mu}{\sigma}
\end{equation}
where mean $\mu$ and standard deviation $\sigma$ are computed strictly over the training folds to eliminate test leakage.''',
r'''Continuous attributes including \texttt{IN\_BYTES}, \texttt{OUT\_BYTES}, \texttt{IN\_PKTS}, \texttt{OUT\_PKTS}, and \texttt{FLOW\_DURATION\_MS} exhibit heavy right-skewed distributions spanning multiple orders of magnitude. To stabilize gradient descent, we log-transform and standardize each continuous feature:
\begin{equation}
x_{\text{scaled}} = \log(x + 1), \quad z = \frac{x_{\text{scaled}} - \mu}{\sigma}
\end{equation}
with scaling parameters $\mu$ and $\sigma$ estimated exclusively on training splits to prevent evaluation leakage.'''
    ),

    (
r'''Rather than forcing a single GNN encoder to process all heterogeneous features simultaneously, we engineer three domain-specialized sub-feature vectors designed to isolate orthogonal attack dynamics:''',
r'''Instead of passing all heterogeneous attributes through a single monolithic encoder, we partition features into three specialized subsets corresponding to distinct traffic properties:'''
    ),

    (
r'''    \item \textbf{Temporal Feature Set (21 features)}: Encodes dynamic flow rates, packet arrival rates (\texttt{IN\_PKTS} / duration), byte rates (\texttt{IN\_BYTES} / duration), forward packet proportion, and log-transformed duration. This detector specializes in identifying volumetric surges, including DDoS and DoS.''',
r'''    \item \textbf{Temporal Feature Set (21 features)}: Captures dynamic packet and byte transmission rates, flow duration, and directional packet ratios, designed to isolate volumetric floods such as DDoS and DoS.'''
    ),

    (
r'''For each client dataset, we construct a directed communication graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \boldsymbol{X})$. Vertices $\mathcal{V} = \{v_0, \dots, v_{N-1}\}$ represent unique IPv4 host addresses observed in local telemetry. Directed edges $\mathcal{E} \subseteq \mathcal{V} \times \mathcal{V}$ represent observed NetFlow conversations directed from source IP to destination IP. Edge attribute vectors $\boldsymbol{e}_{uv} \in \mathbb{R}^{d_e}$ contain the normalized domain-specialized flow features. Because message passing in Graph Attention Networks originates from vertex representations, initial node feature vectors $\boldsymbol{x}_u \in \mathbb{R}^{d_e}$ are computed by aggregating all incident edge attributes:
\begin{equation}
\boldsymbol{x}_u = \frac{1}{\text{deg}(u)} \sum_{(u, v) \in \mathcal{E}} \boldsymbol{e}_{uv}
\label{eq:node_init}
\end{equation}
where $\text{deg}(u)$ is the in-out degree of host $u$. This formulation establishes initial host representations reflecting average communication behaviors. IP addresses are strictly mapped to integer node indices ($0$ to $N-1$) and do not enter model inputs as features, ensuring structural generalizability.''',
r'''From each client's flow logs, we construct a directed communication graph $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \boldsymbol{X})$. Vertices $\mathcal{V} = \{v_0, \dots, v_{N-1}\}$ correspond to observed IPv4 host addresses, while directed edges $(u, v) \in \mathcal{E}$ represent NetFlow sessions from source to destination. Edge feature vectors $\boldsymbol{e}_{uv} \in \mathbb{R}^{d_e}$ store normalized domain-specific attributes. Because standard GAT convolutions initiate message passing at vertices, initial node representations $\boldsymbol{x}_u \in \mathbb{R}^{d_e}$ are computed by averaging incident edge features:
\begin{equation}
\boldsymbol{x}_u = \frac{1}{\text{deg}(u)} \sum_{(u, v) \in \mathcal{E}} \boldsymbol{e}_{uv}
\label{eq:node_init}
\end{equation}
where $\text{deg}(u)$ denotes the combined degree of vertex $u$. Host IP strings are re-indexed to integer identifiers ($0$ to $N-1$) and excluded from model inputs to preserve topological generalizability.'''
    ),

    (
r'''We executed an empirical leakage audit comparing uniform random row splitting against our signature-grouped protocol on the 1,377,837 flows of NF-ToN-IoT.''',
r'''To quantify evaluation leakage, we audited uniform random row splitting against our signature-grouped protocol across the 1,377,837 flows of NF-ToN-IoT.'''
    ),

    (
r'''To simulate authentic decentralized enterprise conditions, the training dataset of 1,102,269 clean flows was partitioned across $K = 5$ federated edge clients following a non-IID Dirichlet distribution $\text{Dir}(\alpha)$ with concentration parameter $\alpha = 0.5$~\cite{hsu2019noniid, zhao2018federated}, combined with source subnet clustering based on \texttt{IPV4\_SRC\_ADDR}. Under this heterogeneous partitioning, rare attack categories---such as Backdoor and DoS---are completely absent from certain clients during specific communication rounds, replicating the severe class starvation encountered in real-world decentralized deployments.''',
r'''To reflect realistic decentralized conditions, the 1,102,269 training flows were distributed across $K = 5$ federated edge clients using a non-IID Dirichlet distribution ($\alpha = 0.5$) combined with source-subnet clustering on \texttt{IPV4\_SRC\_ADDR}~\cite{hsu2019noniid, zhao2018federated}. This partition produces realistic label skew where rare categories (such as Backdoor and DoS) are absent from certain clients, reproducing the class starvation common in edge settings.'''
    ),

    (
r'''All simulation pipelines were implemented in Python 3.12 utilizing PyTorch 2.2.0 and PyTorch Geometric (PyG) 2.5.0 for deep graph convolutional operations. Community partitioning was executed using the C-optimized \texttt{python-leidenalg} 0.10.2 library implementing the Constant Potts Model. Tabular data wrangling, preprocessing, and Random Forest ensemble modeling were executed via Scikit-learn 1.4.1 and Pandas 2.2.0. Distributed federated training was simulated on an NVIDIA Tesla T4 GPU accelerator (16 GB GDDR6 VRAM, CUDA 12.2) hosted on an Intel Xeon server with 32 GB DDR4 RAM running Ubuntu 22.04 LTS. Multi-seed experiments were orchestrated via deterministic bash and python harnesses enforcing fixed seeds ($42, 43, 44$ on NF-ToN-IoT, and $42$ to $46$ on NF-UNSW-NB15) across all PyTorch, NumPy, and Scikit-learn random generators.''',
r'''The experimental framework was implemented in Python 3.12 using PyTorch 2.2.0 and PyTorch Geometric 2.5.0 for graph neural network operations. Graph community partitioning was conducted via the C-optimized \texttt{python-leidenalg} library (v0.10.2) optimizing the Constant Potts Model. Preprocessing and ensemble modeling were handled via Scikit-learn 1.4.1 and Pandas 2.2.0. Federated training was executed on an NVIDIA Tesla T4 GPU (16 GB GDDR6, CUDA 12.2) hosted on an Intel Xeon 2.20 GHz system with 32 GB RAM running Ubuntu 22.04 LTS. Multi-seed experiments were orchestrated with deterministic random states (seeds 42--44 for NF-ToN-IoT and seeds 42--46 for NF-UNSW-NB15) across PyTorch, NumPy, and Scikit-learn.'''
    ),

    # ==========================================
    # 8. CHAPTER 4: METHODOLOGY (Pages 37-45)
    # ==========================================
    (
r'''\textbf{Centralized Tabular Architectures}: Conventional machine learning intrusion detection relies on tabular classifiers---predominantly Random Forests~\cite{breiman2001randomforests} and Gradient Boosted Decision Trees (XGBoost, LightGBM)---trained over centralized NetFlow tables. In these architectures, each network flow record is treated as an isolated, independent vector $\boldsymbol{x} \in \mathbb{R}^D$. Decision trees perform greedy recursive partitioning of the feature space by optimizing impurity criteria along individual feature axes:
\begin{equation}
\theta^* = \arg\min_{j, t} \left[ \frac{N_L}{N} G(\mathcal{D}_L) + \frac{N_R}{N} G(\mathcal{D}_R) \right]
\end{equation}
where split threshold $t$ on feature $j$ divides dataset $\mathcal{D}$ into subsets $\mathcal{D}_L$ and $\mathcal{D}_R$. Because decision trees construct orthogonal, axis-aligned hyperplanes, they excel at detecting volumetric anomalies governed by sharp threshold criteria (such as packet rate spikes or payload size imbalances). However, centralized tabular models suffer from two fatal flaws: (1) They require centralizing unencrypted network telemetry across all enterprise edge gateways, directly violating data privacy mandates (GDPR/HIPAA); and (2) They are structurally oblivious to graph topology, leaving them blind to coordinated multi-host reconnaissance, slow distributed port scans, and multi-hop botnet lateral movement.''',
r'''\textbf{Centralized Tabular Architectures}: Standard machine learning NIDS approaches commonly employ tabular ensemble classifiers, such as Random Forests~\cite{breiman2001randomforests} or gradient-boosted trees, trained on consolidated NetFlow repositories. In these setups, each flow is modeled as an independent vector $\boldsymbol{x} \in \mathbb{R}^D$. Decision trees recursively partition the input space by minimizing node impurity along individual feature dimensions:
\begin{equation}
\theta^* = \arg\min_{j, t} \left[ \frac{N_L}{N} G(\mathcal{D}_L) + \frac{N_R}{N} G(\mathcal{D}_R) \right]
\end{equation}
where threshold $t$ on feature $j$ splits dataset $\mathcal{D}$ into subsets $\mathcal{D}_L$ and $\mathcal{D}_R$. While axis-aligned splits effectively detect volumetric anomalies governed by clear numerical thresholds (such as packet bursts), centralized tabular approaches face two fundamental limitations: (1) They necessitate pooling unencrypted flow records at a central server, conflicting with privacy frameworks; and (2) They disregard graph relational context, making them less capable of detecting multi-host reconnaissance or distributed lateral movement across subnets.'''
    ),

    (
r'''\textbf{Standard Federated NIDS Architectures}: To address privacy constraints, existing federated intrusion detection architectures combine the canonical Federated Averaging (\texttt{FedAvg}) algorithm with shallow multi-layer perceptrons (MLPs) or 1D-Convolutional Neural Networks (CNNs). In these systems, local clients compute gradient updates over local mini-batches using standard unweighted Cross-Entropy loss:
\begin{equation}
\mathcal{L}_{\text{CE}} = - \sum_{c=1}^C y_c \log(p_c)
\end{equation}
During federated communication rounds, the central coordinator aggregates client weight vectors proportionally to client sample counts:
\begin{equation}
W_{\text{global}} = \sum_{k=1}^K \left( \frac{n_k}{n} \right) W_k
\end{equation}
However, standard FedNIDS frameworks continue to treat network telemetry as independent tabular instances.''',
r'''\textbf{Standard Federated NIDS Architectures}: To preserve privacy, federated intrusion detection architectures typically combine the Federated Averaging (\texttt{FedAvg}) protocol with multi-layer perceptrons or 1D convolutional models. Participating clients compute gradient updates locally using standard cross-entropy loss:
\begin{equation}
\mathcal{L}_{\text{CE}} = - \sum_{c=1}^C y_c \log(p_c)
\end{equation}
Across communication rounds, the central server aggregates client weights weighted by local dataset volumes:
\begin{equation}
W_{\text{global}} = \sum_{k=1}^K \left( \frac{n_k}{n} \right) W_k
\end{equation}
However, typical federated setups still model traffic as independent tabular instances.'''
    ),

    (
r'''Finally, a Random Forest meta-classifier trained strictly on concatenated detector probability vectors ($3 \times C$) performs final classification.''',
r'''Finally, an ensemble Random Forest meta-classifier trained on the concatenated probability outputs of the detectors ($3 \times C$) outputs the final class assignment.'''
    ),

    (
r'''To comprehensively resolve the structural pathologies identified in prior art, we formulate a contrastive hybrid federated Graph Neural Network framework engineered specifically for highly imbalanced, non-IID IoT network intrusion detection. 

Our architecture fundamentally transforms decentralized graph learning through four core innovations:
\begin{enumerate}
    \item \textbf{Audited Zero-Leakage Protocol}: An audited 8-tuple StratifiedGroupKFold partitioning protocol that enforces absolute $0.00\%$ signature leakage.
    \item \textbf{Domain-Specialized GAT Client Detectors}: Three dedicated GAT models (Temporal, Content, Behavioral) that prevent feature interference across distinct attack modes.
    \item \textbf{Supervised Contrastive Loss ($\mu = 0.1$)}: A mathematically grounded metric regularizer that exerts active repulsion to prevent minority manifold collapse.
    \item \textbf{Two-Stage Random Forest Meta-Learner}: An ensemble classifier that arbitrates continuous GNN detector logits using deterministic physical NetFlow feature thresholds.
\end{enumerate}''',
r'''To address these limitations, we formulate a contrastive hybrid federated GNN framework designed for intrusion detection under non-IID conditions and severe class skew.

The architecture incorporates four primary design elements:
\begin{enumerate}
    \item \textbf{Audited Zero-Leakage Protocol}: A signature-grouped 5-fold cross-validation scheme ensuring $0.00\%$ flow-signature leakage between training and evaluation folds.
    \item \textbf{Domain-Specialized GAT Client Detectors}: Three specialized GAT client models (Temporal, Content, and Behavioral) that prevent feature interference across distinct intrusion mechanisms.
    \item \textbf{Supervised Contrastive Loss ($\mu = 0.1$)}: A metric regularizer on continuous edge representations that creates angular repulsion between overlapping class manifolds.
    \item \textbf{Two-Stage Random Forest Meta-Learner}: An ensemble meta-classifier combining continuous GNN probability vectors with raw physical NetFlow attributes to enforce robust decision boundaries.
\end{enumerate}'''
    ),

    (
r'''This section details the formal mathematical equations governing every stage of our proposed contrastive hybrid federated architecture.''',
r'''This section presents the mathematical formulations that define the client encoders, loss objectives, server overlay, and downstream arbitration layers.'''
    ),

    (
r'''Rather than forcing a single monolithic GNN to process all heterogeneous NetFlow features simultaneously, our client architecture deploys three specialized Graph Attention Network (GAT) models at each edge client node $k \in \{1, \dots, K\}$, each dedicated to an orthogonal functional domain:''',
r'''To isolate orthogonal attack signatures without cross-feature interference, each client $k \in \{1, \dots, K\}$ trains three specialized Graph Attention Network (GAT) models dedicated to distinct feature domains:'''
    ),

    (
r'''where $p_t$ is the model's estimated probability for the ground-truth class. Focal modulation depresses gradient magnitudes from easy, high-confidence majority samples (where $p_t \to 1$), forcing optimization to prioritize ambiguous boundary flows.''',
r'''where $p_t$ is the predicted probability for the target class. Focal modulation suppresses the loss gradients of confident majority samples ($p_t \to 1$), ensuring that backpropagation focuses primarily on boundary and hard-to-classify flows.'''
    ),

    (
r'''While CB-Focal loss dynamically modulates gradient magnitudes, it does not alter the geometric layout of representations in the continuous latent space.''',
r'''Although CB-Focal loss dynamically scales gradient magnitudes, it does not directly optimize the angular separation of embeddings in continuous latent space.'''
    ),

    (
r'''\textbf{Mathematical Derivation of Contrastive Repulsive Dynamics}: The gradient of $\mathcal{L}_{\text{SupCon}}$ with respect to normalized embedding $\tilde{\boldsymbol{z}}_i$ is derived as:''',
r'''\textbf{Gradient Dynamics of Contrastive Regularization}: Differentiating $\mathcal{L}_{\text{SupCon}}$ with respect to the normalized edge embedding $\tilde{\boldsymbol{z}}_i$ yields:'''
    ),

    (
r'''\textbf{Two-Stage Random Forest Meta-Classifier}: For final decision arbitration, we deploy an ensemble Random Forest meta-classifier consisting of 100 balanced decision trees (max depth 20). For each test flow $i$, the meta-feature input vector $\boldsymbol{\phi}_i$ concatenates:
\begin{equation}
\begin{split}
\boldsymbol{\phi}_i = \big[ & \boldsymbol{P}_{\text{temp}}(i) \,\|\, \boldsymbol{P}_{\text{cont}}(i) \,\|\, \boldsymbol{P}_{\text{behav}}(i) \,\|\, \\
& \boldsymbol{y}_{\text{pred}} \,\|\, \boldsymbol{conf} \,\|\, \boldsymbol{x}_{\text{raw}}(i) \big]
\end{split}
\label{eq:meta_vec}
\end{equation}
where $\boldsymbol{P}_d(i) \in \mathbb{R}^8$ are the softmax output probability vectors from the three specialized GAT detectors ($24$ dims), $\boldsymbol{y}_{\text{pred}} \in \mathbb{R}^3$ are detector argmax indices, $\boldsymbol{conf} \in \mathbb{R}^3$ are maximum confidence values, and $\boldsymbol{x}_{\text{raw}}(i) \in \mathbb{R}^{21}$ represents the normalized physical NetFlow attribute vector. Fusing raw flow features directly into the meta-classifier provides critical deterministic physical threshold checks (e.g., exact packet rates and byte asymmetries) that resolve ambiguities in continuous GNN logits.''',
r'''\textbf{Two-Stage Random Forest Meta-Classifier}: To arbitrate final flow classifications, an ensemble Random Forest of 100 balanced trees (maximum depth 20) evaluates a fused feature vector $\boldsymbol{\phi}_i$:
\begin{equation}
\begin{split}
\boldsymbol{\phi}_i = \big[ & \boldsymbol{P}_{\text{temp}}(i) \,\|\, \boldsymbol{P}_{\text{cont}}(i) \,\|\, \boldsymbol{P}_{\text{behav}}(i) \,\|\, \\
& \boldsymbol{y}_{\text{pred}} \,\|\, \boldsymbol{conf} \,\|\, \boldsymbol{x}_{\text{raw}}(i) \big]
\end{split}
\label{eq:meta_vec}
\end{equation}
where $\boldsymbol{P}_d(i) \in \mathbb{R}^8$ denotes the class probability vector from each GAT model (24 dimensions total), $\boldsymbol{y}_{\text{pred}} \in \mathbb{R}^3$ contains individual model argmax predictions, $\boldsymbol{conf} \in \mathbb{R}^3$ stores maximum confidence scores, and $\boldsymbol{x}_{\text{raw}}(i) \in \mathbb{R}^{21}$ provides the normalized NetFlow features. Including raw features alongside model probabilities supplies the tree ensemble with exact continuous thresholds (such as packet arrival rates and byte ratios), resolving ambiguities in continuous GNN logits.'''
    ),

    # ==========================================
    # 9. CHAPTER 5: RESULTS AND DISCUSSION (Pages 47-54)
    # ==========================================
    (
r'''Table~\ref{tab:system_config} summarizes the complete configuration.''',
r'''The complete hardware and hyperparameter configuration is summarized in Table~\ref{tab:system_config}.'''
    ),

    (
r'''In our proposed architecture incorporating Supervised Contrastive regularization ($\mu = 0.1$), the catastrophic Backdoor collapse is completely resolved. Correct Backdoor detections jump from 6 to 3,419 flows ($99.51\%$ recall in Seed 42, averaging $99.57\%$ across all seeds). Misclassifications into Injection drop from 3,430 to merely 17 flows (a $99.5\%$ reduction in false negatives). Furthermore, correct Scanning detections increase from 3,064 to 4,005 flows ($94.08\%$ recall in Seed 42, averaging $97.98\%$ across seeds), demonstrating that contrastive metric repulsion cleanly decouples minority attack representations from adjacent majority clusters.''',
r'''Under the proposed architecture with Supervised Contrastive regularization ($\mu = 0.1$), the Backdoor detection failure is largely mitigated. Correctly identified Backdoor flows rise from 6 to 3,419 in Seed 42 (yielding $99.51\%$ recall, and averaging $99.57\%$ across all evaluated seeds). Misclassifications into Injection fall from 3,430 to 17 flows, representing a $99.5\%$ decrease in false negatives for this category. In addition, Scanning recall improves from $80.80\%$ to $97.98\%$ across seeds (reaching 4,005 correct flows in Seed 42), demonstrating that metric repulsion effectively separates minority embeddings from dominant clusters.'''
    ),

    (
r'''\caption{Confusion Matrix Heatmaps on NF-ToN-IoT: Anchor (Plain CE) vs Proposed Framework ($\mu=0.1$).}''',
r'''\caption{Confusion Matrix Comparisons on NF-ToN-IoT: Unweighted Cross-Entropy Anchor vs Proposed Framework ($\mu=0.1$).}'''
    ),

    (
r'''Table~\ref{tab:headline_results} summarizes the headline empirical performance across three independent random seeds ($42, 43$, and $44$) on the official NF-ToN-IoT benchmark under the zero-leakage signature-grouped split. All reported values represent the sample mean $\pm$ standard deviation strictly computed from the verified multi-seed execution result logs.''',
r'''Table~\ref{tab:headline_results} reports the mean performance and standard deviations across three independent random seeds (seeds 42, 43, and 44) on NF-ToN-IoT under the audited signature-grouped protocol.'''
    ),

    (
r'''\textbf{Performance Analysis}: The baseline GNN Anchor achieves an overall Balanced Accuracy of $78.11 \pm 2.01\%$ and an unacceptable Macro FNR of $21.89 \pm 2.01\%$. Adding Class-Balanced Focal loss and edge interpolation without contrastive regularization ($\mu = 0.0$) yields only modest gains, raising Balanced Accuracy to $80.69 \pm 1.64\%$ and reducing Macro FNR to $19.31 \pm 1.64\%$; however, Backdoor recall remains suppressed at $0.80 \pm 0.15\%$.

In sharp contrast, our proposed architecture incorporating Supervised Contrastive regularization at $\mu = 0.1$ delivers dramatic, statistically confirmed improvements across all critical metrics:
\begin{itemize}
    \item \textbf{Macro FNR}: Plummets from $21.89 \pm 2.01\%$ to $\mathbf{5.72 \pm 1.20\%}$, cutting missed intrusions by nearly four-fold.''',
r'''\textbf{Performance Analysis}: The baseline GNN Anchor records a Balanced Accuracy of $78.11 \pm 2.01\%$ with a high Macro FNR of $21.89 \pm 2.01\%$. Introducing Class-Balanced Focal loss and edge interpolation without contrastive regularization ($\mu = 0.0$) improves Balanced Accuracy marginally to $80.69 \pm 1.64\%$ and lowers Macro FNR to $19.31 \pm 1.64\%$, yet Backdoor recall remains minimal at $0.80 \pm 0.15\%$.

Conversely, integrating Supervised Contrastive regularization at $\mu = 0.1$ produces substantial improvements across detection metrics:
\begin{itemize}
    \item \textbf{Macro FNR}: Decreases from $21.89 \pm 2.01\%$ to $\mathbf{5.72 \pm 1.20\%}$, substantially lowering overall missed attacks.'''
    ),

    (
r'''To rigorously identify which classes drove the headline improvement, we perform a mathematical decomposition of the $+13.59\%$ Balanced Accuracy gain achieved from $\mu = 0.0$ to $\mu = 0.1$:''',
r'''To determine which categories account for the overall performance gain, we decompose the $+13.59\%$ Balanced Accuracy increase observed between $\mu = 0.0$ and $\mu = 0.1$:'''
    ),

    (
r'''Table~\ref{tab:gain_decomposition} presents the class-by-class contribution. The decomposition reveals an extraordinary finding: exactly $\mathbf{90.85\%}$ of the total Balanced Accuracy improvement ($+12.35$ absolute percentage points) is driven solely by the single-class rescue of Backdoor intrusions (jumping from $0.80\%$ to $99.57\%$ recall). Scanning contributes $7.41\%$ ($+1.01$ points), while Password exhibits a slight $-1.81\%$ drop ($-0.23$ points). This confirms that Supervised Contrastive Loss functions as an exquisitely targeted topological remedy that eliminates minority manifold collapse.''',
r'''Table~\ref{tab:gain_decomposition} details each class's contribution. Notably, $\mathbf{90.85\%}$ of the total Balanced Accuracy improvement ($+12.35$ percentage points) stems directly from recovering Backdoor detection (rising from $0.80\%$ to $99.57\%$ recall). Scanning provides an additional $7.41\%$ share ($+1.01$ points), whereas Password shows a slight $1.81\%$ reduction ($-0.23$ points). These results indicate that contrastive regularization primarily addresses minority-manifold overlap rather than shifting decision boundaries across all classes uniformly.'''
    ),

    (
r'''To isolate the individual contribution of each proposed architectural module, we conducted four systematic ablation experiments grounded strictly in saved execution artifacts across three random seeds.

\subsection{Cumulative Component Ablation Progression}
Table~\ref{tab:ablation_progression} tracks the step-by-step ablation progression from the baseline GNN anchor to the full proposed pipeline under the signature-grouped split:
\begin{itemize}
    \item \textbf{Step (a) (Plain CE Anchor with Class-Balanced Sampler)}: Achieves $78.11 \pm 2.46\%$ BalAcc. Note that even with class-balanced mini-batch sampling active ($M = 64$ samples per class), Backdoor recall collapses to $0.11\%$, proving that mini-batch sampling alone cannot prevent manifold collapse in continuous GNN space.
    \item \textbf{Step (b) (+ Class-Balanced Focal Loss)}: Re-weighting by effective sample volume without interpolation yields $76.79 \pm 10.16\%$ BalAcc with acute seed variance on Backdoor ($33.82 \pm 57.14\%$), demonstrating that loss re-weighting alone destabilizes optimization without metric separation.
    \item \textbf{Step (c) (+ Edge Interpolation, $\mu = 0.0$)}: Intra-class edge Mixup stabilizes optimization variance (Std drops to $\pm 2.01\%$), but Backdoor recall remains severely suppressed at $0.80 \pm 0.18\%$.
    \item \textbf{Step (d) (+ SupCon $\mu = 0.1$, Full Proposed Pipeline)}: Introducing contrastive metric regularization triggers the definitive breakthrough, elevating BalAcc by $+13.59\%$ to $94.28 \pm 1.47\%$ and driving Backdoor recall to $99.57 \pm 0.20\%$.
    \item \textbf{Step (e) (Full Model with RF Detector-Only / No Raw Features)}: Withholding raw flow features from the meta-classifier causes BalAcc to collapse by $-44.60\%$ (down to $49.68 \pm 13.97\%$), proving that downstream decision trees rely decisively on physical NetFlow thresholds.
\end{itemize}''',
r'''To evaluate each module's contribution, we analyze ablation configurations across three random seeds using the signature-grouped protocol.

\subsection{Cumulative Component Ablation Progression}
Table~\ref{tab:ablation_progression} summarizes the progression from the baseline anchor to the complete pipeline:
\begin{itemize}
    \item \textbf{Step (a) (Plain CE Anchor with Class-Balanced Sampler)}: Achieves $78.11 \pm 2.46\%$ Balanced Accuracy. Even with class-balanced mini-batches ($M = 64$ samples per class), Backdoor recall drops to $0.11\%$, indicating that balanced batch sampling alone does not resolve manifold overlap in continuous embedding space.
    \item \textbf{Step (b) (+ Class-Balanced Focal Loss)}: Effective sample re-weighting without interpolation results in $76.79 \pm 10.16\%$ Balanced Accuracy with elevated seed variance on Backdoor ($33.82 \pm 57.14\%$), showing that scalar loss adjustments can destabilize training absent geometric constraints.
    \item \textbf{Step (c) (+ Edge Interpolation, $\mu = 0.0$)}: Intra-class edge interpolation lowers optimization variance ($\pm 2.01\%$), yet Backdoor recall remains limited to $0.80 \pm 0.18\%$.
    \item \textbf{Step (d) (+ SupCon $\mu = 0.1$, Full Proposed Pipeline)}: Adding contrastive regularization yields the primary gain, increasing Balanced Accuracy by $+13.59\%$ to $94.28 \pm 1.47\%$ and raising Backdoor recall to $99.57 \pm 0.20\%$.
    \item \textbf{Step (e) (Full Model with RF Detector-Only / No Raw Features)}: Removing raw NetFlow attributes from the Random Forest meta-learner causes Balanced Accuracy to drop by $44.60\%$ (to $49.68 \pm 13.97\%$), underscoring the role of physical numerical thresholds in resolving logit ambiguities.
\end{itemize}'''
    ),

    (
r'''To test our core hypothesis---that averaging flow attributes onto IP nodes during graph construction is directly responsible for suppressing Backdoor recall---we conducted a controlled experiment comparing the full GNN against an Edge-Only model where node message passing was disabled (Table~\ref{tab:node_averaging_test}). In the Edge-Only configuration, flow classifications are made directly on edge attributes without graph neighborhood aggregation.''',
r'''To evaluate whether aggregating flow attributes onto host vertices causes the Backdoor detection failure, we compared the GNN against an Edge-Only baseline that bypasses neighborhood message passing (Table~\ref{tab:node_averaging_test}). In this configuration, flows are classified directly from edge attributes without graph convolutions.'''
    ),

    (
r'''This definitively proves our hypothesis: topological graph feature averaging causes catastrophic minority collapse, which either requires Supervised Contrastive metric repulsion ($\mu = 0.1$) to overcome or edge-only classification to avoid.''',
r'''This supports the hypothesis that recursive feature pooling on multi-service endpoints dilutes low-volume attack vectors, requiring either metric-space separation ($\mu = 0.1$) or localized edge-level inference to retain detection capability.'''
    ),

    (
r'''Fig.~\ref{fig:sensitivity_curve} illustrates the empirical sensitivity curve across regularization weights $\mu \in \{0.0, 0.1, 0.3, 0.5\}$. At $\mu = 0.0$, the model lacks metric repulsion, resulting in Backdoor collapse ($0.80\%$ recall).''',
r'''Fig.~\ref{fig:sensitivity_curve} plots detection metrics across regularization weights $\mu \in \{0.0, 0.1, 0.3, 0.5\}$. Setting $\mu = 0.0$ omits metric regularization, leaving Backdoor recall at $0.80\%$.'''
    ),

    (
r'''\textbf{Findings on NF-UNSW-NB15}: The baseline Anchor achieved $79.91 \pm 9.99\%$ Balanced Accuracy with 2 collapsed seeds (Seeds 44 and 46). Under $\mu = 0.1$, Seeds 43 and 44 achieved extraordinary Balanced Accuracies exceeding $94\%$ ($95.87\%$ and $94.18\%$), but Seeds 42, 45, and 46 experienced optimization collapse, resulting in an aggregate mean of $55.30 \pm 38.61\%$ BalAcc. Paired t-tests ($t = 0.326, p = 0.761$) indicate that contrastive hyperparameter tuning (specifically temperature $\tau$ and batch quota $M$) is highly sensitive to dataset-specific graph densities, highlighting that contrastive regularization must be calibrated to local subnet clustering coefficients.''',
r'''\textbf{Cross-Dataset Observations on NF-UNSW-NB15}: The baseline Anchor recorded $79.91 \pm 9.99\%$ Balanced Accuracy, with two seeds underperforming. At $\mu = 0.1$, Seeds 43 and 44 achieved strong Balanced Accuracies of $95.87\%$ and $94.18\%$, whereas Seeds 42, 45, and 46 exhibited training instability, yielding a mean of $55.30 \pm 38.61\%$. A paired comparison ($t = 0.326, p = 0.761$) highlights that contrastive parameters (such as temperature $\tau$ and batch size $M$) interact with local graph density and require dataset-specific calibration when migrating across topologies.'''
    ),

    (
r'''Because volumetric classes outnumber stealthy intrusions by $27:1$, gradient updates from majority classes overwhelmingly govern the optimization trajectory.''',
r'''Because volumetric attacks heavily outnumber low-frequency intrusions (over $27:1$), majority-class error terms predominantly guide parameter updates during backpropagation.'''
    ),

    (
r'''Supervised Contrastive Loss overcomes this gradient starvation by establishing an active metric repulsive force proportional to $-\tilde{\boldsymbol{z}}_a / \tau$. When paired with dynamic class-balanced mini-batch sampling ($M = 64$ samples per class), every optimization step contains equal numbers of positive anchor pairs for minority and majority classes. The repulsive force pushes negative pairs apart, carving out an isolated, orthogonal subspace for rare intrusions and eliminating the $99.83\%$ Backdoor-to-Injection misclassification.''',
r'''Supervised Contrastive Loss counteracts this gradient dominance by exerting an active repulsive force proportional to $-\tilde{\boldsymbol{z}}_a / \tau$ between differing classes. When coupled with dynamic class-balanced batching ($M = 64$ samples per class), each step provides balanced positive and negative pairs across all categories. The resulting repulsion isolates minority embeddings from neighboring majority clusters, largely eliminating the misclassification of Backdoors as Injections.'''
    ),

    (
r'''\textbf{Centralized Tabular vs. Federated Graph Trade-Off}: A critical operational comparison emerges between centralized tabular classifiers (Configuration 1, achieving $97.53 \pm 0.46\%$ BalAcc) and our proposed federated GNN (achieving $94.28 \pm 1.20\%$ BalAcc). While centralized tabular models achieve slightly higher accuracy, they require aggregating unencrypted network telemetry at a central repository, directly violating enterprise data privacy regulations (GDPR/HIPAA). In contrast, our federated GNN confines raw telemetry to local edge gateways, transmitting solely privacy-preserving community centroids. Furthermore, tabular models rely on static feature thresholds that are vulnerable to adversarial packet-padding evasion, whereas relational GNNs capture structural multi-hop interaction patterns, conferring resilience against coordinated attack campaigns.''',
r'''\textbf{Centralized Tabular vs. Federated Graph Trade-Off}: Comparing centralized tabular baselines ($97.53 \pm 0.46\%$ Balanced Accuracy) with the proposed federated GNN ($94.28 \pm 1.20\%$) highlights key operational trade-offs. Centralized models offer high detection precision on known numerical thresholds but require aggregating unencrypted telemetry centrally, conflicting with data privacy regulations such as GDPR and HIPAA. In contrast, the federated GNN retains raw NetFlow data locally, sharing only abstract community centroids. Additionally, while tabular models depend on fixed feature thresholds vulnerable to payload obfuscation, graph architectures capture relational interaction patterns across communication endpoints.'''
    ),

    # ==========================================
    # 10. CHAPTER 6: CONCLUSION AND FUTURE DIRECTIONS (Pages 56-57)
    # ==========================================
    (
r'''Driven by the critical necessity to overcome the dual challenges of data privacy preservation and acute class imbalance, this research conducted an exhaustive investigation into the pathologies of existing federated graph frameworks, taking the foundational FedGATSage architecture (Al-Tfaily et al., Nature Scientific Reports 2025) as a primary baseline.''',
r'''Motivated by the simultaneous demands of data privacy and extreme class imbalance, this study investigated structural failure modes in federated graph intrusion detection, using the FedGATSage pipeline (Al-Tfaily et al., 2025) as a foundational baseline.'''
    ),

    (
r'''Our code-level replication audit revealed two pervasive vulnerabilities in conventional pipelines: (1) An alarming $46.88\%$ identical communication socket signature leakage induced by naive uniform random row partitioning, which artificially inflates reported detection accuracy; and (2) A catastrophic minority class collapse under standard empirical risk minimization, wherein $99.83\%$ of rare Backdoor attacks were erroneously misclassified as Injection flows by baseline GNNs (yielding an appalling $0.11\%$ recall). Furthermore, we proved that topological feature averaging on IP endpoint nodes dilutes low-frequency intrusion signals into dominant background profiles, while heuristic Louvain partitioning produces disconnected community artifacts.''',
r'''An audit of baseline implementations identified two key vulnerabilities: (1) a $46.88\%$ socket-signature leakage rate caused by standard random row partitioning, which artificially elevates reported accuracy; and (2) severe minority-class degradation under standard cross-entropy loss, where $99.83\%$ of rare Backdoor intrusions were misclassified as Injection flows ($0.11\%$ recall). Controlled testing also demonstrated that feature averaging on multi-role IP hosts dilutes subtle attack signatures into dominant background profiles, while Louvain community clustering can generate disconnected community artifacts.'''
    ),

    (
r'''Crucially, contrastive metric regularization eliminated the catastrophic Backdoor collapse, slashing misclassifications into Injection from 3,430 to 17 flows and elevating Backdoor detection recall from $0.11 \pm 0.08\%$ to an extraordinary $99.57 \pm 0.16\%$. Through controlled hypothesis testing, we proved that topological host dilution is directly responsible for minority collapse in GNNs, establishing Supervised Contrastive metric repulsion as an indispensable mathematical remedy. This research bridges the critical divide between theoretical decentralized graph modeling and robust, leakage-free cybersecurity defense.''',
r'''Importantly, Supervised Contrastive regularization mitigated the Backdoor detection collapse, reducing Injection misclassifications from 3,430 to 17 flows and raising Backdoor recall from $0.11 \pm 0.08\%$ to $99.57 \pm 0.16\%$. Controlled experiments demonstrated that host-level feature dilution contributes significantly to minority collapse in GNNs, which contrastive metric repulsion helps correct by enforcing geometric class separation.'''
    ),

    (
r'''Our signature-grouped evaluation protocol strictly guarantees zero flow-signature leakage, but relies on shared IP address spaces across training and testing splits.''',
r'''Although the signature-grouped protocol eliminates flow-signature overlap, training and testing sets currently share the underlying IP address space.'''
    ),
]

print(f"Total replacements to check: {len(replacements)}")
all_found = True
for idx, (orig, repl) in enumerate(replacements, 1):
    count = text.count(orig)
    if count == 0:
        print(f"FAILED [{idx}]: Not found!")
        print("ORIGINAL SNIPPET:", repr(orig[:80]), "...")
        all_found = False
    elif count > 1:
        print(f"WARNING [{idx}]: Found {count} times!")
    else:
        print(f"OK [{idx}]: Unique match.")

if all_found:
    print("ALL TARGETS MATCHED UNIQUELY! Applying replacements...")
    revised_text = text
    for orig, repl in replacements:
        revised_text = revised_text.replace(orig, repl)
    
    with open('dissertation_overleaf.tex', 'w', encoding='utf-8') as f:
        f.write(revised_text)
    print("SUCCESS: dissertation_overleaf.tex updated!")
else:
    print("ABORT: Some targets did not match.")
