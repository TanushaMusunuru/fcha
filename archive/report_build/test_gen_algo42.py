import sys
sys.stdout.reconfigure(encoding='utf-8')
import text_ch4

def generate_algo42_latex():
    tex = r"""\begin{algorithm}[H]
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
\State Extract node-pair embeddings $\{\mathbf{z}_i\}_{i \in \mathcal{B}}$ via forward pass through GAT encoder $\Theta^{(d)}$.
\State Normalize representations to unit hypersphere: $\tilde{\mathbf{z}}_i = \mathbf{z}_i / \|\mathbf{z}_i\|_2$.
\State Compute Class-Balanced Focal loss $\mathcal{L}_{\text{CB-Focal}}$ over sampled batch $\mathcal{B}$.
\State Compute Supervised Contrastive regularizer:
\State $\mathcal{L}_{\text{SupCon}} = \sum_{i \in \mathcal{B}} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(\tilde{\mathbf{z}}_i \cdot \tilde{\mathbf{z}}_p / \tau)}{\sum_{a \in A(i)} \exp(\tilde{\mathbf{z}}_i \cdot \tilde{\mathbf{z}}_a / \tau)}$.
\State Formulate joint objective: $\mathcal{L}_{\text{batch}} = \mathcal{L}_{\text{CB-Focal}} + \mu \, \mathcal{L}_{\text{SupCon}}$.
\State \Return $\mathcal{L}_{\text{batch}}$.
\end{algorithmic}
\end{algorithm}
"""
    return tex

print("Algo 4.2 length:", len(generate_algo42_latex()))
