# -*- coding: utf-8 -*-
with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# Eq 17
old_eq17 = r"""\begin{equation}
\alpha_{uv}^{(m)} = \frac{\exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_v] \right) \right)}{\displaystyle\sum_{w \in \mathcal{N}(u)} \exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_w] \right) \right)}
\label{eq:attention_coeffs}
\end{equation}"""

new_eq17 = r"""\begin{equation}
\begin{split}
\alpha_{uv}^{(m)} &= \frac{\exp\left( e_{uv}^{(m)} \right)}{\displaystyle\sum_{w \in \mathcal{N}(u)} \exp\left( e_{uw}^{(m)} \right)}, \\
\text{where } e_{uv}^{(m)} &= \text{LeakyReLU}\left( \boldsymbol{a}^T \left[\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_v\right] \right)
\end{split}
\label{eq:attention_coeffs}
\end{equation}"""
text = text.replace(old_eq17, new_eq17)

# Eq 26
old_eq26 = r"""\begin{equation}
\nabla_{\tilde{\boldsymbol{z}}_i} \mathcal{L}_{\text{SupCon}} = \frac{1}{\tau} \left( \sum_{a \in A(i)} P_{ia} \tilde{\boldsymbol{z}}_a - \frac{1}{|P(i)|} \sum_{p \in P(i)} \tilde{\boldsymbol{z}}_p \right)
\label{eq:supcon_gradient}
\end{equation}"""

new_eq26 = r"""\begin{equation}
\begin{split}
\nabla_{\tilde{\boldsymbol{z}}_i} \mathcal{L}_{\text{SupCon}} &= \frac{1}{\tau} \left( \sum_{a \in A(i)} P_{ia} \tilde{\boldsymbol{z}}_a - \frac{1}{|P(i)|} \sum_{p \in P(i)} \tilde{\boldsymbol{z}}_p \right), \\
\text{where } P_{ia} &= \frac{\exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau\right)}{\sum_{b \in A(i)} \exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_b / \tau\right)}
\end{split}
\label{eq:supcon_gradient}
\end{equation}"""
text = text.replace(old_eq26, new_eq26)

# Eq 30
old_eq30 = r"""\begin{equation}
\mathcal{E}_{\text{comm}} = \left\{ (p, q) : q \in \text{top-}k_{r \neq p}\left( \frac{\boldsymbol{c}_p \cdot \boldsymbol{c}_r}{\|\boldsymbol{c}_p\|_2 \|\boldsymbol{c}_r\|_2} \right) \right\}
\label{eq:server_topk_edges}
\end{equation}"""

new_eq30 = r"""\begin{equation}
\mathcal{E}_{\text{comm}} = \left\{ (p, q) : q \in \text{top-}k_{r \neq p}\left( \frac{\boldsymbol{c}_p \cdot \boldsymbol{c}_r}{\|\boldsymbol{c}_p\|_2 \, \|\boldsymbol{c}_r\|_2} \right) \right\}
\label{eq:server_topk_edges}
\end{equation}"""
text = text.replace(old_eq30, new_eq30)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("Split complex equations successfully!")
