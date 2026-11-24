# text_ch4.py
# Chapter 4: Methodology

CHAPTER_4_TITLE = "METHODOLOGY"

SEC_4_1_TITLE = "4.1 Design / Methodology 1 of Existing Work (Centralized & Standard FedNIDS)"
SEC_4_1_PARAS = [
    (
        "To establish a rigorous comparative foundation for evaluating our proposed architecture, we first analyze the "
        "methodological designs of existing conventional approaches in network intrusion detection: centralized tabular classifiers "
        "and standard federated deep learning models."
    ),
    (
        "Centralized Tabular Architectures: Conventional machine learning intrusion detection relies on tabular classifiers—predominantly "
        "Random Forests (Breiman, 2001) and Gradient Boosted Decision Trees (XGBoost, LightGBM)—trained over centralized NetFlow tables. "
        "In these architectures, each network flow record is treated as an isolated, independent vector x in R^D. Decision trees perform greedy "
        "recursive partitioning of the feature space by optimizing impurity criteria (such as Gini impurity or Shannon entropy) along individual "
        "feature axes: theta* = argmin_{j, t} [ (N_L / N) G(D_L) + (N_R / N) G(D_R) ], where split threshold t on feature j divides dataset D into "
        "subsets D_L and D_R. Because decision trees construct orthogonal, axis-aligned hyperplanes, they excel at detecting volumetric anomalies "
        "governed by sharp threshold criteria (such as packet rate spikes or payload size imbalances). However, centralized tabular models suffer from "
        "two fatal flaws: (1) They require centralizing unencrypted network telemetry across all enterprise edge gateways, directly violating data "
        "privacy mandates (GDPR/HIPAA); and (2) They are structurally oblivious to graph topology, leaving them blind to coordinated multi-host "
        "reconnaissance, slow distributed port scans, and multi-hop botnet lateral movement."
    ),
    (
        "Standard Federated NIDS Architectures: To address privacy constraints, existing federated intrusion detection architectures combine the canonical "
        "Federated Averaging (FedAvg) algorithm with shallow multi-layer perceptrons (MLPs) or 1D-Convolutional Neural Networks (CNNs). In these systems, "
        "local clients compute gradient updates over local mini-batches using standard unweighted Cross-Entropy loss: L_{CE} = - sum_{c=1}^C y_c log(p_c). "
        "During federated communication rounds, the central coordinator aggregates client weight vectors proportionally to client sample counts: "
        "W_{global} = sum_{k=1}^K (n_k / n) W_k. However, standard FedNIDS frameworks continue to treat network telemetry as independent tabular instances. "
        "Under non-IID client skew, local parameter updates diverge along incompatible trajectories. More critically, when rare intrusions (such as Backdoors) "
        "are absent from certain clients, FedAvg parameter averaging heavily dilutes minority class weights, causing severe global false negative rates."
    )
]

SEC_4_2_TITLE = "4.2 Design / Methodology 2 of Existing Work (Base FedGATSage Framework)"
SEC_4_2_PARAS = [
    (
        "The base FedGATSage architecture proposed by Al-Tfaily et al. (2025) sought to bridge the gap between federated privacy and relational "
        "modeling by uniting client-side Graph Attention Networks (GAT), Louvain community detection, an aggregated server GraphSAGE overlay, and "
        "a Random Forest meta-classifier. In FedGATSage, each edge client constructs a local communication graph G_k = (V_k, E_k) where vertices "
        "represent IP hosts and directed edges represent network flows. Node feature vectors are initialized via incident edge feature averaging: "
        "x_u = (1 / deg(u)) sum_{(u, v) in E} e_{uv}."
    ),
    (
        "Client Representation Learning: Local client training in FedGATSage employs a two-layer Graph Attention Network (GAT) with multi-head attention. "
        "For nodes u and v, attention coefficients alpha_{uv} are computed via LeakyReLU-activated linear projections, and node representations are "
        "updated across M heads: h_u = sigma((1 / M) sum_{m=1}^M sum_{v in N(u)} alpha_{uv}^m W^m x_v). Edge representations z_{uv} for flow classification "
        "are synthesized by concatenating endpoint representations into an edge MLP: z_{uv} = MLP_{edge}([h_u || h_v]). Crucially, the base FedGATSage "
        "framework optimizes local GAT parameters strictly using standard, unweighted Cross-Entropy empirical risk minimization."
    ),
    (
        "Community Detection and Server Overlay: To preserve client privacy and reduce communication overhead, FedGATSage applies the Louvain modularity "
        "algorithm to partition client graphs into community clusters C_1, ..., C_P by optimizing graph modularity Q = (1 / 2m) sum_{ij} [A_{ij} - (k_i k_j / 2m)] delta(c_i, c_j). "
        "Community centroids c_p are computed by degree-weighted averaging of constituent node embeddings and transmitted to the central server. The server "
        "constructs an inter-community overlay graph by connecting community centroids whose pairwise cosine similarity exceeds a dynamic threshold decay "
        "heuristic (decaying from 0.7 to 0.3 with minimum degree 3). The server processes this overlay graph using GraphSAGE convolutions, and global parameters "
        "are aggregated via a performance-weighted averaging scheme. Finally, a Random Forest meta-classifier trained strictly on concatenated detector "
        "probability vectors (3 x C) performs final classification."
    ),
    (
        "Pathologies Identified in our Code-Level Audit: Our systematic replication and audit of the base FedGATSage codebase revealed three severe flaws:\n"
        "1. Catastrophic Minority Manifold Collapse: Under unweighted Cross-Entropy loss, local GAT optimization is completely dominated by majority classes. "
        "Because Injection outnumbers Backdoor by 27:1, the continuous GNN feature space collapses, causing 99.83% of Backdoor flows to be misclassified as "
        "Injection (resulting in an appalling 0.11% recall across random seeds).\n"
        "2. Evaluation Signature Leakage: The published results were derived from a naive uniform random row split that leaked 46.88% of identical flow signatures "
        "into the test fold, artificially inflating reported metrics.\n"
        "3. Louvain Disconnected Community Artifacts: Louvain optimization frequently generates internally disconnected community subgraphs, transmitting "
        "unstable centroids to the server overlay."
    )
]

SEC_4_3_TITLE = "4.3 Proposed Architecture"
SEC_4_3_PARAS = [
    (
        "To comprehensively resolve the structural pathologies identified in prior art, we formulate a contrastive hybrid federated Graph Neural "
        "Network framework engineered specifically for highly imbalanced, non-IID IoT network intrusion detection. Figure 4.1 illustrates the end-to-end "
        "system architecture, detailing the coordinated multi-tier pipeline spanning leakage-controlled ingestion, client-side domain-specialized "
        "GAT message passing, Leiden community partitioning, joint Class-Balanced Focal and Supervised Contrastive loss optimization, server-side "
        "GraphSAGE overlay aggregation, and two-stage Random Forest meta-classification."
    ),
    (
        "Our architecture fundamentally transforms decentralized graph learning through four core innovations: (1) An audited 8-tuple StratifiedGroupKFold "
        "partitioning protocol that enforces absolute 0.00% signature leakage; (2) Three domain-specialized GAT client detectors (Temporal, Content, Behavioral) "
        "that prevent feature interference across distinct attack modes; (3) A mathematically grounded Supervised Contrastive loss mechanism (mu = 0.1) that "
        "exerts active metric repulsion to prevent minority manifold collapse; and (4) A two-stage Random Forest meta-learner that arbitrates continuous GNN "
        "detector logits using deterministic physical NetFlow feature thresholds."
    )
]

SEC_4_4_TITLE = "4.4 Proposed Design / Detailed Methodology Formulations"
SEC_4_4_PARAS = [
    (
        "This section details the formal mathematical equations governing every stage of our proposed contrastive hybrid federated architecture."
    )
]

SUBSEC_4_4_1_TITLE = "4.4.1 Three Domain-Specialized Client GAT Detectors"
SUBSEC_4_4_1_PARAS = [
    (
        "Rather than forcing a single monolithic GNN to process all heterogeneous NetFlow features simultaneously, our client architecture deploys "
        "three specialized Graph Attention Network (GAT) models at each edge client node k in {1, ..., K}, each dedicated to an orthogonal functional domain:\n"
        "• Temporal GAT (M_{temp}): Specializes in flow duration, packet arrival rates, byte rates, and forward-to-backward packet ratios.\n"
        "• Content GAT (M_{cont}): Specializes in payload volume asymmetry, average packet sizes, and TCP flag distribution ratios.\n"
        "• Behavioral GAT (M_{behav}): Specializes in service port privilege flags, ephemeral port dispersion, and protocol identifiers."
    ),
    (
        "For each specialized detector d in {temp, cont, behav}, local telemetry is mapped to a client subgraph G_k^{(d)} = (V_k, E_k, X_k^{(d)}). "
        "Initial vertex representations x_u^{(d)} in R^{d_{feat}} are computed via incident edge averaging: x_u^{(d)} = (1 / deg(u)) sum_{(u, v) in E} e_{uv}^{(d)}. "
        "The graph attention layer computes dynamic attention coefficients alpha_{uv} between connected nodes u and v across M = 8 attention heads:"
    ),
    (
        "alpha_{uv}^{(m)} = exp( LeakyReLU( a^T [ W^{(m)} x_u || W^{(m)} x_v ] ) ) / sum_{w in N(u)} exp( LeakyReLU( a^T [ W^{(m)} x_u || W^{(m)} x_w ] ) )    (Eq. 4.1)\n\n"
        "where W^{(m)} in R^{32 x d_{feat}} is a learnable projection matrix for head m, a in R^{64} is a learnable attention parameter vector, || denotes vector "
        "concatenation, and N(u) represents the immediate neighborhood of host u."
    ),
    (
        "Vertex embeddings are updated by aggregating projected neighbor features weighted by attention coefficients across all M = 8 heads, followed by ELU activation:"
    ),
    (
        "h_u^{(d)} = ELU( (1 / M) sum_{m=1}^M sum_{v in N(u)} alpha_{uv}^{(m)} W^{(m)} x_v )    (Eq. 4.2)\n\n"
        "yielding a 256-dimensional latent representation for each host node. A second GAT layer applies identical attention convolutions: h_u'^{(d)} = GATLayer_2(h_u^{(d)})."
    ),
    (
        "Because NetFlow intrusion detection requires classifying directional flows (edges) rather than individual host vertices, edge representations "
        "z_{uv}^{(d)} are synthesized by feeding concatenated endpoint node embeddings into a dedicated two-layer Edge Multi-Layer Perceptron (MLP):"
    ),
    (
        "z_{uv}^{(d)} = Linear_{256 -> 8}( Dropout_{0.2}( ReLU( Linear_{512 -> 256}( [ h_u'^{(d)} || h_v'^{(d)} ] ) ) ) )    (Eq. 4.3)\n\n"
        "where the 256-dimensional intermediate layer z_tilde_{uv}^{(d)} serves as the continuous edge embedding used for contrastive regularization, and the final "
        "8-dimensional output vector produces pre-softmax detector classification logits: y_hat_{uv}^{(d)} = Softmax( z_{uv}^{(d)} )."
    )
]

SUBSEC_4_4_2_TITLE = "4.4.2 Leiden Community Partitioning and Centroid Pooling"
SUBSEC_4_4_2_PARAS = [
    (
        "To eliminate the disconnected community artifacts generated by Louvain modularity optimization in base architectures, our framework incorporates "
        "the Leiden community detection algorithm (Traag et al., 2019). The Leiden algorithm operates by optimizing the Constant Potts Model (CPM) quality function "
        "H_{CPM} parameterized by resolution parameter gamma = 1.0:"
    ),
    (
        "H_{CPM} = sum_{c in C} [ e(c, c) - gamma * (n_c * (n_c - 1) / 2) ]    (Eq. 4.4)\n\n"
        "where C denotes the partition of vertices into communities, e(c, c) is the total edge weight internal to community c, and n_c is the number of nodes in c. "
        "The Leiden algorithm guarantees well-connected communities by executing three alternating phases: (1) Local movement of individual nodes; (2) Refinement "
        "of the discovered partition where communities are iteratively split into connected components; and (3) Graph aggregation based on the refined partition. "
        "This guarantees that every discovered community is strictly connected."
    ),
    (
        "For each detected community c_p in C_k, client k synthesizes a community centroid embedding c_p in R^{256} via uniform mean pooling over all constituent host nodes:"
    ),
    (
        "c_p = (1 / |V_p|) sum_{u in V_p} h_u'    (Eq. 4.5)\n\n"
        "Community centroid pooling compresses local client telemetry by 85% (reducing transmission from ~25 KB of raw telemetry to 3.2 KB of centroid vectors per client), "
        "preserving client identity privacy while abstracting topological communication patterns for server aggregation."
    )
]

SUBSEC_4_4_3_TITLE = "4.4.3 Class-Balanced Focal Optimization"
SUBSEC_4_4_3_PARAS = [
    (
        "To mitigate extreme majority-class dominance during client training, local GAT parameters are optimized using Class-Balanced Focal (CB-Focal) Loss "
        "(Cui et al., 2019; Lin et al., 2017). Based on effective sample volume theory, the effective number of training instances E_{n_y} for class y is defined as:"
    ),
    (
        "E_{n_y} = (1 - beta^{n_y}) / (1 - beta)    (Eq. 4.6)\n\n"
        "where n_y is the sample count for class y, and beta = 0.9999 controls the effective volume growth rate. The normalized class-balancing weight alpha_y is:"
    ),
    (
        "alpha_y = [ (1 - beta) / (1 - beta^{n_y}) ] * [ sum_{c=1}^C (1 - beta) / (1 - beta^{n_c}) ]^{-1} * C    (Eq. 4.7)\n\n"
        "This class-balancing weight is embedded into the Focal Loss formulation with focusing parameter gamma = 2.0:"
    ),
    (
        "L_{CB-Focal} = - alpha_y * (1 - p_t)^gamma * log(p_t)    (Eq. 4.8)\n\n"
        "where p_t is the model's estimated probability for the ground-truth class. Focal modulation depresses gradient magnitudes from easy, high-confidence "
        "majority samples (where p_t -> 1), forcing optimization to prioritize ambiguous boundary flows."
    )
]

SUBSEC_4_4_4_TITLE = "4.4.4 Supervised Contrastive Representation Regularization (SupCon)"
SUBSEC_4_4_4_PARAS = [
    (
        "While CB-Focal loss dynamically modulates gradient magnitudes, it does not alter the geometric layout of representations in the continuous latent space. "
        "Under extreme 27:1 class imbalance, cross-entropy derivatives still allow majority clusters to swallow minority decision boundaries. To establish "
        "active angular metric separation, we formulate Supervised Contrastive (SupCon) loss (Khosla et al., 2020) directly on normalized edge representations: "
        "z_tilde_i = z_i / ||z_i||_2."
    ),
    (
        "Within each mini-batch I of edge indices, the multi-view Supervised Contrastive loss with temperature tau = 0.07 is formulated as:"
    ),
    (
        "L_{SupCon} = sum_{i in I} ( -1 / |P(i)| ) * sum_{p in P(i)} log [ exp( z_tilde_i . z_tilde_p / tau ) / sum_{a in A(i)} exp( z_tilde_i . z_tilde_a / tau ) ]    (Eq. 4.9)\n\n"
        "where A(i) = I \\ {i} indexes all mini-batch edges excluding anchor i, P(i) = {p in A(i) : y_p = y_i} indexes all co-class positive edges relative to anchor i, "
        "and |P(i)| is positive pair cardinality."
    ),
    (
        "Mathematical Derivation of Contrastive Repulsive Dynamics: The gradient of L_{SupCon} with respect to normalized embedding z_tilde_i is derived as:"
    ),
    (
        "nabla_{z_tilde_i} L_{SupCon} = (1 / tau) * [ sum_{a in A(i)} P_{ia} * z_tilde_a - (1 / |P(i)|) * sum_{p in P(i)} z_tilde_p ]    (Eq. 4.10)\n\n"
        "where P_{ia} = exp( z_tilde_i . z_tilde_a / tau ) / sum_{k in A(i)} exp( z_tilde_i . z_tilde_k / tau ). Eq. 4.10 reveals the dual geometric forces exerted "
        "by SupCon: (1) An attractive force (second term) pulling representations of the same intrusion class together toward their class centroid; and (2) A powerful "
        "repulsive force (first term) pushing representations of all non-matching classes apart with magnitude proportional to -z_tilde_a / tau."
    ),
    (
        "The overall local client optimization objective combines CB-Focal classification loss with SupCon representation regularization weighted by hyperparameter mu = 0.1:"
    ),
    (
        "L_{total} = L_{CB-Focal} + mu * L_{SupCon}    (Eq. 4.11)\n\n"
        "In Section 5.4, we systematically evaluate mu in {0.0, 0.1, 0.3, 0.5}, proving that mu = 0.1 delivers the optimal mathematical equilibrium between semantic "
        "class separation and graph structural integrity."
    )
]

SUBSEC_4_4_5_TITLE = "4.4.5 Dynamic Class-Balanced Sampling and Intra-Class Edge Interpolation"
SUBSEC_4_4_5_PARAS = [
    (
        "To guarantee that every optimization step contains adequate positive pairs for rare intrusions, a dynamic sampler draws an equal quota of M = 64 edges "
        "per class per mini-batch step: B_{step} = union_{c=1}^C Sample({e in E_k : y_e = c}, min(M, N_c)). If a rare class contains fewer than M edges in the client graph, "
        "replacement sampling is dynamically applied."
    ),
    (
        "Furthermore, to expand the geometric support of sparse minority manifolds, we implement client-local intra-class convex feature interpolation along "
        "flow feature dimensions (Zhang et al., 2018):"
    ),
    (
        "e_tilde_{new} = lambda * e_i + (1 - lambda) * e_j,    where y_i = y_j = c    (Eq. 4.12)\n\n"
        "where mixing parameter lambda ~ Beta(0.5, 0.5) and interpolation ratio is fixed at 0.50 (maximum 10x augmentation). Restricting interpolation strictly "
        "within identical class labels prevents the generation of corrupted boundary flows while densifying minority attack manifolds."
    )
]

SUBSEC_4_4_6_TITLE = "4.4.6 Server GraphSAGE Overlay and Two-Stage Random Forest Meta-Learner"
SUBSEC_4_4_6_PARAS = [
    (
        "At the centralized coordination layer, community centroids c_p received from participating clients form an aggregated server overlay graph "
        "G_{overlay} = (V_{comm}, E_{comm}). To bound communication density, inter-community edges are established using a static top-k nearest neighbor protocol "
        "with k = 5 based on pairwise cosine similarity:"
    ),
    (
        "E_{comm} = { (p, q) : q in top-k_{r != p}( (c_p . c_r) / (||c_p||_2 * ||c_r||_2) ) }    (Eq. 4.13)\n\n"
        "The server executes 2-layer GraphSAGE inductive convolutions over this overlay graph to capture macro-level inter-community relationships across enterprise subnets. "
        "Concurrently, local client GAT model parameters are synchronized across communication rounds using edge-count weighted Federated Averaging (FedAvg):"
    ),
    (
        "Theta_{global}^{(d)} = sum_{k=1}^K [ |E_k| / sum_j |E_j| ] * Theta_k^{(d)}    (Eq. 4.14)"
    ),
    (
        "Two-Stage Random Forest Meta-Classifier: For final decision arbitration, we deploy an ensemble Random Forest meta-classifier consisting of 100 balanced "
        "decision trees (max depth 20). For each test flow i, the meta-feature input vector phi_i concatenates:"
    ),
    (
        "phi_i = [ P_{temp}(i) || P_{cont}(i) || P_{behav}(i) || y_{pred} || conf || x_{raw}(i) ]    (Eq. 4.15)\n\n"
        "where P_d(i) in R^8 are the softmax output probability vectors from the three specialized GAT detectors (24 dims), y_{pred} in R^3 are detector argmax indices, "
        "conf in R^3 are maximum confidence values, and x_{raw}(i) in R^{21} represents the normalized physical NetFlow attribute vector. Fusing raw flow features "
        "directly into the meta-classifier provides critical deterministic physical threshold checks (e.g., exact packet rates and byte asymmetries) that resolve "
        "ambiguities in continuous GNN logits."
    )
]

SEC_4_5_TITLE = "4.5 Proposed Complete Flowchart and Execution Algorithms"
SEC_4_5_PARAS = [
    (
        "The end-to-end execution of our contrastive hybrid federated framework is formalized in Algorithm 4.1 (Overall Federated Pipeline) and "
        "Algorithm 4.2 (Dynamic Class-Balanced Mini-Batch Sampling with SupCon Evaluation). Figure 4.2 presents the complete procedural flowchart "
        "mapping the interaction between client-side GAT optimization, community pooling, server GraphSAGE aggregation, and meta-learner training."
    )
]

ALGO_4_1_TEXT = (
    "Algorithm 4.1: Contrastive Hybrid Federated GNN Pipeline\n"
    "Input: Client NetFlow datasets {D_1, ..., D_K}, global communication rounds R=15, local epochs E=5, temperature tau=0.07, SupCon weight mu=0.1.\n"
    "Output: Global GAT models Theta_{global}^{(d)} and trained Random Forest meta-classifier RF.\n"
    "1: Initialize global detector parameters Theta_{global}^{(d)} for d in {temp, cont, behav}.\n"
    "2: For each communication round r = 1 to R do:\n"
    "3:    For each client k in {1, ..., K} in parallel do:\n"
    "4:       Synchronize local parameters: Theta_{k, r}^{(d)} <- Theta_{global, r-1}^{(d)}.\n"
    "5:       Construct client subgraphs G_k^{(d)} with intra-class edge mixup (Eq. 4.12).\n"
    "6:       Partition client graph into communities C_k via Leiden CPM optimization (Eq. 4.4).\n"
    "7:       Compute Class-Balanced weights alpha_y via effective sample volume (Eq. 4.7).\n"
    "8:       For local epoch e = 1 to E do:\n"
    "9:          Sample class-balanced mini-batch B_{step} with M=64 edges per class (Algorithm 4.2).\n"
    "10:         Execute forward message passing: compute edge embeddings z_{uv} and logits y_hat.\n"
    "11:         Evaluate L_{CB-Focal} (Eq. 4.8) and L_{SupCon} (Eq. 4.9).\n"
    "12:         Compute total loss: L_{total} = L_{CB-Focal} + mu * L_{SupCon}.\n"
    "13:         Update parameters Theta_k^{(d)} via Adam optimizer with gradient clipping.\n"
    "14:      End For\n"
    "15:      Pool community centroids c_p via uniform mean pooling (Eq. 4.5).\n"
    "16:      Transmit centroids {c_p} and model parameters Theta_k^{(d)} to coordination server.\n"
    "17:   End For\n"
    "18:   Server constructs top-k overlay graph G_{overlay} (k=5) based on centroid cosine similarity (Eq. 4.13).\n"
    "19:   Server executes GraphSAGE convolutions over G_{overlay}.\n"
    "20:   Server aggregates global parameters Theta_{global, r}^{(d)} via edge-weighted FedAvg (Eq. 4.14).\n"
    "21: End For\n"
    "22: Extract concatenated meta-features phi (Eq. 4.15) across client graphs.\n"
    "23: Train Random Forest meta-classifier RF on concatenated meta-features.\n"
    "24: Return Theta_{global}^{(d)} and RF."
)

ALGO_4_2_TEXT = (
    "Algorithm 4.2: Dynamic Class-Balanced Sampling & SupCon Evaluation\n"
    "Input: Client edge set E_k, labels Y_k, samples per class M=64, temperature tau=0.07, model Theta.\n"
    "Output: Mini-batch loss L_{batch}.\n"
    "1: Initialize empty mini-batch edge index set B <- emptyset.\n"
    "2: For each class c in {1, ..., C} do:\n"
    "3:    Identify edge indices belonging to class c: E_c = {e in E_k : y_e = c}.\n"
    "4:    If |E_c| >= M then sample M unique edges without replacement.\n"
    "5:    Else sample |E_c| edges and sample (M - |E_c|) edges with replacement.\n"
    "6:    B <- B union Sampled_Edges.\n"
    "7: End For\n"
    "8: Extract normalized edge embeddings z_tilde_i = z_i / ||z_i||_2 for all i in B.\n"
    "9: Evaluate pairwise cosine similarities S_{ij} = z_tilde_i . z_tilde_j / tau.\n"
    "10: For each anchor i in B, compute SupCon loss term over positive set P(i) (Eq. 4.9).\n"
    "11: Compute mean SupCon loss L_{SupCon} across all anchors in B.\n"
    "12: Return L_{SupCon}."
)
