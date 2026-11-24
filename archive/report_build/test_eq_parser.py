import re

sample_para = (
    "Initial node feature vectors are computed by aggregating all incident edge attributes:\n\n"
    "x_u = (1 / deg(u)) * sum_{(u, v) in E} e_{uv}    (Eq. 3.1)\n\n"
    "where deg(u) is the in-out degree of host u."
)

pattern = r"^(.*?)(?:[\r\n]+)?([^\r\n]+?\s*\((?:Eq\.\s*)?(\d+\.\d+)\))(?:[\r\n]+)?(.*)$"
m = re.search(r"([^\r\n]+?)\s*\((?:Eq\.\s*)?(\d+\.\d+)\)", sample_para)
if m:
    eq_text = m.group(1).strip()
    eq_num = f"({m.group(2).strip()})"
    print(f"Detected equation: '{eq_text}' with number: '{eq_num}'")
