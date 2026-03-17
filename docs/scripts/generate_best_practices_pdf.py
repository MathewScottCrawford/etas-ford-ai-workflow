"""
=============================================================================
File:    generate_best_practices_pdf.py
Project: AI-Assisted Automotive Software Engineering Workflow
Author:  Mathew S. Crawford
Contact: mathew.s.crawford@gmail.com | 734-765-4143
         linkedin.com/in/mathewscrawford
GitHub:  github.com/MathewScottCrawford/etas-ford-ai-workflow
License: MIT
Purpose: Generates ASE-workflow-best-practices.pdf for docs/
=============================================================================
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

OUTPUT = "ASE-workflow-best-practices.pdf"

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY       = colors.HexColor("#1E2761")
ICE_BLUE   = colors.HexColor("#CADCFC")
ACCENT     = colors.HexColor("#E8A838")
MID_BLUE   = colors.HexColor("#4A6FA5")
OFF_WHITE  = colors.HexColor("#F4F6FB")
LIGHT_GRAY = colors.HexColor("#E8ECF4")
TEXT_DARK  = colors.HexColor("#1A1E3C")
TEXT_MID   = colors.HexColor("#3D4F7C")
MUTED      = colors.HexColor("#8A9BC4")
GREEN_BG   = colors.HexColor("#EAF5EE")
GREEN_TEXT = colors.HexColor("#2E7D52")
AMBER_BG   = colors.HexColor("#FEF3C7")
AMBER_TEXT = colors.HexColor("#B45309")

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "DocTitle",
    fontName="Helvetica-Bold",
    fontSize=20,
    textColor=NAVY,
    spaceAfter=4,
    leading=24,
)
subtitle_style = ParagraphStyle(
    "DocSubtitle",
    fontName="Helvetica",
    fontSize=11,
    textColor=MUTED,
    spaceAfter=2,
)
meta_style = ParagraphStyle(
    "Meta",
    fontName="Helvetica",
    fontSize=8.5,
    textColor=MUTED,
    spaceAfter=0,
)
section_header_style = ParagraphStyle(
    "SectionHeader",
    fontName="Helvetica-Bold",
    fontSize=13,
    textColor=NAVY,
    spaceBefore=18,
    spaceAfter=4,
)
bp_number_style = ParagraphStyle(
    "BPNumber",
    fontName="Helvetica-Bold",
    fontSize=11,
    textColor=MID_BLUE,
    spaceBefore=14,
    spaceAfter=2,
)
bp_title_style = ParagraphStyle(
    "BPTitle",
    fontName="Helvetica-Bold",
    fontSize=11,
    textColor=TEXT_DARK,
    spaceBefore=0,
    spaceAfter=3,
)
body_style = ParagraphStyle(
    "Body",
    fontName="Helvetica",
    fontSize=10,
    textColor=TEXT_MID,
    leading=15,
    spaceAfter=4,
)
impl_label_style = ParagraphStyle(
    "ImplLabel",
    fontName="Helvetica-Bold",
    fontSize=9,
    textColor=GREEN_TEXT,
    spaceBefore=4,
    spaceAfter=2,
)
impl_body_style = ParagraphStyle(
    "ImplBody",
    fontName="Helvetica-Oblique",
    fontSize=9,
    textColor=TEXT_MID,
    leading=13,
    spaceAfter=2,
    leftIndent=12,
)
footer_style = ParagraphStyle(
    "Footer",
    fontName="Helvetica",
    fontSize=7.5,
    textColor=MUTED,
    alignment=TA_CENTER,
)

# ── Best practices data ───────────────────────────────────────────────────────
BEST_PRACTICES = [
    {
        "num": "BP-01",
        "phase": "DEFINE",
        "title": "End-to-End Requirements Traceability",
        "body": (
            "Requirements authored in IBM DOORS must maintain verifiable links to the "
            "software components that implement them, the Git commits that deliver the "
            "implementation, and the test cases that verify it. In practice, these links "
            "are frequently maintained manually, incompletely, or not at all — resulting "
            "in traceability gaps that surface as ASPICE audit findings and create risk "
            "when requirements change late in the program."
        ),
        "impl": (
            "Addressed by the RTM Bridge (roadmap): automated linkage between DOORS "
            "requirement IDs, GitHub commit messages, and VectorCAST test results. "
            "Requirements Agent flags missing allocation and verification method fields "
            "at authoring time, before gaps enter the baseline."
        ),
    },
    {
        "num": "BP-02",
        "phase": "DEFINE",
        "title": "Testable and Unambiguous Requirement Language",
        "body": (
            "Requirements containing vague qualifiers — 'appropriate,' 'sufficient,' "
            "'robust,' 'fast,' or open TBD/TBI placeholders — are untestable and "
            "non-verifiable. They pass DOORS entry gates, get baselined, and generate "
            "disputes at integration and validation. This is one of the most common "
            "root causes of late-program rework."
        ),
        "impl": (
            "Requirements Agent performs automated ASPICE SWE.1 quality analysis on "
            "DOORS CSV exports: ambiguity term detection, testability assessment, TBD "
            "flagging (auto-escalated to error severity), and suggested rewrites with "
            "measurable acceptance criteria."
        ),
    },
    {
        "num": "BP-03",
        "phase": "CONFIGURE",
        "title": "Reviewable ARXML Configuration Changes",
        "body": (
            "ARXML files modified through BSW configuration tools produce verbose XML "
            "diffs that are not meaningfully reviewable in standard Git pull request "
            "workflows. Configuration changes — signal width adjustments, OS task "
            "priority changes, diagnostic session modifications — frequently bypass peer "
            "review because reviewers cannot interpret raw ARXML diffs. Integration "
            "issues that would be caught in a code review instead surface at build or "
            "system test."
        ),
        "impl": (
            "arxml_diff.py generates SHORT-NAME keyed, human-readable structured diffs "
            "per AR-PACKAGE, filterable by module (COM, OS, DCM). Output feeds directly "
            "into Config Agent for automated cross-module risk assessment before "
            "baseline entry."
        ),
    },
    {
        "num": "BP-04",
        "phase": "CONFIGURE",
        "title": "Cross-Module Integration Risk Assessment",
        "body": (
            "AUTOSAR BSW modules are tightly coupled: a COM signal width change affects "
            "PduR buffer sizing; an OS task priority change affects COM callback timing; "
            "a DCM session change can conflict with ComM channel state management. These "
            "dependencies are well understood by experienced integration engineers but "
            "are rarely captured in a form that can be systematically checked at "
            "configuration time."
        ),
        "impl": (
            "Config Agent (LangGraph, 3-step): parses ARXML diff, assesses cross-module "
            "risk against known AUTOSAR dependency patterns, generates per-change "
            "findings with severity and traceability refs. Tested end-to-end: 7-change "
            "COM stack diff processed in under 5 seconds with confidence score 0.8."
        ),
    },
    {
        "num": "BP-05",
        "phase": "BUILD",
        "title": "MISRA Static Analysis as a Hard Gate, Not a Checkbox",
        "body": (
            "PC-lint and Polyspace results are routinely suppressed in bulk under "
            "schedule pressure, with generic justifications that do not constitute "
            "valid MISRA deviation rationale. The discipline of triaging every finding, "
            "documenting a legitimate rationale for each waiver, and tracking suppressed "
            "findings across releases is rarely maintained. This creates both safety "
            "risk and compliance exposure."
        ),
        "impl": (
            "Build Agent (roadmap): automated MISRA finding triage — categorizes "
            "violations by rule, suggests rationale templates for common patterns, "
            "flags safety-classified rules that require engineer sign-off. Guardrail: "
            "agents may triage findings but never suppress or dismiss them."
        ),
    },
    {
        "num": "BP-06",
        "phase": "BUILD",
        "title": "Reproducible Build Environments",
        "body": (
            "ECU software built on individual developer workstations with locally "
            "installed tool versions produces binaries that cannot be reliably "
            "reproduced by another engineer or a CI server. Compiler version "
            "differences, library path variations, and environment-specific flags "
            "introduce subtle behavioral differences that are difficult to diagnose "
            "and undermine release confidence."
        ),
        "impl": (
            "Docker Compose stack defines the complete build environment — compiler "
            "toolchain, agent services, Ollama inference — as code. Every build "
            "executes in an identical, version-controlled container regardless of "
            "host machine."
        ),
    },
    {
        "num": "BP-07",
        "phase": "CI/CT/CD",
        "title": "Continuously Green CI Pipeline",
        "body": (
            "CI pipelines are frequently allowed to remain in a failing state for "
            "extended periods because fixing the build is not prioritized against "
            "feature delivery. A persistently red pipeline provides no integration "
            "safety net and erodes team confidence in the CI system, eventually "
            "leading to the pipeline being ignored entirely."
        ),
        "impl": (
            "GitHub Actions CI baseline enforces lint (ruff), unit tests, n8n workflow "
            "JSON validation, and Docker Compose config validation on every push. "
            "Jenkinsfile defines equivalent gates for the automotive CI environment."
        ),
    },
    {
        "num": "BP-08",
        "phase": "CI/CT/CD",
        "title": "Automated Test Coverage Tied to Requirements",
        "body": (
            "Test suites grow organically without systematic coverage of the requirement "
            "set. Tests that were written for one software version remain in the suite "
            "without being updated when requirements change. Coverage gaps are "
            "discovered at system test or, worse, in the field. MC/DC coverage metrics "
            "are reported but not connected to specific requirements."
        ),
        "impl": (
            "Test Agent (roadmap): generates testable acceptance criteria from "
            "Requirements Agent output, traces test cases to source requirements, "
            "flags requirements with no associated test. VectorCAST/LDRA integration "
            "for MC/DC coverage reporting."
        ),
    },
    {
        "num": "BP-09",
        "phase": "CROSS-CUTTING",
        "title": "Enforced Human Approval Gates for AI-Generated Artifacts",
        "body": (
            "Teams adopting AI tooling frequently trust AI-generated outputs — test "
            "cases, code suggestions, configuration recommendations — without a "
            "structured review step, treating them as equivalent to engineer-authored "
            "content. In a safety-critical context, this bypasses the review and "
            "approval processes required by ISO 26262 and ASPICE, and creates "
            "unqualified tool usage risk."
        ),
        "impl": (
            "ADR-001 defines the agent isolation principle: no agent writes directly "
            "to any controlled artifact. All agent output carries confidence_score and "
            "human_review_required flags. n8n enforces the gate programmatically — "
            "confidence below 0.75 or error severity creates a Jira ticket before "
            "any downstream action is permitted."
        ),
    },
    {
        "num": "BP-10",
        "phase": "CROSS-CUTTING",
        "title": "AI Tool Limitation Documentation for Safety Assessments",
        "body": (
            "ISO 26262 requires tool qualification for tools used in safety-relevant "
            "development activities. Most programs adopting AI tooling have not "
            "formally documented the tool's known failure modes, confidence boundaries, "
            "or output verification approach in a form that satisfies a tool "
            "qualification argument. This is an emerging gap across the industry as "
            "AI adoption accelerates faster than safety standards evolve."
        ),
        "impl": (
            "Confidence scoring, severity classification, and the human approval gate "
            "constitute the foundation of a tool qualification argument. ADR-001 "
            "documents the design rationale. Safety guardrails module enforces "
            "output validation at runtime. Full tool qualification assessment is "
            "identified as a roadmap item requiring collaboration with the "
            "program safety team."
        ),
    },
]


def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.85 * inch,
    )

    story = []
    W = letter[0] - 1.7 * inch   # usable width

    # ── Header bar ────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph(
            "<font color='#FFFFFF'><b>AI-Assisted Automotive Software Engineering Workflow</b></font>",
            ParagraphStyle("hdr", fontName="Helvetica-Bold", fontSize=11,
                           textColor=colors.white, leading=14)
        )
    ]]
    header_table = Table(header_data, colWidths=[W])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [4]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # ── Title block ───────────────────────────────────────────────────────────
    story.append(Paragraph(
        "ASE Workflow Best Practices",
        title_style
    ))
    story.append(Paragraph(
        "Common gaps addressed by the AI-assisted pipeline design",
        subtitle_style
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Mathew S. Crawford  \u00b7  mathew.s.crawford@gmail.com  \u00b7  "
        "github.com/MathewScottCrawford/etas-ford-ai-workflow  \u00b7  v1.0  \u00b7  March 2026",
        meta_style
    ))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width=W, thickness=2, color=ACCENT, spaceAfter=10))

    # ── Purpose ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Purpose", section_header_style))
    story.append(Paragraph(
        "This document identifies ten best practices that are commonly shortfalled in "
        "automotive ECU software development programs. For each practice, the gap is "
        "described in concrete terms drawn from integration experience across AUTOSAR "
        "Classic environments, and the corresponding design element in this workflow "
        "architecture that addresses it is identified. The intent is to demonstrate "
        "that the architectural decisions in this project are grounded in real program "
        "experience, not theoretical ideals.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # ── Phase tag helper ──────────────────────────────────────────────────────
    phase_colors = {
        "DEFINE":      (colors.HexColor("#EEEDFE"), colors.HexColor("#534AB7")),
        "CONFIGURE":   (colors.HexColor("#FAEEDA"), colors.HexColor("#854F0B")),
        "BUILD":       (colors.HexColor("#E6F1FB"), colors.HexColor("#185FA5")),
        "CI/CT/CD":    (colors.HexColor("#FAECE7"), colors.HexColor("#993C1D")),
        "CROSS-CUTTING":(colors.HexColor("#F1EFE8"), colors.HexColor("#5F5E5A")),
    }

    # ── Best practices ────────────────────────────────────────────────────────
    story.append(Paragraph("Best Practices", section_header_style))
    story.append(HRFlowable(width=W, thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))

    for bp in BEST_PRACTICES:
        bg_col, fg_col = phase_colors.get(bp["phase"], (LIGHT_GRAY, TEXT_MID))

        # Number + title row with phase tag
        num_para = Paragraph(
            f"<font color='#4A6FA5'><b>{bp['num']}</b></font>",
            ParagraphStyle("n", fontName="Helvetica-Bold", fontSize=11,
                           textColor=MID_BLUE, leading=14)
        )
        title_para = Paragraph(
            f"<b>{bp['title']}</b>",
            ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=11,
                           textColor=TEXT_DARK, leading=14)
        )
        phase_para = Paragraph(
            bp["phase"],
            ParagraphStyle("p", fontName="Helvetica-Bold", fontSize=8,
                           textColor=fg_col, alignment=TA_CENTER, leading=11)
        )

        header_row = Table(
            [[num_para, title_para, phase_para]],
            colWidths=[0.55 * inch, W - 1.45 * inch, 0.9 * inch]
        )
        header_row.setStyle(TableStyle([
            ("BACKGROUND",   (2, 0), (2, 0), bg_col),
            ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
            ("LEFTPADDING",  (2, 0), (2, 0), 4),
            ("RIGHTPADDING", (2, 0), (2, 0), 4),
            ("TOPPADDING",   (2, 0), (2, 0), 4),
            ("BOTTOMPADDING",(2, 0), (2, 0), 4),
            ("ROUNDEDCORNERS", [3]),
        ]))

        gap_para   = Paragraph(bp["body"], body_style)
        impl_label = Paragraph("Implementation in this architecture:", impl_label_style)
        impl_para  = Paragraph(bp["impl"], impl_body_style)

        # Wrap in keep-together block with subtle background
        block_content = [header_row, Spacer(1, 4), gap_para, impl_label, impl_para]
        block_table = Table(
            [[block_content]],
            colWidths=[W]
        )
        block_table.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), OFF_WHITE),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 10),
            ("TOPPADDING",    (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.5, LIGHT_GRAY),
        ]))

        story.append(KeepTogether([block_table, Spacer(1, 6)]))

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width=W, thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
    story.append(Paragraph(
        "This document is a living artifact. Best practices marked as roadmap items "
        "will be updated as the corresponding pipeline components are implemented and "
        "validated. See docs/adr/ for related architectural decision records.",
        ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8.5,
                       textColor=MUTED, leading=13)
    ))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Mathew S. Crawford  \u00b7  mathew.s.crawford@gmail.com  \u00b7  734-765-4143  \u00b7  "
        "linkedin.com/in/mathewscrawford  \u00b7  MIT License",
        footer_style
    ))

    doc.build(story)
    print(f"PDF written: {OUTPUT}")


if __name__ == "__main__":
    build()
