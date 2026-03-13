"""
AI-Assisted Automotive Software Engineering Workflow
Architecture Diagram — ETAS / Ford Motor Company
"""

from reportlab.lib.pagesizes import landscape, A3
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

OUTPUT = "architecture_diagram.pdf"

# ── Palette ──────────────────────────────────────────────────────────────────
C_PURPLE_FILL   = colors.HexColor("#EEEDFE")
C_PURPLE_STROKE = colors.HexColor("#534AB7")
C_PURPLE_TEXT   = colors.HexColor("#3C3489")

C_TEAL_FILL     = colors.HexColor("#E1F5EE")
C_TEAL_STROKE   = colors.HexColor("#0F6E56")
C_TEAL_TEXT     = colors.HexColor("#085041")

C_AMBER_FILL    = colors.HexColor("#FAEEDA")
C_AMBER_STROKE  = colors.HexColor("#854F0B")
C_AMBER_TEXT    = colors.HexColor("#633806")

C_BLUE_FILL     = colors.HexColor("#E6F1FB")
C_BLUE_STROKE   = colors.HexColor("#185FA5")
C_BLUE_TEXT     = colors.HexColor("#0C447C")

C_CORAL_FILL    = colors.HexColor("#FAECE7")
C_CORAL_STROKE  = colors.HexColor("#993C1D")
C_CORAL_TEXT    = colors.HexColor("#712B13")

C_GREEN_FILL    = colors.HexColor("#EAF3DE")
C_GREEN_STROKE  = colors.HexColor("#3B6D11")
C_GREEN_TEXT    = colors.HexColor("#27500A")

C_PINK_FILL     = colors.HexColor("#FBEAF0")
C_PINK_STROKE   = colors.HexColor("#993556")
C_PINK_TEXT     = colors.HexColor("#72243E")

C_GRAY_FILL     = colors.HexColor("#F1EFE8")
C_GRAY_STROKE   = colors.HexColor("#5F5E5A")
C_GRAY_TEXT     = colors.HexColor("#444441")

C_ARROW         = colors.HexColor("#888780")
C_BG            = colors.HexColor("#FAFAF8")
C_SPINE_FILL    = colors.HexColor("#F4F0FF")
C_SPINE_STROKE  = colors.HexColor("#534AB7")

# ── Helpers ───────────────────────────────────────────────────────────────────
def box(c, x, y, w, h, fill, stroke, title, subtitle=None,
        title_size=8, sub_size=6.5, radius=4):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
    # title
    c.setFillColor(stroke)
    c.setFont("Helvetica-Bold", title_size)
    c.drawCentredString(x + w / 2, y + h / 2 + (5 if subtitle else 0), title)
    if subtitle:
        c.setFont("Helvetica", sub_size)
        c.setFillColor(colors.HexColor("#444441"))
        c.drawCentredString(x + w / 2, y + h / 2 - 6, subtitle)

def phase_label(c, x, y, w, h, text, fill, stroke):
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.6)
    c.roundRect(x, y, w, h, 3, fill=1, stroke=1)
    c.setFillColor(stroke)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(x + w / 2, y + h / 2 - 2.5, text)

def arrow_down(c, x, y1, y2):
    c.setStrokeColor(C_ARROW)
    c.setLineWidth(0.8)
    c.line(x, y1, x, y2)
    # arrowhead
    c.setFillColor(C_ARROW)
    p = c.beginPath()
    p.moveTo(x - 3, y2 + 5)
    p.lineTo(x + 3, y2 + 5)
    p.lineTo(x, y2)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

def spine_box(c, x, y, w, h, title, subtitle):
    c.setFillColor(C_PINK_FILL)
    c.setStrokeColor(C_PINK_STROKE)
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    c.setFillColor(C_PINK_STROKE)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawCentredString(x + w / 2, y + h - 12, title)
    c.setFont("Helvetica", 6)
    c.setFillColor(C_GRAY_TEXT)
    # wrap subtitle manually
    words = subtitle.split()
    line, lines = "", []
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Helvetica", 6) < w - 8:
            line = test
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    start_y = y + h - 24
    for l in lines:
        c.drawCentredString(x + w / 2, start_y, l)
        start_y -= 8

# ── Main ──────────────────────────────────────────────────────────────────────
def build():
    W, H = landscape(A3)  # 420 x 297 mm → ~1191 x 842 pts
    c = canvas.Canvas(OUTPUT, pagesize=landscape(A3))

    # Background
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Title block ──────────────────────────────────────────────────────────
    c.setFillColor(C_PURPLE_STROKE)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, H - 35, "AI-Assisted Automotive Software Engineering Workflow")
    c.setFont("Helvetica", 9)
    c.setFillColor(C_GRAY_TEXT)
    c.drawString(30, H - 50, "ETAS / Ford Motor Company  |  n8n + LangGraph Agentic Pipeline  |  AUTOSAR Classic (RTA-CAR)")

    # Divider
    c.setStrokeColor(C_GRAY_STROKE if False else colors.HexColor("#B4B2A9"))
    c.setLineWidth(0.5)
    c.line(30, H - 58, W - 30, H - 58)

    # ── Layout constants ─────────────────────────────────────────────────────
    LEFT        = 30
    PHASE_W     = 52
    GAP         = 8
    CONTENT_X   = LEFT + PHASE_W + GAP
    SPINE_W     = 90
    CONTENT_W   = W - CONTENT_X - SPINE_W - GAP - 30
    BOX_H       = 46
    ROW_GAP     = 14
    TOP_Y       = H - 75

    phases = [
        ("DEFINE",     C_PURPLE_FILL, C_PURPLE_STROKE),
        ("DESIGN",     C_TEAL_FILL,   C_TEAL_STROKE),
        ("CONFIGURE",  C_AMBER_FILL,  C_AMBER_STROKE),
        ("BUILD",      C_BLUE_FILL,   C_BLUE_STROKE),
        ("CI / CT / CD", C_CORAL_FILL, C_CORAL_STROKE),
        ("DELIVER",    C_GREEN_FILL,  C_GREEN_STROKE),
    ]

    rows = [
        # (title, subtitle, fill, stroke)
        [
            ("IBM DOORS", "Requirements authoring", C_PURPLE_FILL, C_PURPLE_STROKE),
            ("Jira", "Change mgmt / issues", C_PURPLE_FILL, C_PURPLE_STROKE),
            ("RTM Bridge", "DOORS \u2194 commits \u2194 tests", C_PURPLE_FILL, C_PURPLE_STROKE),
            ("AI Agent", "Req. review, gap analysis", C_PINK_FILL, C_PINK_STROKE),
        ],
        [
            ("Draw.io / EA", "System architecture", C_TEAL_FILL, C_TEAL_STROKE),
            ("Structurizr / C4", "Component + context views", C_TEAL_FILL, C_TEAL_STROKE),
            ("ARXML Linter", "Schema + interface validation", C_TEAL_FILL, C_TEAL_STROKE),
            ("AI Agent", "Design review, tradeoffs", C_PINK_FILL, C_PINK_STROKE),
        ],
        [
            ("ETAS RTA-CAR", "BSW / RTE / SWC config", C_AMBER_FILL, C_AMBER_STROKE),
            ("MATLAB / Simulink", "Model-based design, codegen", C_AMBER_FILL, C_AMBER_STROKE),
            ("Embedded AI Coder", "NN \u2192 optimized ECU C code", C_AMBER_FILL, C_AMBER_STROKE),
            ("AI Agent", "Config lint, schema checks", C_PINK_FILL, C_PINK_STROKE),
        ],
        [
            ("GNU Make", "Build orchestration", C_BLUE_FILL, C_BLUE_STROKE),
            ("TASKING Compiler", "Cross-compile ECU targets", C_BLUE_FILL, C_BLUE_STROKE),
            ("PC-lint / Polyspace", "MISRA static analysis", C_BLUE_FILL, C_BLUE_STROKE),
            ("Artifactory", "Binary / SWC artifact store", C_BLUE_FILL, C_BLUE_STROKE),
        ],
        [
            ("GitHub", "SCM, PR triggers", C_CORAL_FILL, C_CORAL_STROKE),
            ("Jenkins", "Pipeline orchestration", C_CORAL_FILL, C_CORAL_STROKE),
            ("VectorCAST / LDRA", "Unit + integration testing", C_CORAL_FILL, C_CORAL_STROKE),
            ("Docker", "Reproducible build envs", C_CORAL_FILL, C_CORAL_STROKE),
        ],
        [
            ("dSPACE HIL", "Hardware-in-the-loop", C_GREEN_FILL, C_GREEN_STROKE),
            ("Release Package", "Binaries, A2L, traceability", C_GREEN_FILL, C_GREEN_STROKE),
            ("AI Calibration", "ETAS AI calibration suite", C_GREEN_FILL, C_GREEN_STROKE),
            ("AI Agent", "Release notes, sign-off", C_PINK_FILL, C_PINK_STROKE),
        ],
    ]

    n_boxes   = 4
    box_w     = (CONTENT_W - (n_boxes - 1) * GAP) / n_boxes

    row_tops = []
    for i, (phase, boxes) in enumerate(zip(phases, rows)):
        row_y = TOP_Y - i * (BOX_H + ROW_GAP)
        row_tops.append(row_y)

        # Phase label (left column)
        phase_label(c, LEFT, row_y, PHASE_W, BOX_H,
                    phase[0], phase[1], phase[2])

        # Tool boxes
        for j, (title, subtitle, fill, stroke) in enumerate(boxes):
            bx = CONTENT_X + j * (box_w + GAP)
            box(c, bx, row_y, box_w, BOX_H, fill, stroke, title, subtitle)

        # Down arrow (between rows, centred on content area)
        if i < len(phases) - 1:
            ax = CONTENT_X + CONTENT_W / 2
            arrow_down(c, ax, row_y - 1, row_y - ROW_GAP + 3)

    # ── AI Orchestration Spine ────────────────────────────────────────────────
    spine_x = W - 30 - SPINE_W
    spine_y = row_tops[-1]
    spine_h = row_tops[0] + BOX_H - spine_y

    c.setFillColor(C_SPINE_FILL)
    c.setStrokeColor(C_SPINE_STROKE)
    c.setLineWidth(1)
    c.setDash(4, 3)
    c.roundRect(spine_x, spine_y, SPINE_W, spine_h, 5, fill=1, stroke=1)
    c.setDash()

    # Rotated spine label
    c.saveState()
    c.translate(spine_x + SPINE_W / 2, spine_y + spine_h / 2)
    c.rotate(90)
    c.setFillColor(C_SPINE_STROKE)
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(0, 4, "n8n + LangGraph  |  AI Orchestration Pipeline")
    c.setFont("Helvetica", 6.5)
    c.setFillColor(C_GRAY_TEXT)
    c.drawCentredString(0, -7, "Ollama local LLM  |  FastAPI microservices  |  Agentic task routing")
    c.restoreState()

    # ── Legend ────────────────────────────────────────────────────────────────
    legend_y = row_tops[-1] - 28
    legend_items = [
        (C_PURPLE_FILL, C_PURPLE_STROKE, "Requirements / Change"),
        (C_TEAL_FILL,   C_TEAL_STROKE,   "Architecture / Design"),
        (C_AMBER_FILL,  C_AMBER_STROKE,  "AUTOSAR Configuration"),
        (C_BLUE_FILL,   C_BLUE_STROKE,   "Build & Analysis"),
        (C_CORAL_FILL,  C_CORAL_STROKE,  "CI / CT / CD"),
        (C_GREEN_FILL,  C_GREEN_STROKE,  "Delivery / Validation"),
        (C_PINK_FILL,   C_PINK_STROKE,   "AI Agent (n8n/LangGraph)"),
    ]
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(C_GRAY_TEXT)
    c.drawString(CONTENT_X, legend_y + 5, "Legend:")
    lx = CONTENT_X + 42
    for fill, stroke, label in legend_items:
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.setLineWidth(0.5)
        c.roundRect(lx, legend_y, 12, 10, 2, fill=1, stroke=1)
        c.setFillColor(C_GRAY_TEXT)
        c.setFont("Helvetica", 6.5)
        c.drawString(lx + 15, legend_y + 2.5, label)
        lx += c.stringWidth(label, "Helvetica", 6.5) + 30

    # ── Footer ────────────────────────────────────────────────────────────────
    c.setFont("Helvetica", 6)
    c.setFillColor(colors.HexColor("#B4B2A9"))
    c.drawString(LEFT, 14,
        "AI-Assisted ASE Workflow  |  ETAS / Ford Motor Company  |  "
        "github.com/mathew/etas-ford-ai-workflow  |  v0.1.0")
    c.drawRightString(W - 30, 14, "ISO 26262 / ASPICE aware  |  AUTOSAR Classic (RTA-CAR)")

    c.save()
    print(f"PDF written: {OUTPUT}")

if __name__ == "__main__":
    build()
