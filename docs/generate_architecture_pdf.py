"""
=============================================================================
File:    docs/generate_architecture_pdf.py
Project: AI-Assisted Automotive Software Engineering Workflow
Author:  Mathew S. Crawford
Contact: mathew.s.crawford@gmail.com | 734-765-4143
         linkedin.com/in/mathewscrawford
GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
License: MIT
Purpose: Generates A3 landscape architecture diagram PDF via reportlab
=============================================================================
"""

from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfgen import canvas
from reportlab.lib import colors

OUTPUT = "architecture_diagram.pdf"

# ── Palette ───────────────────────────────────────────────────────────────────
C_PURPLE_FILL   = colors.HexColor("#EEEDFE")
C_PURPLE_STROKE = colors.HexColor("#534AB7")
C_TEAL_FILL     = colors.HexColor("#E1F5EE")
C_TEAL_STROKE   = colors.HexColor("#0F6E56")
C_AMBER_FILL    = colors.HexColor("#FAEEDA")
C_AMBER_STROKE  = colors.HexColor("#854F0B")
C_BLUE_FILL     = colors.HexColor("#E6F1FB")
C_BLUE_STROKE   = colors.HexColor("#185FA5")
C_CORAL_FILL    = colors.HexColor("#FAECE7")
C_CORAL_STROKE  = colors.HexColor("#993C1D")
C_GREEN_FILL    = colors.HexColor("#EAF3DE")
C_GREEN_STROKE  = colors.HexColor("#3B6D11")
C_PINK_FILL     = colors.HexColor("#FBEAF0")
C_PINK_STROKE   = colors.HexColor("#993556")
C_GRAY_TEXT     = colors.HexColor("#444441")
C_ORCH_FILL     = colors.HexColor("#2D1B69")
C_ORCH_TEXT     = colors.HexColor("#FFFFFF")
C_ARROW         = colors.HexColor("#888780")
C_ARROW_AI      = colors.HexColor("#993556")
C_BG            = colors.HexColor("#FAFAF8")


# ── Helpers ───────────────────────────────────────────────────────────────────
def filled_box(cv, x, y, w, h, fill, stroke, title, subtitle=None,
               title_size=8, sub_size=6.5, radius=4):
    cv.setFillColor(fill)
    cv.setStrokeColor(stroke)
    cv.setLineWidth(0.5)
    cv.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    cv.setFillColor(stroke)
    cv.setFont("Helvetica-Bold", title_size)
    cv.drawCentredString(x + w / 2, y + h / 2 + (5 if subtitle else 0), title)
    if subtitle:
        cv.setFont("Helvetica", sub_size)
        cv.setFillColor(C_GRAY_TEXT)
        cv.drawCentredString(x + w / 2, y + h / 2 - 6, subtitle)


def phase_label(cv, x, y, w, h, text, fill, stroke):
    cv.setFillColor(fill)
    cv.setStrokeColor(stroke)
    cv.setLineWidth(0.6)
    cv.roundRect(x, y, w, h, 3, fill=1, stroke=1)
    cv.setFillColor(stroke)
    cv.setFont("Helvetica-Bold", 7)
    cv.drawCentredString(x + w / 2, y + h / 2 - 2.5, text)


def arrow_down(cv, x, y1, y2, color=None):
    col = color or C_ARROW
    cv.setStrokeColor(col)
    cv.setLineWidth(0.8)
    cv.line(x, y1, x, y2 + 5)
    cv.setFillColor(col)
    p = cv.beginPath()
    p.moveTo(x - 3, y2 + 5)
    p.lineTo(x + 3, y2 + 5)
    p.lineTo(x, y2)
    p.close()
    cv.drawPath(p, fill=1, stroke=0)


def arrowhead_left(cv, tip_x, cy, color):
    cv.setFillColor(color)
    p = cv.beginPath()
    p.moveTo(tip_x + 6, cy + 3)
    p.lineTo(tip_x + 6, cy - 3)
    p.lineTo(tip_x, cy)
    p.close()
    cv.drawPath(p, fill=1, stroke=0)


# ── Main ──────────────────────────────────────────────────────────────────────
def build():
    W, H = landscape(A3)   # ~1191 x 842 pts
    cv = canvas.Canvas(OUTPUT, pagesize=landscape(A3))

    # Background
    cv.setFillColor(C_BG)
    cv.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Title ─────────────────────────────────────────────────────────────────
    cv.setFillColor(C_PURPLE_STROKE)
    cv.setFont("Helvetica-Bold", 15)
    cv.drawString(30, H - 33,
        "AI-Assisted Automotive Software Engineering Workflow")
    cv.setFont("Helvetica", 8.5)
    cv.setFillColor(C_GRAY_TEXT)
    cv.drawString(30, H - 47,
        "ETAS / Ford Motor Company  \u2022  n8n + LangGraph Agentic Pipeline"
        "  \u2022  AUTOSAR Classic (RTA-CAR)  \u2022  ISO 26262 / ASPICE-aware")
    cv.setStrokeColor(colors.HexColor("#B4B2A9"))
    cv.setLineWidth(0.5)
    cv.line(30, H - 55, W - 30, H - 55)

    # ── Layout ────────────────────────────────────────────────────────────────
    LEFT         = 30
    RIGHT_MARGIN = 30
    PHASE_W      = 50
    GAP          = 8
    BOX_H        = 46
    ROW_GAP      = 14

    # Orchestrator sits just below title divider (divider at H-55)
    # In reportlab y is always the BOTTOM-LEFT corner of a rect.
    ORCH_H    = 40
    ORCH_TOP  = H - 55 - 8            # top edge of orch block (= y + h)
    ORCH_BOT  = ORCH_TOP - ORCH_H     # bottom edge = roundRect y argument
    # TOP_Y = bottom edge of row 0 box.
    # Row 0 top edge = TOP_Y + BOX_H, must be <= ORCH_BOT - ROW_GAP
    TOP_Y     = ORCH_BOT - ROW_GAP - BOX_H

    # Columns: 3 tool cols | AI agent col | spine col
    ORCH_W   = 100
    AI_W     = 112
    TOOL_W   = (W - LEFT - PHASE_W - GAP           # phase
                - 3 * GAP                          # inter-tool gaps (2) + ai gap (1)
                - AI_W - GAP - ORCH_W              # AI col + spine
                - RIGHT_MARGIN) / 3

    CONTENT_X = LEFT + PHASE_W + GAP
    AI_COL_X  = CONTENT_X + 3 * TOOL_W + 3 * GAP
    ORCH_X    = AI_COL_X + AI_W + GAP

    # ── Row definitions ───────────────────────────────────────────────────────
    phases = [
        ("DEFINE",       C_PURPLE_FILL, C_PURPLE_STROKE),
        ("DESIGN",       C_TEAL_FILL,   C_TEAL_STROKE),
        ("CONFIGURE",    C_AMBER_FILL,  C_AMBER_STROKE),
        ("BUILD",        C_BLUE_FILL,   C_BLUE_STROKE),
        ("CI / CT / CD", C_CORAL_FILL,  C_CORAL_STROKE),
        ("DELIVER",      C_GREEN_FILL,  C_GREEN_STROKE),
    ]

    tool_rows = [
        [
            ("IBM DOORS",        "Requirements authoring",        C_PURPLE_FILL, C_PURPLE_STROKE),
            ("Jira",             "Change mgmt / issues",          C_PURPLE_FILL, C_PURPLE_STROKE),
            ("RTM Bridge",       "DOORS \u2194 commits \u2194 tests", C_PURPLE_FILL, C_PURPLE_STROKE),
        ],
        [
            ("Draw.io / EA",     "System architecture",           C_TEAL_FILL,   C_TEAL_STROKE),
            ("Structurizr / C4", "Component + context views",     C_TEAL_FILL,   C_TEAL_STROKE),
            ("ARXML Linter",     "Schema + interface validation",  C_TEAL_FILL,   C_TEAL_STROKE),
        ],
        [
            ("ETAS RTA-CAR",     "BSW / RTE / SWC config",        C_AMBER_FILL,  C_AMBER_STROKE),
            ("MATLAB/Simulink",  "Model-based design, codegen",    C_AMBER_FILL,  C_AMBER_STROKE),
            ("Embedded AI Coder","NN \u2192 optimized ECU C",      C_AMBER_FILL,  C_AMBER_STROKE),
        ],
        [
            ("GNU Make",         "Build orchestration",           C_BLUE_FILL,   C_BLUE_STROKE),
            ("TASKING Compiler", "Cross-compile ECU targets",     C_BLUE_FILL,   C_BLUE_STROKE),
            ("PC-lint/Polyspace","MISRA static analysis",         C_BLUE_FILL,   C_BLUE_STROKE),
        ],
        [
            ("GitHub",           "SCM, PR triggers",              C_CORAL_FILL,  C_CORAL_STROKE),
            ("Jenkins",          "Pipeline orchestration",        C_CORAL_FILL,  C_CORAL_STROKE),
            ("Docker",           "Reproducible build envs",       C_CORAL_FILL,  C_CORAL_STROKE),
        ],
        [
            ("dSPACE HIL",       "Hardware-in-the-loop",          C_GREEN_FILL,  C_GREEN_STROKE),
            ("Release Package",  "Binaries, A2L, traceability",   C_GREEN_FILL,  C_GREEN_STROKE),
            ("AI Calibration",   "ETAS AI calibration suite",     C_GREEN_FILL,  C_GREEN_STROKE),
        ],
    ]

    ai_agents = [
        ("Req. Agent",     "Gap analysis, ambiguity"),
        ("Design Agent",   "Review, tradeoffs"),
        ("Config Agent",   "ARXML lint, schema checks"),
        ("Build Agent",    "Log triage, MISRA summary"),
        ("Test Agent",     "Test gen, failure RCA"),
        ("Release Agent",  "Notes, sign-off checklist"),
    ]

    # ── Draw phase rows ───────────────────────────────────────────────────────
    row_tops      = []
    agent_centers = []

    for i, (phase, tools, agent) in enumerate(
            zip(phases, tool_rows, ai_agents)):
        row_y = TOP_Y - i * (BOX_H + ROW_GAP)
        row_tops.append(row_y)

        phase_label(cv, LEFT, row_y, PHASE_W, BOX_H,
                    phase[0], phase[1], phase[2])

        for j, (title, sub, fill, stroke) in enumerate(tools):
            bx = CONTENT_X + j * (TOOL_W + GAP)
            filled_box(cv, bx, row_y, TOOL_W, BOX_H,
                       fill, stroke, title, sub)

        filled_box(cv, AI_COL_X, row_y, AI_W, BOX_H,
                   C_PINK_FILL, C_PINK_STROKE,
                   agent[0], agent[1])
        agent_centers.append((
            AI_COL_X + AI_W / 2,
            row_y + BOX_H / 2,
        ))

        if i < len(phases) - 1:
            ax = CONTENT_X + (3 * TOOL_W + 2 * GAP) / 2
            arrow_down(cv, ax, row_y - 1, row_y - ROW_GAP + 3)

    # ── Orchestrator header block ─────────────────────────────────────────────
    ORCH_BX = AI_COL_X                       # aligns with AI col left edge
    ORCH_BW = AI_W + GAP + ORCH_W            # spans AI col + spine

    cv.setFillColor(C_ORCH_FILL)
    cv.setStrokeColor(C_PINK_STROKE)
    cv.setLineWidth(1.2)
    cv.roundRect(ORCH_BX, ORCH_BOT, ORCH_BW, ORCH_H, 5, fill=1, stroke=1)
    cv.setFillColor(C_ORCH_TEXT)
    cv.setFont("Helvetica-Bold", 9)
    cv.drawCentredString(ORCH_BX + ORCH_BW / 2,
                         ORCH_BOT + ORCH_H / 2 + 4,
                         "n8n + LangGraph  |  AI Orchestrator")
    cv.setFont("Helvetica", 7)
    cv.setFillColor(colors.HexColor("#DDD8FF"))
    cv.drawCentredString(ORCH_BX + ORCH_BW / 2,
                         ORCH_BOT + ORCH_H / 2 - 6,
                         "Ollama (phi4-mini)  \u2022  FastAPI microservices  \u2022  Agentic task routing")

    # Main arrow: orchestrator bottom → first agent top
    orch_cx = AI_COL_X + AI_W / 2
    arrow_down(cv, orch_cx,
               ORCH_BOT - 1,
               row_tops[0] + BOX_H + 1,
               color=C_ARROW_AI)

    # Vertical rail on right side of AI col → connects to all agents
    rail_x = AI_COL_X + AI_W + GAP / 2

    cv.setStrokeColor(C_ARROW_AI)
    cv.setLineWidth(0.75)
    cv.setDash(4, 3)
    cv.line(rail_x, ORCH_BOT, rail_x, agent_centers[-1][1])
    cv.setDash()

    # Horizontal stubs from rail → each agent box right edge (rows 1-5)
    for i, (ax, ay) in enumerate(agent_centers):
        if i == 0:
            continue
        cv.setStrokeColor(C_ARROW_AI)
        cv.setLineWidth(0.75)
        cv.setDash(4, 3)
        cv.line(rail_x, ay, AI_COL_X + AI_W + 2, ay)
        cv.setDash()
        arrowhead_left(cv, AI_COL_X + AI_W, ay, C_ARROW_AI)

    # ── Orchestrator → Docker connection ──────────────────────────────────────
    # Route: from orch block bottom-centre → down through gap between
    # tool col 3 and AI col → right into Docker right edge
    docker_row_y  = row_tops[4]
    docker_x      = CONTENT_X + 2 * (TOOL_W + GAP)   # col 2 left edge
    docker_right  = docker_x + TOOL_W                 # col 2 right edge
    docker_cy     = docker_row_y + BOX_H / 2

    # Vertical rail runs in the gap between tool col 3 and AI col
    gap_rail_x    = AI_COL_X - GAP / 2                # midpoint of that gap

    # Start from orch block bottom (centre of AI col portion)
    orch_cx_ai    = AI_COL_X + AI_W / 2

    cv.setStrokeColor(C_ARROW_AI)
    cv.setLineWidth(0.85)
    cv.setDash(5, 3)
    # Vertical drop from orch bottom down to Docker row midpoint
    cv.line(gap_rail_x, ORCH_BOT, gap_rail_x, docker_cy)
    # Horizontal from gap rail right into Docker right edge
    cv.line(gap_rail_x, docker_cy, docker_right - 1, docker_cy)
    cv.setDash()
    arrowhead_left(cv, docker_right, docker_cy, C_ARROW_AI)

    # Small connector from orch block bottom to the gap rail (short horizontal)
    cv.setStrokeColor(C_ARROW_AI)
    cv.setLineWidth(0.85)
    cv.setDash(5, 3)
    cv.line(ORCH_BX, ORCH_BOT + ORCH_H / 2, gap_rail_x, ORCH_BOT + ORCH_H / 2)
    cv.line(gap_rail_x, ORCH_BOT + ORCH_H / 2, gap_rail_x, ORCH_BOT)
    cv.setDash()

    cv.setFillColor(C_ARROW_AI)
    cv.setFont("Helvetica", 5.5)
    cv.drawString(gap_rail_x + 2, docker_cy + 4, "env provisioning")

    # ── Spine background ──────────────────────────────────────────────────────
    spine_y = row_tops[-1]
    spine_h = row_tops[0] + BOX_H - spine_y
    cv.setFillColor(colors.HexColor("#F4F0FF"))
    cv.setStrokeColor(C_PURPLE_STROKE)
    cv.setLineWidth(0.8)
    cv.setDash(4, 3)
    cv.roundRect(ORCH_X, spine_y, ORCH_W, spine_h, 5, fill=1, stroke=1)
    cv.setDash()

    cv.saveState()
    cv.translate(ORCH_X + ORCH_W / 2, spine_y + spine_h / 2)
    cv.rotate(90)
    cv.setFillColor(C_PURPLE_STROKE)
    cv.setFont("Helvetica-Bold", 7.5)
    cv.drawCentredString(0, 5, "AI Orchestration Pipeline")
    cv.setFont("Helvetica", 6)
    cv.setFillColor(C_GRAY_TEXT)
    cv.drawCentredString(0, -6, "Per-phase agentic task dispatch")
    cv.restoreState()

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_y = row_tops[-1] - 25
    legend_items = [
        (C_PURPLE_FILL, C_PURPLE_STROKE, "Requirements / Change"),
        (C_TEAL_FILL,   C_TEAL_STROKE,   "Architecture / Design"),
        (C_AMBER_FILL,  C_AMBER_STROKE,  "AUTOSAR Config"),
        (C_BLUE_FILL,   C_BLUE_STROKE,   "Build & Analysis"),
        (C_CORAL_FILL,  C_CORAL_STROKE,  "CI / CT / CD"),
        (C_GREEN_FILL,  C_GREEN_STROKE,  "Delivery / Validation"),
        (C_PINK_FILL,   C_PINK_STROKE,   "AI Agent (LangGraph)"),
    ]
    cv.setFont("Helvetica-Bold", 7)
    cv.setFillColor(C_GRAY_TEXT)
    cv.drawString(CONTENT_X, legend_y + 4, "Legend:")
    lx = CONTENT_X + 40
    for fill, stroke, label in legend_items:
        cv.setFillColor(fill)
        cv.setStrokeColor(stroke)
        cv.setLineWidth(0.5)
        cv.roundRect(lx, legend_y, 11, 9, 2, fill=1, stroke=1)
        cv.setFillColor(C_GRAY_TEXT)
        cv.setFont("Helvetica", 6.5)
        cv.drawString(lx + 14, legend_y + 2, label)
        lx += cv.stringWidth(label, "Helvetica", 6.5) + 28

    # ── Footer ────────────────────────────────────────────────────────────────
    cv.setFont("Helvetica-Bold", 7.5)
    cv.setFillColor(C_PURPLE_STROKE)
    cv.drawString(LEFT, 23, "Mathew S. Crawford")
    cv.setFont("Helvetica", 6.5)
    cv.setFillColor(C_GRAY_TEXT)
    cv.drawString(LEFT, 13,
        "mathew.s.crawford@gmail.com  \u2022  734-765-4143  "
        "\u2022  linkedin.com/in/mathewscrawford")
    cv.setFont("Helvetica", 6)
    cv.setFillColor(colors.HexColor("#B4B2A9"))
    cv.drawRightString(W - RIGHT_MARGIN, 23,
        "AI-Assisted ASE Workflow  |  ETAS / Ford Motor Company  |  v0.1.0")
    cv.drawRightString(W - RIGHT_MARGIN, 13,
        "ISO 26262 / ASPICE aware  |  AUTOSAR Classic (RTA-CAR)")

    cv.save()
    print(f"PDF written: {OUTPUT}")


if __name__ == "__main__":
    build()
