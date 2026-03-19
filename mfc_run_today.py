import csv
from collections import defaultdict

# =========================
# CONFIG & COLOR PALETTE
# =========================
BACKBONE = ["Model", "M/A", "AOI", "SPOT", "Sealer", "FA"]

MODEL_COLORS = {
    "DC1U/1V": "#0097E6",
    "DC1A/GP2A": "#0097E6",
    "GD1B": "#0097E6",
    "HONDA_A3": "#44BD32",
    "CNG": "#FFA600",
    "Cbmu": "#10AC84",
    "ISS BMU":"#028F25",
    "Pwc": "#833471",
    "GP1Y": "#C23616",
    "GP2Y": "#0026FF",
    "A/B MSIL A3":"#EB92D6",
    "HV 5/YY8 EV":"#EECD8F",
    "All AC":"#6E6E6E",
    "DEFAULT": "#2F3640"
}

STAGE_COLORS = {
    "M/A": "#F7F7F7",
    "AOI": "#EEF5FF",
    "SPOT": "#FFF4E6",
    "Sealer": "#EEF8F0",
    "FA": "#F3EEFF"
}

def safe_id(text):
    return "".join(c if c.isalnum() else "_" for c in text)

# =========================
# LOAD PROCESS STRUCTURE
# =========================
process_seq = {}
stage_processes = defaultdict(list)

with open("process_structure.csv", newline="") as f:
    for r in csv.DictReader(f):
        stage_processes[r["Stage"]].append(r["ProcessName"])
        if r["Behavior"] == "SEQUENTIAL" and r.get("SequenceOrder"):
            process_seq[r["ProcessName"]] = int(r["SequenceOrder"])

# =========================
# LOAD MODEL MATRIX (ROUTE AWARE)
# =========================
models = []
model_routes = defaultdict(list)

with open("model_process_matrix.csv", newline="") as f:
    reader = csv.DictReader(f)
    process_columns = reader.fieldnames[2:]  # Model, Route, then processes

    for r in reader:
        model = r["Model"]
        route = r["Route"]

        if model not in models:
            models.append(model)

        model_routes[model].append({
            "route": route,
            "processes": {p: (r[p] == "1") for p in process_columns}
        })

# =========================
# BUILD GRAPHVIZ DOT
# =========================
dot = ["digraph MFC {"]
dot.append("  rankdir=LR; splines=ortho; nodesep=0.4; ranksep=1.2;")
dot.append("  node [shape=rect, style=\"filled,rounded\", fontname=\"Segoe UI Semibold\", fontsize=10, height=0.45, width=1.1];")
dot.append("  edge [penwidth=2.2, arrowhead=vee, arrowsize=0.8];")

# ALIGNMENT ANCHORS
top_nodes = [f"TOP_{s.replace('/', '_').replace(' ', '_')}" for s in BACKBONE]
dot.append("  { rank=same; " + " ".join([f"\"{n}\" [style=invis, width=0, height=0];" for n in top_nodes]) + " }")

# MODEL COLUMN
dot.append("  subgraph cluster_Models { style=invis;")
for m in models:
    c = MODEL_COLORS.get(m, MODEL_COLORS["DEFAULT"])
    dot.append(f"    \"{m}\" [fillcolor=\"#FFFFFF\", color=\"{c}\", penwidth=3, fontname=\"Segoe UI Bold\"];")
dot.append("  }")

# PROCESS STAGES (UNCHANGED)
for stage in BACKBONE[1:]:
    cid = stage.replace("/", "_").replace(" ", "_")
    bgcolor = STAGE_COLORS.get(stage, "#FFFFFF")

    dot.append(f"  subgraph cluster_{cid} {{")
    dot.append(f"    label=\"{stage}\"; labelloc=\"t\"; fontname=\"Segoe UI Bold\"; fontsize=12;")
    dot.append(f"    style=\"filled,rounded\"; color=\"#D1D1D1\"; bgcolor=\"{bgcolor}\"; margin=20;")

    for p in stage_processes.get(stage, []):
        is_dashed = "AOI" in stage or "AB-" in p or "MA-5" in p or "SPOT-2" in p
        b_style = "dashed" if is_dashed else "solid"
        b_color = "#2E5BFF" if is_dashed else "#777777" # Blue dash for emphasis
        dot.append(f"    \"{p}\" [fillcolor=\"#FFFFFF\", style=\"filled,rounded,{b_style}\", color=\"{b_color}\", penwidth=1.5];")
    dot.append("  }")

# =========================
# FLOW LOGIC (ROUTES) — FIXED
# =========================
for model, routes in model_routes.items():
    e_color = MODEL_COLORS.get(model, MODEL_COLORS["DEFAULT"])

    for route in routes:
        prev_nodes = [model]
        proc_map = route["processes"]

        for stage in BACKBONE[1:]:
            active = [p for p in stage_processes.get(stage, []) if proc_map.get(p)]
            if not active:
                continue

            # ---- GENERALIZED SEQUENTIAL LOGIC ----
            seq = [p for p in active if p in process_seq]

            if len(seq) > 1:
                seq.sort(key=lambda x: process_seq[x])

                dot.append(
                f"  \"{prev_nodes[0]}\" -> \"{seq[0]}\" "
                f"[color=\"{e_color}\",model=\"{safe_id(model)}\"];"
                )

                for i in range(len(seq) - 1):
                    dot.append(
                        f"  \"{seq[i]}\" -> \"{seq[i+1]}\" "
                        f"[color=\"{e_color}\",model=\"{safe_id(model)}\"];"
                    )
                prev_nodes = [seq[-1]]

            else:
                next_nodes = []
                for p in active:
                    for prev in prev_nodes:             
                        dot.append(
                            f"  \"{prev}\" -> \"{p}\" "
                            f"[color=\"{e_color}\",model=\"{safe_id(model)}\"];"
                        )
                    next_nodes.append(p)
                prev_nodes = next_nodes

dot.append("}")

dot_text = "\n".join(dot)

# Force ASCII arrows only
dot_text = dot_text.replace("–>", "->") \
                   .replace("→", "->") \
                   .replace("‑>", "->")

with open("mfc_colored.dot", "w", encoding="utf-8") as f:
    f.write(dot_text)


print("✅ Route issue fixed without changing visuals: mfc_colored.dot")