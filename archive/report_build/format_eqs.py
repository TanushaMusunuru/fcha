# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("dissertation_overleaf.tex", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Eq 9: Socket signature tuple
old_eq9 = r"\mathcal{S} \equiv \big[ \text{L4\_SRC\_PORT}, \, \text{L4\_DST\_PORT}, \, \text{PROTOCOL}, \, \text{IN\_BYTES}, \, \text{OUT\_BYTES}, \, \text{IN\_PKTS}, \, \text{OUT\_PKTS}, \, \text{FLOW\_DURATION} \big]"
new_eq9 = r"""\begin{split}
\mathcal{S} \equiv \big[ & \text{L4\_SRC\_PORT}, \, \text{L4\_DST\_PORT}, \, \text{PROTOCOL}, \, \text{IN\_BYTES}, \\
& \text{OUT\_BYTES}, \, \text{IN\_PKTS}, \, \text{OUT\_PKTS}, \, \text{FLOW\_DURATION} \big]
\end{split}"""
text = text.replace(old_eq9, new_eq9)

# 2. Eq 17: Attention coefficients
old_eq17 = r"\alpha_{uv}^{(m)} = \frac{\exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_v] \right) \right)}{\sum_{w \in \mathcal{N}(u)} \exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_w] \right) \right)}"
new_eq17 = r"""\alpha_{uv}^{(m)} = \frac{\exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_v] \right) \right)}{\displaystyle\sum_{w \in \mathcal{N}(u)} \exp\left( \text{LeakyReLU}\left( \boldsymbol{a}^T [\boldsymbol{W}^{(m)}\boldsymbol{x}_u \,\|\, \boldsymbol{W}^{(m)}\boldsymbol{x}_w] \right) \right)}"""
text = text.replace(old_eq17, new_eq17)

# 3. Eq 19: Edge predictor MLP
old_eq19 = r"\boldsymbol{z}_{uv}^{(d)} = \text{Linear}_{256 \to 8}\left( \text{Dropout}_{0.2}\left( \text{ReLU}\left( \text{Linear}_{512 \to 256}\left( [\boldsymbol{h}_u'^{(d)} \,\|\, \boldsymbol{h}_v'^{(d)}] \right) \right) \right) \right)"
new_eq19 = r"""\begin{split}
\boldsymbol{z}_{uv}^{(d)} = \text{Linear}_{256 \to 8}\Big( & \text{Dropout}_{0.2}\big( \text{ReLU}\big( \\
& \text{Linear}_{512 \to 256}\left( [\boldsymbol{h}_u'^{(d)} \,\|\, \boldsymbol{h}_v'^{(d)}] \right) \big) \big) \Big)
\end{split}"""
text = text.replace(old_eq19, new_eq19)

# 4. Eq 25: SupCon loss
old_eq25 = r"\mathcal{L}_{\text{SupCon}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_p / \tau\right)}{\sum_{a \in A(i)} \exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau\right)}"
new_eq25 = r"""\mathcal{L}_{\text{SupCon}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_p / \tau\right)}{\displaystyle\sum_{a \in A(i)} \exp\left(\tilde{\boldsymbol{z}}_i \cdot \tilde{\boldsymbol{z}}_a / \tau\right)}"""
text = text.replace(old_eq25, new_eq25)

# 5. Eq 26: SupCon gradient
old_eq26 = r"\nabla_{\tilde{\boldsymbol{z}}_i} \mathcal{L}_{\text{SupCon}} = \frac{1}{\tau} \left( \sum_{a \in A(i)} P_{ia} \tilde{\boldsymbol{z}}_a - \frac{1}{|P(i)|} \sum_{p \in P(i)} \tilde{\boldsymbol{z}}_p \right)"
new_eq26 = r"""\nabla_{\tilde{\boldsymbol{z}}_i} \mathcal{L}_{\text{SupCon}} = \frac{1}{\tau} \left( \sum_{a \in A(i)} P_{ia} \tilde{\boldsymbol{z}}_a - \frac{1}{|P(i)|} \sum_{p \in P(i)} \tilde{\boldsymbol{z}}_p \right)"""
text = text.replace(old_eq26, new_eq26)

# 6. Eq 29: Intra-class interpolation
old_eq29 = r"\tilde{\boldsymbol{e}}_{\text{new}} = \lambda \boldsymbol{e}_i + (1 - \lambda) \boldsymbol{e}_j, \quad \text{where } y_i = y_j = c, \; \lambda \sim \text{Beta}(0.5, 0.5)"
new_eq29 = r"""\begin{split}
\tilde{\boldsymbol{e}}_{\text{new}} = \lambda \boldsymbol{e}_i + (1 - \lambda) \boldsymbol{e}_j, \quad & \text{where } y_i = y_j = c, \\
& \lambda \sim \text{Beta}(0.5, 0.5)
\end{split}"""
text = text.replace(old_eq29, new_eq29)

# 7. Eq 30: Communication edge set
old_eq30 = r"\mathcal{E}_{\text{comm}} = \left\{ (p, q) : q \in \text{top-}k_{r \neq p}\left( \frac{\boldsymbol{c}_p \cdot \boldsymbol{c}_r}{\|\boldsymbol{c}_p\|_2 \|\boldsymbol{c}_r\|_2} \right) \right\}"
new_eq30 = r"""\mathcal{E}_{\text{comm}} = \left\{ (p, q) : q \in \text{top-}k_{r \neq p}\left( \frac{\boldsymbol{c}_p \cdot \boldsymbol{c}_r}{\|\boldsymbol{c}_p\|_2 \|\boldsymbol{c}_r\|_2} \right) \right\}"""
text = text.replace(old_eq30, new_eq30)

# 8. Eq 32: Concatenation
old_eq32 = r"\boldsymbol{\phi}_i = \left[ \boldsymbol{P}_{\text{temp}}(i) \,\|\, \boldsymbol{P}_{\text{cont}}(i) \,\|\, \boldsymbol{P}_{\text{behav}}(i) \,\|\, \boldsymbol{y}_{\text{pred}} \,\|\, \boldsymbol{conf} \,\|\, \boldsymbol{x}_{\text{raw}}(i) \right]"
new_eq32 = r"""\begin{split}
\boldsymbol{\phi}_i = \big[ & \boldsymbol{P}_{\text{temp}}(i) \,\|\, \boldsymbol{P}_{\text{cont}}(i) \,\|\, \boldsymbol{P}_{\text{behav}}(i) \,\|\, \\
& \boldsymbol{y}_{\text{pred}} \,\|\, \boldsymbol{conf} \,\|\, \boldsymbol{x}_{\text{raw}}(i) \big]
\end{split}"""
text = text.replace(old_eq32, new_eq32)

with open("dissertation_overleaf.tex", "w", encoding="utf-8") as f:
    f.write(text)

print("Formatted all long equations with split!")
