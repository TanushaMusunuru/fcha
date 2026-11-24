# render_equations.py
import re

BEAUTIFIED_MATH = {
    "3.1": {
        "unicode": "𝐱ᵤ = ( 1 / deg(u) ) ∑₍ᵤ, ᵥ₎ ∈ ℰ  𝐞ᵤᵥ",
        "latex": r"$$ \boldsymbol{x}_u = \frac{1}{\text{deg}(u)} \sum_{(u, v) \in \mathcal{E}} \boldsymbol{e}_{uv} \tag{3.1} $$"
    },
    "3.2": {
        "unicode": "𝒮 ≡ [ L4_SRC_PORT, L4_DST_PORT, PROTOCOL, IN_BYTES, OUT_BYTES, IN_PKTS, OUT_PKTS, FLOW_DURATION ]",
        "latex": r"$$ \mathcal{S} \equiv \left[ \text{L4\_SRC\_PORT}, \text{L4\_DST\_PORT}, \text{PROTOCOL}, \text{IN\_BYTES}, \text{OUT\_BYTES}, \text{IN\_PKTS}, \text{OUT\_PKTS}, \text{FLOW\_DURATION} \right] \tag{3.2} $$"
    },
    "4.1": {
        "unicode": "αᵤᵥ⁽ᵐ⁾ = exp( LeakyReLU( 𝐚ᵀ [ 𝐖⁽ᵐ⁾𝐱ᵤ ‖ 𝐖⁽ᵐ⁾𝐱ᵥ ] ) ) / ∑_{w ∈ 𝒩(u)} exp( LeakyReLU( 𝐚ᵀ [ 𝐖⁽ᵐ⁾𝐱ᵤ ‖ 𝐖⁽ᵐ⁾𝐱_w ] ) )",
        "latex": r"$$ \alpha_{uv}^{(m)} = \frac{\exp\left(\text{LeakyReLU}\left(\boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_v]\right)\right)}{\sum_{w \in \mathcal{N}(u)} \exp\left(\text{LeakyReLU}\left(\boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_w]\right)\right)} \tag{4.1} $$"
    },
    "4.2": {
        "unicode": "𝐡ᵤ⁽ᵈ⁾ = ELU( ( 1 / M ) ∑ₘ₌₁ᴹ ∑_{v ∈ 𝒩(u)} αᵤᵥ⁽ᵐ⁾ 𝐖⁽ᵐ⁾ 𝐱ᵥ )",
        "latex": r"$$ \boldsymbol{h}_u^{(d)} = \text{ELU}\left( \frac{1}{M} \sum_{m=1}^M \sum_{v \in \mathcal{N}(u)} \alpha_{uv}^{(m)} \boldsymbol{W}^{(m)} \boldsymbol{x}_v \right) \tag{4.2} $$"
    },
    "4.3": {
        "unicode": "𝐳ᵤᵥ⁽ᵈ⁾ = Linear₂₅₆→₈( Dropout₀.₂( ReLU( Linear₅₁₂→₂₅₆( [ 𝐡ᵤ′⁽ᵈ⁾ ‖ 𝐡ᵥ′⁽ᵈ⁾ ] ) ) ) )",
        "latex": r"$$ \boldsymbol{z}_{uv}^{(d)} = \text{Linear}_{256 \to 8}\left( \text{Dropout}_{0.2}\left( \text{ReLU}\left( \text{Linear}_{512 \to 256}\left( [\boldsymbol{h}_u'^{(d)} \,\|\, \boldsymbol{h}_v'^{(d)}] \right) \right) \right) \right) \tag{4.3} $$"
    },
    "4.4": {
        "unicode": "ℋ_{CPM} = ∑_{c ∈ 𝒞} [ e(c, c) - γ · ( n_c(n_c - 1) / 2 ) ]",
        "latex": r"$$ \mathcal{H}_{\text{CPM}} = \sum_{c \in \mathcal{C}} \left[ e(c, c) - \gamma \binom{n_c}{2} \right] \tag{4.4} $$"
    },
    "4.5": {
        "unicode": "𝐜ₚ = ( 1 / |Vₚ| ) ∑_{u ∈ Vₚ} 𝐡ᵤ′",
        "latex": r"$$ \boldsymbol{c}_p = \frac{1}{|V_p|} \sum_{u \in V_p} \boldsymbol{h}_u' \tag{4.5} $$"
    },
    "4.6": {
        "unicode": "E_{n_y} = ( 1 - β^{n_y} ) / ( 1 - β )",
        "latex": r"$$ E_{n_y} = \frac{1 - \beta^{n_y}}{1 - \beta} \tag{4.6} $$"
    },
    "4.7": {
        "unicode": "α_y = [ ( 1 - β ) / ( 1 - β^{n_y} ) ] · [ ∑_{c=1}^C ( 1 - β ) / ( 1 - β^{n_c} ) ]⁻¹ · C",
        "latex": r"$$ \alpha_y = \frac{1 - \beta}{1 - \beta^{n_y}} \cdot \left( \sum_{c=1}^C \frac{1 - \beta}{1 - \beta^{n_c}} \right)^{-1} \cdot C \tag{4.7} $$"
    },
    "4.8": {
        "unicode": "ℒ_{CB-Focal} = - α_y · ( 1 - p_t )^γ · log( p_t )",
        "latex": r"$$ \mathcal{L}_{\text{CB-Focal}} = - \alpha_y (1 - p_t)^\gamma \log(p_t) \tag{4.8} $$"
    },
    "4.9": {
        "unicode": "ℒ_{SupCon} = ∑_{i ∈ I} ( -1 / |P(i)| ) ∑_{p ∈ P(i)} log [ exp( 𝐳̃ᵢ · 𝐳̃ₚ / τ ) / ∑_{a ∈ A(i)} exp( 𝐳̃ᵢ · 𝐳̃ₐ / τ ) ]",
        "latex": r"$$ \mathcal{L}_{\text{SupCon}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_p / \tau\right)}{\sum_{a \in A(i)} \exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau\right)} \tag{4.9} $$"
    },
    "4.10": {
        "unicode": "∇_{𝐳̃ᵢ} ℒ_{SupCon} = ( 1 / τ ) · [ ∑_{a ∈ A(i)} P_{ia} 𝐳̃ₐ - ( 1 / |P(i)| ) ∑_{p ∈ P(i)} 𝐳̃ₚ ]",
        "latex": r"$$ \nabla_{\tilde{\boldsymbol{z}}_i} \mathcal{L}_{\text{SupCon}} = \frac{1}{\tau} \left( \sum_{a \in A(i)} P_{ia} \tilde{\boldsymbol{z}}_a - \frac{1}{|P(i)|} \sum_{p \in P(i)} \tilde{\boldsymbol{z}}_p \right) \tag{4.10} $$"
    },
    "4.11": {
        "unicode": "ℒ_{total} = ℒ_{CB-Focal} + μ · ℒ_{SupCon}",
        "latex": r"$$ \mathcal{L}_{\text{total}} = \mathcal{L}_{\text{CB-Focal}} + \mu \cdot \mathcal{L}_{\text{SupCon}} \tag{4.11} $$"
    },
    "4.12": {
        "unicode": "𝐞̃_{new} = λ · 𝐞ᵢ + ( 1 - λ ) · 𝐞ⱼ,    where yᵢ = yⱼ = c,  λ ~ Beta(0.5, 0.5)",
        "latex": r"$$ \tilde{\boldsymbol{e}}_{new} = \lambda \boldsymbol{e}_i + (1 - \lambda) \boldsymbol{e}_j, \quad \text{where } y_i = y_j = c, \; \lambda \sim \text{Beta}(0.5, 0.5) \tag{4.12} $$"
    },
    "4.13": {
        "unicode": "ℰ_{comm} = { (p, q) : q ∈ top-k_{r ≠ p}( ( 𝐜ₚ · 𝐜ᵣ ) / ( ‖𝐜ₚ‖₂ · ‖𝐜ᵣ‖₂ ) ) }",
        "latex": r"$$ \mathcal{E}_{\text{comm}} = \left\{ (p, q) : q \in \text{top-}k_{r \neq p}\left( \frac{\boldsymbol{c}_p \cdot \boldsymbol{c}_r}{\|\boldsymbol{c}_p\|_2 \|\boldsymbol{c}_r\|_2} \right) \right\} \tag{4.13} $$"
    },
    "4.14": {
        "unicode": "𝚯_{global}⁽ᵈ⁾ = ∑_{k=1}^K [ |ℰ_k| / ∑ⱼ |ℰⱼ| ] · 𝚯_k⁽ᵈ⁾",
        "latex": r"$$ \boldsymbol{\Theta}_{\text{global}}^{(d)} = \sum_{k=1}^K \frac{|\mathcal{E}_k|}{\sum_{j} |\mathcal{E}_j|} \boldsymbol{\Theta}_k^{(d)} \tag{4.14} $$"
    },
    "4.15": {
        "unicode": "𝛟ᵢ = [ 𝐏_{temp}(i) ‖ 𝐏_{cont}(i) ‖ 𝐏_{behav}(i) ‖ 𝐲_{pred} ‖ conf ‖ 𝐱_{raw}(i) ]",
        "latex": r"$$ \boldsymbol{\phi}_i = \left[ \boldsymbol{P}_{\text{temp}}(i) \,\|\, \boldsymbol{P}_{\text{cont}}(i) \,\|\, \boldsymbol{P}_{\text{behav}}(i) \,\|\, \boldsymbol{y}_{\text{pred}} \,\|\, \boldsymbol{conf} \,\|\, \boldsymbol{x}_{\text{raw}}(i) \right] \tag{4.15} $$"
    },
    "5.1": {
        "unicode": "ΔBalAcc = ( 1 / C ) ∑_{k=1}^C ΔRecall_k = +13.59%",
        "latex": r"$$ \Delta \text{BalAcc} = \frac{1}{C} \sum_{k=1}^C \Delta \text{Recall}_k = +13.59\% \tag{5.1} $$"
    }
}

print("Loaded beautified math dictionary with 18 equations.")
