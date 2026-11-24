import re
import render_equations

test_texts = [
    "Initial node feature vectors are computed by aggregating incident edges:\n\nx_u = (1 / deg(u)) * sum_{(u, v) in E} e_{uv}    (Eq. 3.1)\n\nwhere deg(u) is the in-out degree.",
    "This is normal text without equation.",
    "Total loss is formulated as:\n\nL_{total} = L_{CB-Focal} + mu * L_{SupCon}    (Eq. 4.11)\n\nwhere mu = 0.1."
]

for t in test_texts:
    m = re.search(r"\((?:Eq\.\s*)?(\d+\.\d+)\)", t)
    if m:
        eq_id = m.group(1)
        print(f"Matched eq {eq_id} -> {render_equations.BEAUTIFIED_MATH.get(eq_id)['unicode']}")
    else:
        print("No eq matched.")
