import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_fully_connected_diagram(output_paths):
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'Segoe UI'],
        'mathtext.fontset': 'dejavusans',
    })

    fig_w, fig_h = 16.8, 9.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Color definitions matching exactly the original paper diagram
    COLOR_GREY_FILL = '#D9D9D9'
    COLOR_GREY_STROKE = '#2D3748'
    
    COLOR_BLUE_FILL = '#92BCED'
    COLOR_BLUE_STROKE = '#245285'
    
    COLOR_ORANGE_FILL = '#F7AD5F'
    COLOR_ORANGE_STROKE = '#B8550D'
    
    COLOR_CARD_BG = '#FFFFFF'
    COLOR_CARD_BORDER = '#212529'
    
    TEXT_DARK = '#111827'
    LINE_DARK = '#1F2937'

    # Outer black frame around entire figure
    outer_rect = patches.Rectangle((0.15, 0.15), fig_w - 0.30, fig_h - 0.30,
                                   fill=False, edgecolor='#111827', linewidth=2.2, zorder=1)
    ax.add_patch(outer_rect)

    # Helper: draw rounded node box
    def draw_node(cx, cy, w, h, text, fill_col, stroke_col, is_dashed=False, fontsize=10.0, fontweight='bold', text_color=TEXT_DARK, zorder=5):
        boxstyle = "round,pad=0.14,rounding_size=0.18"
        linestyle = '--' if is_dashed else '-'
        lw = 1.8 if is_dashed else 1.5
        rect = patches.FancyBboxPatch(
            (cx - w/2.0, cy - h/2.0), w, h,
            boxstyle=boxstyle,
            facecolor=fill_col,
            edgecolor=stroke_col,
            linewidth=lw,
            linestyle=linestyle,
            zorder=zorder
        )
        ax.add_patch(rect)
        if text:
            ax.text(cx, cy, text, ha='center', va='center',
                    fontsize=fontsize, fontweight=fontweight, color=text_color,
                    multialignment='center', zorder=zorder+1)
        return (cx, cy, w, h)

    # Helper: draw straight arrow
    def draw_arrow(start, end, text=None, text_offset=(0, 0), color=LINE_DARK, lw=1.5, ls='-', zorder=6, fontsize=8.8, text_color=TEXT_DARK, text_bg=True):
        ax.annotate(
            '', xy=end, xytext=start,
            arrowprops=dict(
                arrowstyle='->',
                color=color,
                lw=lw,
                linestyle=ls,
                shrinkA=2,
                shrinkB=2,
                mutation_scale=13
            ),
            zorder=zorder
        )
        if text:
            mx = (start[0] + end[0]) / 2.0 + text_offset[0]
            my = (start[1] + end[1]) / 2.0 + text_offset[1]
            bbox_props = dict(boxstyle='round,pad=0.18', fc='white', ec='#CBD5E0', lw=0.7, alpha=0.96) if text_bg else None
            ax.text(mx, my, text, ha='center', va='center', fontsize=fontsize,
                    fontweight='semibold', color=text_color, bbox=bbox_props, zorder=zorder+2)

    # Helper: draw elbow / routed arrow
    def draw_elbow(pts, text=None, text_pos=None, color=LINE_DARK, lw=1.5, ls='-', zorder=6, fontsize=8.8, text_bg=True):
        for i in range(len(pts) - 1):
            is_last = (i == len(pts) - 2)
            p1 = pts[i]
            p2 = pts[i+1]
            if is_last:
                ax.annotate(
                    '', xy=p2, xytext=p1,
                    arrowprops=dict(
                        arrowstyle='->',
                        color=color,
                        lw=lw,
                        linestyle=ls,
                        shrinkA=0,
                        shrinkB=2,
                        mutation_scale=13
                    ),
                    zorder=zorder
                )
            else:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, lw=lw, linestyle=ls, zorder=zorder)
        if text and text_pos:
            bbox_props = dict(boxstyle='round,pad=0.2', fc='white', ec='#CBD5E0', lw=0.7, alpha=0.96) if text_bg else None
            ax.text(text_pos[0], text_pos[1], text, ha='center', va='center', fontsize=fontsize,
                    fontweight='semibold', color=TEXT_DARK, bbox=bbox_props, zorder=zorder+2)

    # =========================================================================
    # COLUMN HEADERS
    # =========================================================================
    ax.text(1.7, 9.0, "Data", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)
    ax.text(8.3, 9.0, "Client (×5)", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)
    ax.text(14.4, 9.0, "Server", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)

    # =========================================================================
    # COLUMN 1: DATA
    # =========================================================================
    data_x = 1.7
    data_w = 2.45

    # 1. NF-ToN-IoT (same as base paper)
    draw_node(data_x, 8.0, data_w, 0.9, "NF-ToN-IoT\n(real IPs)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    
    # 2. Feature Extraction (same as base paper)
    draw_node(data_x, 6.3, data_w, 0.9, "Feature extraction\n(TCP flags, rates)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_arrow((data_x, 7.55), (data_x, 6.75))

    # 3. Signature-grouped split (same as base paper)
    draw_node(data_x, 4.4, data_w, 1.15, "Signature-grouped\nsplit (train / test,\n0% overlap)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.0)
    draw_arrow((data_x, 5.85), (data_x, 4.98))

    # Floating Orange Box: Edge Interpolation + class-balanced sampler (NEW)
    interp_cx, interp_cy = 3.85, 5.75
    interp_w, interp_h = 1.45, 1.35
    draw_node(interp_cx, interp_cy, interp_w, interp_h,
              "Edge\ninterpolation +\nclass-balanced\nsampler\n(training only)",
              COLOR_ORANGE_FILL, COLOR_ORANGE_STROKE, fontsize=8.4)

    # Arrow from split into Edge Interpolation
    draw_elbow([
        (data_x + data_w/2.0, 4.4),
        (interp_cx, 4.4),
        (interp_cx, interp_cy - interp_h/2.0)
    ], color=COLOR_ORANGE_STROKE, lw=1.6)

    # Arrow from Edge Interpolation into Client Card GATs
    draw_arrow((interp_cx + interp_w/2.0, interp_cy), (5.15, interp_cy), color=COLOR_ORANGE_STROKE, lw=1.6)

    # =========================================================================
    # COLUMN 2: CLIENT (x5) STACKED CONTAINER
    # =========================================================================
    c_card_x = 5.15
    c_card_y = 0.55
    c_card_w = 6.4
    c_card_h = 8.0

    # Back cards (depth effect for x5 clients)
    bg_card3 = patches.FancyBboxPatch(
        (c_card_x - 0.28, c_card_y + 0.28), c_card_w, c_card_h,
        boxstyle="round,pad=0.0,rounding_size=0.28",
        facecolor='#EDF2F7', edgecolor='#718096', linewidth=1.2, zorder=2
    )
    ax.add_patch(bg_card3)

    bg_card2 = patches.FancyBboxPatch(
        (c_card_x - 0.14, c_card_y + 0.14), c_card_w, c_card_h,
        boxstyle="round,pad=0.0,rounding_size=0.28",
        facecolor='#F7FAFC', edgecolor='#4A5568', linewidth=1.3, zorder=3
    )
    ax.add_patch(bg_card2)

    front_card = patches.FancyBboxPatch(
        (c_card_x, c_card_y), c_card_w, c_card_h,
        boxstyle="round,pad=0.0,rounding_size=0.28",
        facecolor=COLOR_CARD_BG, edgecolor=COLOR_CARD_BORDER, linewidth=1.8, zorder=4
    )
    ax.add_patch(front_card)

    # Privacy boundary vertical line and text inside client card
    p_bound_x = c_card_x + c_card_w - 0.55
    ax.plot([p_bound_x, p_bound_x], [c_card_y + 0.25, c_card_y + c_card_h - 0.25],
            color='#374151', linestyle='-', linewidth=1.6, zorder=5)
    ax.text(p_bound_x + 0.28, c_card_y + 2.7, "Privacy boundary",
            ha='center', va='center', rotation=90, fontsize=9.8, fontweight='bold', color='#374151', zorder=6)

    # Active center for Client modules
    client_cx = c_card_x + (c_card_w - 0.55) / 2.0  # = 5.15 + 2.925 = 8.075

    # 1. Local graph: IP nodes, flow edges (same as base paper)
    draw_node(client_cx, 8.0, 5.0, 0.85, "Local graph:\nIP nodes, flow edges", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)

    # 2. Three Specialized GATs (MODIFIED: blue)
    gat_y = 6.45
    gat_w = 1.35
    gat_h = 0.85
    gat1_cx = client_cx - 1.62
    gat2_cx = client_cx
    gat3_cx = client_cx + 1.62

    draw_node(gat1_cx, gat_y, gat_w, gat_h, "Temporal\nGAT", COLOR_BLUE_FILL, COLOR_BLUE_STROKE, fontsize=9.5)
    draw_node(gat2_cx, gat_y, gat_w, gat_h, "Content\nGAT", COLOR_BLUE_FILL, COLOR_BLUE_STROKE, fontsize=9.5)
    draw_node(gat3_cx, gat_y, gat_w, gat_h, "Behavioral\nGAT", COLOR_BLUE_FILL, COLOR_BLUE_STROKE, fontsize=9.5)

    draw_arrow((gat1_cx, 7.57), (gat1_cx, 6.88))
    draw_arrow((gat2_cx, 7.57), (gat2_cx, 6.88))
    draw_arrow((gat3_cx, 7.57), (gat3_cx, 6.88))

    # 3. Edge embeddings (same as base paper)
    emb_y = 5.0
    draw_node(client_cx, emb_y, 5.0, 0.75, "Edge embeddings", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)

    draw_arrow((gat1_cx, 6.02), (gat1_cx, 5.38))
    draw_arrow((gat2_cx, 6.02), (gat2_cx, 5.38))
    draw_arrow((gat3_cx, 6.02), (gat3_cx, 5.38))

    # 4. Joint Losses: CB-Focal & SupCon (NEW: orange)
    loss_y = 3.8
    l1_cx = client_cx - 1.2
    l2_cx = client_cx + 1.2
    l_w = 2.15
    l_h = 0.65

    draw_node(l1_cx, loss_y, l_w, l_h, "CB-Focal loss", COLOR_ORANGE_FILL, COLOR_ORANGE_STROKE, fontsize=9.5)
    draw_node(l2_cx, loss_y, l_w, l_h, "SupCon loss", COLOR_ORANGE_FILL, COLOR_ORANGE_STROKE, fontsize=9.5)

    draw_arrow((l1_cx, 4.62), (l1_cx, 4.13), color=COLOR_ORANGE_STROKE, lw=1.5)
    draw_arrow((l2_cx, 4.62), (l2_cx, 4.13), color=COLOR_ORANGE_STROKE, lw=1.5)

    # 5. Leiden communities (MODIFIED: blue)
    leiden_y = 2.65
    draw_node(client_cx, leiden_y, 3.4, 0.75, "Leiden communities", COLOR_BLUE_FILL, COLOR_BLUE_STROKE, fontsize=10.5)

    # Dual regularization arrows from both losses into Leiden
    draw_elbow([
        (l1_cx, loss_y - l_h/2.0),
        (l1_cx, 3.2),
        (client_cx - 0.6, 3.2),
        (client_cx - 0.6, leiden_y + 0.38)
    ], color=COLOR_BLUE_STROKE, lw=1.4)

    draw_elbow([
        (l2_cx, loss_y - l_h/2.0),
        (l2_cx, 3.2),
        (client_cx + 0.6, 3.2),
        (client_cx + 0.6, leiden_y + 0.38)
    ], color=COLOR_BLUE_STROKE, lw=1.4)

    # 6. Mean pooling (SIMPLIFIED: dashed border!)
    pool_y = 1.45
    draw_node(client_cx, pool_y, 3.4, 0.75, "Mean pooling", COLOR_GREY_FILL, '#4A5568', is_dashed=True, fontsize=10.5)
    draw_arrow((client_cx, 2.27), (client_cx, 1.83))

    # =========================================================================
    # COLUMN 3: SERVER
    # =========================================================================
    srv_x = 14.4
    srv_w = 2.85

    # 1. Overlay graph (top-k cosine) (SIMPLIFIED: dashed border!)
    draw_node(srv_x, 8.0, srv_w, 0.85, "Overlay graph\n(top-k cosine)", COLOR_GREY_FILL, '#4A5568', is_dashed=True, fontsize=10.5)

    # 2. GraphSAGE (2 layers) (MODIFIED: blue)
    draw_node(srv_x, 6.45, srv_w, 0.85, "GraphSAGE\n(2 layers)", COLOR_BLUE_FILL, COLOR_BLUE_STROKE, fontsize=10.5)
    draw_arrow((srv_x, 7.57), (srv_x, 6.88))

    # 3. FedAvg (SIMPLIFIED: dashed border!)
    draw_node(srv_x, 5.0, srv_w, 0.75, "FedAvg", COLOR_GREY_FILL, '#4A5568', is_dashed=True, fontsize=10.5)
    draw_arrow((srv_x, 6.02), (srv_x, 5.38))

    # 4. Random Forest meta-learner (same as base paper)
    draw_node(srv_x, 3.3, srv_w, 0.85, "Random Forest\nmeta-learner", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_arrow((srv_x, 4.62), (srv_x, 3.73), color=LINE_DARK, lw=1.5)

    # 5. Attack class prediction (same as base paper)
    draw_node(srv_x, 1.5, srv_w, 0.85, "Attack class\nprediction", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_arrow((srv_x, 2.87), (srv_x, 1.93))

    # =========================================================================
    # FULLY CONNECTED CROSS-BOUNDARY CONNECTIONS
    # =========================================================================

    # 1. Mean Pooling -> Overlay graph (Client pooled community centroids sent to server)
    draw_elbow([
        (client_cx + 1.7, pool_y),        # From right edge of Mean pooling
        (12.35, pool_y),                  # Across privacy boundary
        (12.35, 8.0),                     # Up through cross-boundary channel
        (srv_x - srv_w/2.0, 8.0)          # Enter Overlay graph
    ], text="community centroids", text_pos=(12.35, 7.15), color=COLOR_BLUE_STROKE, lw=1.8, text_bg=True)

    # 2. Bidirectional Federated Model Parameter Sync
    # Server -> Client: Model parameters broadcast (FedAvg -> Client GATs/Edge embeddings)
    draw_arrow((srv_x - srv_w/2.0, 5.2), (client_cx + 2.5, 5.2),
               text="model parameters", text_offset=(0, 0.22),
               color=COLOR_BLUE_STROKE, lw=1.8, text_bg=True)

    # Client -> Server: Local model updates upload
    draw_arrow((client_cx + 2.5, 4.75), (srv_x - srv_w/2.0, 4.75),
               text="local updates (θ_k)", text_offset=(0, -0.22),
               color='#4A5568', lw=1.5, ls='--', text_bg=True)

    # =========================================================================
    # LEGEND (Bottom Left, below Signature-grouped split)
    # =========================================================================
    leg_x = 0.55
    leg_y = 2.45
    spacing = 0.46
    box_w = 0.65
    box_h = 0.28

    # 1. same as base paper
    draw_node(leg_x + box_w/2.0, leg_y, box_w, box_h, "", COLOR_GREY_FILL, COLOR_GREY_STROKE)
    ax.text(leg_x + box_w + 0.18, leg_y, "same as base paper", ha='left', va='center', fontsize=9.5, fontweight='semibold', color=TEXT_DARK)

    # 2. modified
    draw_node(leg_x + box_w/2.0, leg_y - spacing, box_w, box_h, "", COLOR_BLUE_FILL, COLOR_BLUE_STROKE)
    ax.text(leg_x + box_w + 0.18, leg_y - spacing, "modified", ha='left', va='center', fontsize=9.5, fontweight='semibold', color=TEXT_DARK)

    # 3. new
    draw_node(leg_x + box_w/2.0, leg_y - 2*spacing, box_w, box_h, "", COLOR_ORANGE_FILL, COLOR_ORANGE_STROKE)
    ax.text(leg_x + box_w + 0.18, leg_y - 2*spacing, "new", ha='left', va='center', fontsize=9.5, fontweight='semibold', color=TEXT_DARK)

    # 4. simplified
    draw_node(leg_x + box_w/2.0, leg_y - 3*spacing, box_w, box_h, "", COLOR_GREY_FILL, '#4A5568', is_dashed=True)
    ax.text(leg_x + box_w + 0.18, leg_y - 3*spacing, "simplified", ha='left', va='center', fontsize=9.5, fontweight='semibold', color=TEXT_DARK)

    plt.tight_layout()
    for p in output_paths:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        plt.savefig(p, dpi=300, bbox_inches='tight', pad_inches=0.1)
        print(f"Generated: {p}")
    plt.close()


def generate_fc_baseline_diagram(output_paths):
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'Segoe UI'],
        'mathtext.fontset': 'dejavusans',
    })

    fig_w, fig_h = 16.8, 9.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    COLOR_GREY_FILL = '#D9D9D9'
    COLOR_GREY_STROKE = '#2D3748'
    COLOR_BLUE_FILL = '#92BCED'
    COLOR_BLUE_STROKE = '#245285'
    COLOR_PURPLE_FILL = '#C4B5FD'
    COLOR_PURPLE_STROKE = '#6D28D9'
    COLOR_CARD_BG = '#FFFFFF'
    COLOR_CARD_BORDER = '#212529'
    TEXT_DARK = '#111827'
    LINE_DARK = '#1F2937'

    outer_rect = patches.Rectangle((0.15, 0.15), fig_w - 0.30, fig_h - 0.30,
                                   fill=False, edgecolor='#111827', linewidth=2.2, zorder=1)
    ax.add_patch(outer_rect)

    def draw_node(cx, cy, w, h, text, fill_col, stroke_col, is_dashed=False, fontsize=10.0, fontweight='bold', text_color=TEXT_DARK, zorder=5):
        boxstyle = "round,pad=0.14,rounding_size=0.18"
        linestyle = '--' if is_dashed else '-'
        rect = patches.FancyBboxPatch(
            (cx - w/2.0, cy - h/2.0), w, h,
            boxstyle=boxstyle,
            facecolor=fill_col,
            edgecolor=stroke_col,
            linewidth=1.5,
            linestyle=linestyle,
            zorder=zorder
        )
        ax.add_patch(rect)
        if text:
            ax.text(cx, cy, text, ha='center', va='center',
                    fontsize=fontsize, fontweight=fontweight, color=text_color,
                    multialignment='center', zorder=zorder+1)
        return (cx, cy, w, h)

    def draw_arrow(start, end, text=None, text_offset=(0, 0), color=LINE_DARK, lw=1.5, ls='-', zorder=6, fontsize=8.8, text_color=TEXT_DARK, text_bg=True):
        ax.annotate(
            '', xy=end, xytext=start,
            arrowprops=dict(
                arrowstyle='->',
                color=color,
                lw=lw,
                linestyle=ls,
                shrinkA=2,
                shrinkB=2,
                mutation_scale=13
            ),
            zorder=zorder
        )
        if text:
            mx = (start[0] + end[0]) / 2.0 + text_offset[0]
            my = (start[1] + end[1]) / 2.0 + text_offset[1]
            bbox_props = dict(boxstyle='round,pad=0.18', fc='white', ec='#CBD5E0', lw=0.7, alpha=0.96) if text_bg else None
            ax.text(mx, my, text, ha='center', va='center', fontsize=fontsize,
                    fontweight='semibold', color=text_color, bbox=bbox_props, zorder=zorder+2)

    # Column Headers
    ax.text(2.1, 9.0, "Data Ingestion", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)
    ax.text(8.3, 9.0, "Client (×5) [Fully Connected MLP]", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)
    ax.text(14.4, 9.0, "Server", ha='center', va='center', fontsize=19, fontweight='bold', color=TEXT_DARK)

    # Column 1: Data
    data_x = 2.1
    draw_node(data_x, 7.8, 2.9, 0.9, "NF-ToN-IoT\n(real IPs)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_node(data_x, 5.8, 2.9, 0.9, "Feature extraction\n(24 NetFlow tabular feats)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.2)
    draw_arrow((data_x, 7.35), (data_x, 6.25))

    draw_node(data_x, 3.8, 2.9, 1.15, "Signature-grouped\nsplit (train / test,\n0% overlap)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.0)
    draw_arrow((data_x, 5.35), (data_x, 4.38))

    draw_arrow((data_x + 1.45, 3.8), (5.15, 3.8), text="local flow batches", text_offset=(0, 0.2), color=LINE_DARK, lw=1.6)

    # Column 2: Client x5 FC / MLP
    c_card_x = 5.15
    c_card_y = 0.55
    c_card_w = 6.4
    c_card_h = 8.0

    bg_card3 = patches.FancyBboxPatch(
        (c_card_x - 0.28, c_card_y + 0.28), c_card_w, c_card_h,
        boxstyle="round,pad=0.0,rounding_size=0.28",
        facecolor='#EDF2F7', edgecolor='#718096', linewidth=1.2, zorder=2
    )
    ax.add_patch(bg_card3)

    bg_card2 = patches.FancyBboxPatch(
        (c_card_x - 0.14, c_card_y + 0.14), c_card_w, c_card_h,
        boxstyle="round,pad=0.0,rounding_size=0.28",
        facecolor='#F7FAFC', edgecolor='#4A5568', linewidth=1.3, zorder=3
    )
    ax.add_patch(bg_card2)

    front_card = patches.FancyBboxPatch(
        (c_card_x, c_card_y), c_card_w, c_card_h,
        boxstyle="round,pad=0.0,rounding_size=0.28",
        facecolor=COLOR_CARD_BG, edgecolor=COLOR_CARD_BORDER, linewidth=1.8, zorder=4
    )
    ax.add_patch(front_card)

    p_bound_x = c_card_x + c_card_w - 0.55
    ax.plot([p_bound_x, p_bound_x], [c_card_y + 0.25, c_card_y + c_card_h - 0.25],
            color='#374151', linestyle='-', linewidth=1.6, zorder=5)
    ax.text(p_bound_x + 0.28, c_card_y + 4.0, "Privacy boundary",
            ha='center', va='center', rotation=90, fontsize=9.8, fontweight='bold', color='#374151', zorder=6)

    client_cx = c_card_x + (c_card_w - 0.55) / 2.0

    # FC Layers
    draw_node(client_cx, 7.8, 5.0, 0.85, "Input Tabular Flow Vector\nx ∈ R^24", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_node(client_cx, 6.4, 5.0, 0.85, "Dense Layer 1 (Fully Connected)\nLinear(24, 256) + BatchNorm + ReLU", COLOR_PURPLE_FILL, COLOR_PURPLE_STROKE, fontsize=10.0)
    draw_arrow((client_cx, 7.37), (client_cx, 6.83))

    draw_node(client_cx, 5.0, 5.0, 0.85, "Dense Layer 2 (Fully Connected)\nLinear(256, 128) + Dropout(0.2) + ReLU", COLOR_PURPLE_FILL, COLOR_PURPLE_STROKE, fontsize=10.0)
    draw_arrow((client_cx, 5.97), (client_cx, 5.43))

    draw_node(client_cx, 3.6, 5.0, 0.85, "Dense Layer 3 (Output Head)\nLinear(128, 8) -> Class Logits", COLOR_PURPLE_FILL, COLOR_PURPLE_STROKE, fontsize=10.0)
    draw_arrow((client_cx, 4.57), (client_cx, 4.03))

    draw_node(client_cx, 2.1, 5.0, 0.85, "Client Loss Engine\nCross-Entropy Loss (SGD / Adam)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_arrow((client_cx, 3.17), (client_cx, 2.53))

    # Server FC FedAvg
    srv_x = 14.4
    srv_w = 2.85

    draw_node(srv_x, 7.0, srv_w, 1.1, "Global Model Aggregator\n(FedAvg Parameter Sync)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_node(srv_x, 4.5, srv_w, 1.1, "Central Evaluator\n(Global Test Set)", COLOR_GREY_FILL, COLOR_GREY_STROKE, fontsize=10.5)
    draw_arrow((srv_x, 6.45), (srv_x, 5.05))

    draw_node(srv_x, 2.0, srv_w, 1.0, "Attack Class Prediction\n(8-Class Multi-Classification)", COLOR_BLUE_FILL, COLOR_BLUE_STROKE, fontsize=10.5)
    draw_arrow((srv_x, 3.95), (srv_x, 2.5))

    # Cross Boundary Arrows
    draw_arrow((srv_x - srv_w/2.0, 7.3), (client_cx + 2.5, 7.3),
               text="global weights (W_t)", text_offset=(0, 0.22),
               color=COLOR_BLUE_STROKE, lw=1.8, text_bg=True)

    draw_arrow((client_cx + 2.5, 6.7), (srv_x - srv_w/2.0, 6.7),
               text="local weights (W_t^k)", text_offset=(0, -0.22),
               color='#4A5568', lw=1.5, ls='--', text_bg=True)

    # Legend
    leg_x = 0.55
    leg_y = 2.1
    spacing = 0.46
    box_w = 0.65
    box_h = 0.28

    draw_node(leg_x + box_w/2.0, leg_y, box_w, box_h, "", COLOR_GREY_FILL, COLOR_GREY_STROKE)
    ax.text(leg_x + box_w + 0.18, leg_y, "Standard Component", ha='left', va='center', fontsize=9.5, fontweight='semibold', color=TEXT_DARK)

    draw_node(leg_x + box_w/2.0, leg_y - spacing, box_w, box_h, "", COLOR_PURPLE_FILL, COLOR_PURPLE_STROKE)
    ax.text(leg_x + box_w + 0.18, leg_y - spacing, "Fully Connected (Dense) Layer", ha='left', va='center', fontsize=9.5, fontweight='semibold', color=TEXT_DARK)

    draw_node(leg_x + box_w/2.0, leg_y - 2*spacing, box_w, box_h, "", COLOR_BLUE_FILL, COLOR_BLUE_STROKE)
    ax.text(leg_x + box_w + 0.18, leg_y - 2*spacing, "Classification / Output", ha='left', va='center', fontsize=9.5, fontweight='semibold', color=TEXT_DARK)

    plt.tight_layout()
    for p in output_paths:
        os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
        plt.savefig(p, dpi=300, bbox_inches='tight', pad_inches=0.1)
        print(f"Generated FC Baseline: {p}")
    plt.close()

if __name__ == '__main__':
    paths_fc = [
        'papers/paper_latex/figures/fig1_architecture.png',
        '../../fully_connected_arch.png',
        'C:/Users/musun/.gemini/antigravity-ide/brain/c7ce23d3-0bae-4463-8d85-428c8808fe22/fully_connected_arch.png'
    ]
    generate_fully_connected_diagram(paths_fc)

    paths_baseline = [
        'papers/paper_latex/figures/fig_fc_baseline_architecture.png',
        '../../fc_baseline_arch.png',
        'C:/Users/musun/.gemini/antigravity-ide/brain/c7ce23d3-0bae-4463-8d85-428c8808fe22/fc_baseline_arch.png'
    ]
    generate_fc_baseline_diagram(paths_baseline)
