"""Generate the AI Agent Program plan as an Excel workbook (AWS, 5 months)."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ---------- styles ----------
NAVY   = "232F3E"
ORANGE = "FF9900"
WHITE  = "FFFFFF"
LIGHT  = "F2F4F7"
GREY   = "6B7480"
BAND   = "EAF2F8"

PHASE_HEX = ["2E86C1", "28B463", "8E44AD", "E67E22", "16A085", "C0392B"]

thin = Side(style="thin", color="D5DBE0")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def fill(hexv):
    return PatternFill("solid", fgColor=hexv)

def style_cell(c, *, font_color="1B2430", bold=False, size=11, bg=None,
               align="left", wrap=False, valign="center", bordered=True):
    c.font = Font(color=font_color, bold=bold, size=size, name="Calibri")
    if bg:
        c.fill = fill(bg)
    c.alignment = Alignment(horizontal=align, vertical=valign, wrap_text=wrap)
    if bordered:
        c.border = border

# (name, objective, start, dur, owner, aws, deliverables)
# Compressed 5-month plan - phases run in parallel to hit the deadline.
PHASES = [
    ("Phase 1 - Administrative AI Agent (MVP)",
     "Automate meeting admin: transcripts to minutes, actions, owners, due dates",
     1, 1, "AI/ML Lead",
     "Amazon Transcribe; Amazon Bedrock; Amazon S3; DynamoDB; AWS Lambda",
     "Meeting minutes; Action register; Summary report; Dashboard updates"),
    ("Phase 2 - Action Tracking Agent",
     "Monitor, remind, escalate and report on open / overdue actions",
     2, 1, "Automation Eng",
     "Amazon EventBridge; Amazon SES / SNS; DynamoDB; AWS Lambda",
     "Weekly action reports; Overdue alerts; Escalation notifications"),
    ("Phase 3 - Governance & Forum Agent",
     "Read SteerCo / CIO / Cyber / Risk / Audit outputs; detect themes & risks",
     2, 2, "Data Eng",
     "Amazon Bedrock; Bedrock Knowledge Bases; Amazon S3; AWS Lambda",
     "Governance dashboard; Executive reports; Risk insights"),
    ("Phase 4 - Reporting & Analytics Agent",
     "Consolidate reports, measure delivery, build CIO packs & trend analysis",
     3, 2, "BI Lead",
     "Amazon QuickSight; AWS Glue; Amazon Athena; Amazon S3",
     "QuickSight dashboards; Monthly reports; CIO packs; Trend analysis"),
    ("Phase 5 - Enterprise Knowledge Agent",
     "Searchable organisational memory; natural-language Q&A over all outputs",
     4, 1, "AI/ML Lead",
     "Bedrock Knowledge Bases; OpenSearch Serverless; Amazon Bedrock (RAG)",
     "Searchable knowledge base; Q&A assistant; Decision history"),
    ("Phase 6 - Central Control Tower (Orchestration)",
     'Connect all agents through a central platform - the "spine"',
     4, 2, "Solutions Architect",
     "Amazon Bedrock Agents; AWS Step Functions; API Gateway; Amazon Cognito",
     "Unified orchestration platform; Agent registry; Central console"),
]
N_MONTHS = 5

wb = Workbook()

# =====================================================================
# SHEET 1 - Roadmap (Gantt)
# =====================================================================
ws = wb.active
ws.title = "Roadmap"
ws.sheet_view.showGridLines = False

# Title banner
ws.merge_cells("A1:Q1")
t = ws["A1"]
t.value = "Enterprise AI Agent Programme - Delivery Roadmap (AWS, 5 Months)"
style_cell(t, font_color=WHITE, bold=True, size=15, bg=NAVY, align="left", bordered=False)
ws.row_dimensions[1].height = 30

ws.merge_cells("A2:Q2")
st = ws["A2"]
st.value = "6 Phases - MVP to Central Control Tower"
style_cell(st, font_color=ORANGE, bold=True, size=11, bg=NAVY, align="left", bordered=False)
ws.row_dimensions[2].height = 20

# Header row (row 4)
hdr_row = 4
headers = ["Phase", "Start", "End"] + [f"M{i}" for i in range(1, N_MONTHS + 1)]
for j, h in enumerate(headers, start=1):
    c = ws.cell(row=hdr_row, column=j, value=h)
    align = "left" if j == 1 else "center"
    style_cell(c, font_color=WHITE, bold=True, size=10, bg=ORANGE, align=align)
ws.row_dimensions[hdr_row].height = 20

# Phase rows
for i, (name, obj, start, dur, owner, aws, deliv) in enumerate(PHASES):
    r = hdr_row + 1 + i
    end = start + dur - 1
    cn = ws.cell(row=r, column=1, value=name)
    style_cell(cn, bold=True, size=10, align="left", wrap=True)
    cs = ws.cell(row=r, column=2, value=f"M{start}")
    style_cell(cs, align="center", size=10)
    ce = ws.cell(row=r, column=3, value=f"M{end}")
    style_cell(ce, align="center", size=10)
    for m in range(1, N_MONTHS + 1):
        col = 3 + m
        cell = ws.cell(row=r, column=col)
        if start <= m <= end:
            mid = (start + end) / 2
            label = ""
            if m == round(mid) or (dur == 1 and m == start):
                label = f"M{start}-M{end}" if dur > 1 else f"M{start}"
            cell.value = label
            style_cell(cell, font_color=WHITE, bold=True, size=8, bg=PHASE_HEX[i],
                       align="center")
        else:
            style_cell(cell, bg=LIGHT)
    ws.row_dimensions[r].height = 30

# Milestones row
ms_row = hdr_row + 1 + len(PHASES) + 1
ws.cell(row=ms_row, column=1, value="Key Milestones")
style_cell(ws.cell(row=ms_row, column=1), bold=True, size=10, bg=NAVY, font_color=WHITE)
ws.cell(row=ms_row, column=2)
ws.cell(row=ms_row, column=3)
style_cell(ws.cell(row=ms_row, column=2), bg=NAVY, bordered=True)
style_cell(ws.cell(row=ms_row, column=3), bg=NAVY, bordered=True)
milestones = {1: "MVP live", 3: "Gov insights", 4: "Knowledge Q&A", 5: "Control Tower"}
for m in range(1, N_MONTHS + 1):
    col = 3 + m
    cell = ws.cell(row=ms_row, column=col)
    if m in milestones:
        cell.value = milestones[m]
        style_cell(cell, font_color=NAVY, bold=True, size=8, bg=ORANGE, align="center", wrap=True)
    else:
        style_cell(cell, bg=NAVY, bordered=True)
ws.row_dimensions[ms_row].height = 26

# column widths
ws.column_dimensions["A"].width = 34
ws.column_dimensions["B"].width = 7
ws.column_dimensions["C"].width = 7
for m in range(1, N_MONTHS + 1):
    ws.column_dimensions[get_column_letter(3 + m)].width = 11

note_row = ms_row + 2
ws.cell(row=note_row, column=1,
        value="Cross-cutting from M1: Security & IAM, Cost governance, Data privacy/PII, CI/CD, Human-in-the-loop review.")
style_cell(ws.cell(row=note_row, column=1), font_color=GREY, size=9, bordered=False, align="left")

# =====================================================================
# SHEET 2 - Phase Plan (detail)
# =====================================================================
ws2 = wb.create_sheet("Phase Plan")
ws2.sheet_view.showGridLines = False
cols = ["Phase", "Timeline", "Duration", "Owner", "Objective", "Core AWS Services", "Key Deliverables"]
widths = [30, 12, 11, 18, 42, 40, 42]
for j, (h, w) in enumerate(zip(cols, widths), start=1):
    c = ws2.cell(row=1, column=j, value=h)
    style_cell(c, font_color=WHITE, bold=True, size=11, bg=NAVY, align="center", wrap=True)
    ws2.column_dimensions[get_column_letter(j)].width = w
ws2.row_dimensions[1].height = 26

for i, (name, obj, start, dur, owner, aws, deliv) in enumerate(PHASES):
    r = 2 + i
    end = start + dur - 1
    band = BAND if i % 2 == 0 else WHITE
    vals = [name, f"M{start} - M{end}", f"{dur} mo", owner, obj,
            aws.replace("; ", "\n"), deliv.replace("; ", "\n")]
    for j, v in enumerate(vals, start=1):
        c = ws2.cell(row=r, column=j, value=v)
        style_cell(c, size=10, bg=band, wrap=True, valign="top", align="left")
    # phase colour chip in col A via font
    ws2.cell(row=r, column=1).font = Font(bold=True, size=10, color=PHASE_HEX[i], name="Calibri")
    ws2.row_dimensions[r].height = 70

# =====================================================================
# SHEET 3 - Detailed Tasks
# =====================================================================
ws3 = wb.create_sheet("Detailed Tasks")
ws3.sheet_view.showGridLines = False
tcols = ["Phase", "Month(s)", "Workstream / Task", "AWS Service", "Output"]
twidths = [30, 12, 46, 30, 40]
for j, (h, w) in enumerate(zip(tcols, twidths), start=1):
    c = ws3.cell(row=1, column=j, value=h)
    style_cell(c, font_color=WHITE, bold=True, size=11, bg=ORANGE, align="center")
    ws3.column_dimensions[get_column_letter(j)].width = w
ws3.row_dimensions[1].height = 22

TASKS = [
    # Phase 1 - M1
    (0, "M1", "Set up AWS landing zone, IAM roles, S3 buckets for raw inputs", "S3, IAM, Organizations", "Secure ingest foundation"),
    (0, "M1", "Transcribe recordings to text; ingest Teams transcripts & notes", "Amazon Transcribe, S3", "Normalised transcript store"),
    (0, "M1", "Extract actions/owners/due dates; minutes, summaries, register", "Amazon Bedrock, DynamoDB", "MVP live (minutes + register)"),
    # Phase 2 - M2
    (1, "M2", "Scheduled scan of open/overdue actions; reminder + escalation logic", "EventBridge, Lambda", "Automated reminders"),
    (1, "M2", "Notification channels and closure-evidence capture", "Amazon SES / SNS, S3", "Alerts & status reports"),
    # Phase 3 - M2-M3
    (2, "M2-M3", "Ingest SteerCo/CIO/Cyber/Risk/Audit outputs into knowledge base", "Bedrock Knowledge Bases, S3", "Governance corpus"),
    (2, "M3", "Theme, risk & dependency detection; executive summaries", "Amazon Bedrock, Lambda", "Risk insights & exec reports"),
    # Phase 4 - M3-M4
    (3, "M3", "Build data lake / ETL for reporting; define KPIs & metrics", "AWS Glue, Athena, S3", "Curated reporting datasets"),
    (3, "M3-M4", "Dashboards, monthly reports, CIO packs, trend analysis", "Amazon QuickSight", "Executive reporting packs"),
    # Phase 5 - M4
    (4, "M4", "Index all outputs; build vector store for semantic search", "OpenSearch Serverless, S3", "Searchable index"),
    (4, "M4", "RAG-based Q&A assistant over organisational memory", "Bedrock Knowledge Bases (RAG)", "Natural-language Q&A"),
    # Phase 6 - M4-M5
    (5, "M4", "Design orchestration spine; agent registry & shared data contracts", "Step Functions, API Gateway", "Orchestration design"),
    (5, "M5", "Wire all agents together; central console & access control", "Bedrock Agents, Cognito", "Unified platform"),
    (5, "M5", "End-to-end testing, hardening, go-live & handover", "CloudWatch, Step Functions", "Production Control Tower"),
]
for i, (pidx, months, task, svc, out) in enumerate(TASKS):
    r = 2 + i
    band = BAND if pidx % 2 == 0 else WHITE
    row_vals = [PHASES[pidx][0].split(" - ")[0], months, task, svc, out]
    for j, v in enumerate(row_vals, start=1):
        c = ws3.cell(row=r, column=j, value=v)
        style_cell(c, size=10, bg=band, wrap=True, valign="center", align="left")
    ws3.cell(row=r, column=1).font = Font(bold=True, size=9, color=PHASE_HEX[pidx], name="Calibri")
    ws3.row_dimensions[r].height = 30

# freeze header rows
ws.freeze_panes = "A5"
ws2.freeze_panes = "A2"
ws3.freeze_panes = "A2"

import os
_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AI_Agent_Programme_Plan.xlsx")
wb.save(_OUT)
print("XLSX saved with sheets:", wb.sheetnames)
