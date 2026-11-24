from latex2mathml.converter import convert as latex_to_mathml
import lxml.etree as ET

xslt_path = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
xslt_doc = ET.parse(xslt_path)
xslt_transform = ET.XSLT(xslt_doc)

additional_eqs = [
    r"W_{t+1} = \sum_{k=1}^K \frac{n_k}{n} W_{t+1}^k",
    r"\frac{\mu}{2} \|W - W_t\|^2",
    r"\mathcal{L}_{\text{FL}} = - (1 - p_t)^\gamma \log(p_t)",
    r"E_n = \frac{1 - \beta^n}{1 - \beta}",
    r"\alpha_c \propto \frac{1 - \beta}{1 - \beta^{n_c}}",
    r"\tilde{x} = \lambda x_i + (1 - \lambda) x_j",
    r"\theta^* = \arg\min_{j, t} \left[ \frac{N_L}{N} G(D_L) + \frac{N_R}{N} G(D_R) \right]",
    r"\mathcal{L}_{\text{CE}} = - \sum_{c=1}^C y_c \log(p_c)",
    r"W_{\text{global}} = \sum_{k=1}^K \frac{n_k}{n} W_k",
    r"x_u = \frac{1}{\text{deg}(u)} \sum_{(u, v) \in \mathcal{E}} e_{uv}",
    r"h_u = \sigma\left( \frac{1}{M} \sum_{m=1}^M \sum_{v \in \mathcal{N}(u)} \alpha_{uv}^m W^m x_v \right)",
    r"z_{uv} = \text{MLP}_{\text{edge}}([h_u \,\|\, h_v])",
    r"Q = \frac{1}{2m} \sum_{ij} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)",
    r"\frac{\partial \mathcal{L}_{\text{CE}}}{\partial z_i} = p_i - y_i"
]

for idx, eq in enumerate(additional_eqs):
    try:
        mml = latex_to_mathml(eq)
        omml = xslt_transform(ET.fromstring(mml))
        print(f"Extra Eq {idx+1}: SUCCESS")
    except Exception as e:
        print(f"Extra Eq {idx+1}: FAILED -> {e} | Eq: {eq}")
