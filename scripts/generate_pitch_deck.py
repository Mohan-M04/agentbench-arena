import os
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    REPO_ROOT = Path(__file__).resolve().parent.parent
    SCREENSHOTS_DIR = REPO_ROOT / "docs" / "screenshots"

    # Color Palette: Dark Navy Tech Theme
    BG_COLOR = RGBColor(15, 23, 42)       # Slate 900
    CARD_BG = RGBColor(30, 41, 59)        # Slate 800
    ACCENT_CYAN = RGBColor(6, 182, 212)   # Cyan 500
    ACCENT_PURPLE = RGBColor(168, 85, 247)# Purple 500
    TEXT_WHITE = RGBColor(248, 250, 252)  # Slate 50
    TEXT_MUTED = RGBColor(148, 163, 184)  # Slate 400
    ACCENT_GREEN = RGBColor(34, 197, 94)  # Emerald 500
    ACCENT_RED = RGBColor(239, 68, 68)    # Red 500

    def set_slide_bg(slide):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        shape.fill.solid()
        shape.fill.fore_color.rgb = BG_COLOR
        shape.line.color.rgb = BG_COLOR
        return shape

    def add_header(slide, title_text, category_text="GEEK ROOM AI GLOBAL HACKATHON 2026"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(11)
        p_c.font.bold = True
        p_c.font.color.rgb = ACCENT_CYAN

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.5), Inches(0.7))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(24)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1)

    card1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.1), Inches(6.8), Inches(5.3))
    card1.fill.solid()
    card1.fill.fore_color.rgb = CARD_BG
    card1.line.color.rgb = ACCENT_CYAN
    card1.line.width = Pt(1.5)

    tb = s1.shapes.add_textbox(Inches(1.1), Inches(1.3), Inches(6.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "GEEK ROOM AI GLOBAL HACKATHON 2026"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN
    p.space_after = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "AgentBench Arena"
    p2.font.size = Pt(36)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.space_after = Pt(8)

    p3 = tf.add_paragraph()
    p3.text = "“Deterministic Chaos Engineering & Side-by-Side Reliability Observability for AI Agents.”"
    p3.font.size = Pt(15)
    p3.font.italic = True
    p3.font.color.rgb = ACCENT_PURPLE
    p3.space_after = Pt(16)

    p4 = tf.add_paragraph()
    p4.text = "• Primary Track: Build a Benchmarking Platform for AI Agents, Not Just Models\n• Ecosystem: Integrated with Bifrost (Maxim AI) & Tavily API\n• Developer: Mohan M (Solo Submission)\n• GitHub: github.com/Mohan-M04/agentbench-arena"
    p4.font.size = Pt(12)
    p4.font.color.rgb = TEXT_MUTED

    # Embed Real Dashboard Screenshot
    dash_img = SCREENSHOTS_DIR / "dashboard.png"
    if dash_img.exists():
        s1.shapes.add_picture(str(dash_img), Inches(7.8), Inches(1.1), Inches(4.7), Inches(5.3))

    # -------------------------------------------------------------
    # SLIDE 2: THE PROBLEM
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2)
    add_header(s2, "The Real-World Gap: Why Model Accuracy Does Not Guarantee Agent Reliability")

    boxes_data = [
        ("Static Benchmarks Are Insufficient", "MMLU, HumanEval, and GSM8K test models in static isolation. They measure conversational recall, not autonomous agent execution loops in production environments."),
        ("Production Failure Modes", "In the real world, autonomous agents crash from tool HTTP 500s, rate-limit throttles (HTTP 429), and malformed tool JSON. Existing benchmarks rarely measure runtime resilience, recovery, cost, and failure behavior together under identical stress."),
        ("Runaway Retry Loops & Cost Escalation", "When unhedged agents hit transient API outages, they enter unhandled recursive loops, exhausting token budgets and fabricating hallucinated data without resolving the user's task.")
    ]
    for idx, (b_title, b_desc) in enumerate(boxes_data):
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 3.9), Inches(1.8), Inches(3.7), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_CYAN if idx == 0 else ACCENT_PURPLE
        card.line.width = Pt(1)

        tbox = s2.shapes.add_textbox(Inches(1.0 + idx * 3.9), Inches(2.1), Inches(3.3), Inches(4.2))
        tf = tbox.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"0{idx+1}. {b_title}"
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.space_after = Pt(14)
        p2 = tf.add_paragraph()
        p2.text = b_desc
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 3: THE SOLUTION
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3)
    add_header(s3, "The Solution: AgentBench Arena Reliability Lab")

    # Flow Banner
    flow_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.65), Inches(11.7), Inches(0.65))
    flow_card.fill.solid()
    flow_card.fill.fore_color.rgb = CARD_BG
    flow_card.line.color.rgb = ACCENT_CYAN
    flow_tb = s3.shapes.add_textbox(Inches(0.9), Inches(1.7), Inches(11.5), Inches(0.5))
    flow_p = flow_tb.text_frame.paragraphs[0]
    flow_p.text = "Task ➔ Agent Adapter ➔ Tool Sandbox ➔ Chaos Injector ➔ Bifrost / Tavily ➔ Trace ➔ ARS"
    flow_p.font.size = Pt(13)
    flow_p.font.bold = True
    flow_p.font.color.rgb = ACCENT_CYAN

    s3_cards = [
        ("Controlled Fault Injection", "Applies programmable fault injection (HTTP 500s, transient errors, malformed JSON, and outages) with identical seeded schedules across all agents for 100% fair evaluation."),
        ("Side-by-Side Agent Duel", "Races two agent architectures on identical tasks under identical stress in real time to observe divergence in error handling and tool reasoning."),
        ("Execution Autopsy & Traces", "Turn-by-turn trace logs pinpoint the exact failing step, HTTP code, token spike, and provide actionable engineering root-cause diagnoses."),
        ("Counterfactual Replay Engine", "Re-run failed scenarios with one controlled intervention (e.g. Bifrost Gateway failover) to measure its causal impact on recovery, cost, and latency.")
    ]
    for idx, (c_title, c_desc) in enumerate(s3_cards):
        row = idx // 2
        col = idx % 2
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + col * 5.9), Inches(2.5 + row * 2.3), Inches(5.6), Inches(2.1))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_CYAN if col == 0 else ACCENT_PURPLE
        card.line.width = Pt(1)

        tbox = s3.shapes.add_textbox(Inches(1.0 + col * 5.9), Inches(2.6 + row * 2.3), Inches(5.2), Inches(1.8))
        tf = tbox.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = c_title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.space_after = Pt(6)
        p2 = tf.add_paragraph()
        p2.text = c_desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE & PARTNERS
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4)
    add_header(s4, "System Architecture & Partner Stack")

    arch_cards = [
        ("⚡ Bifrost Gateway (Maxim AI)", "Unified OpenAI-compatible proxy (localhost:8080) managing model routing, token/cost accounting, and multi-provider failover (gpt-4o-mini -> claude-3-haiku -> local).\n• Emulated deterministically in Simulation Mode for zero-key runs\n• Executed live in Live Bifrost Mode"),
        ("🔍 Tavily Search & Extract API", "Live web search and real-time knowledge retrieval validating factual citation answers beyond static model cutoffs.\n• Provides fresh real-world grounding for Tasks 04 & 05\n• Deterministic mock corpora used in Simulation Mode for zero-cost reproduction"),
        ("🛡️ Tool Sandbox & Chaos Layer", "Isolated execution layer with schema verification for SQLite, Calculator, Weather, and Flights.\n• Intercepts calls to inject transient errors, persistent 500s, and 429 throttles\n• Strictly sandboxed with zero unauthorized host egress"),
        ("🤖 Multi-Architecture Harness", "Direct adapters for LangGraph (state checkpointing), ReAct with Retry/Fallback, Custom JSON State Machines, and Naive baselines, plus external webhook support (:9000).")
    ]
    for idx, (a_title, a_desc) in enumerate(arch_cards):
        row = idx // 2
        col = idx % 2
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + col * 5.9), Inches(1.8 + row * 2.6), Inches(5.6), Inches(2.3))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_CYAN if col == 0 else ACCENT_PURPLE
        card.line.width = Pt(1)

        tbox = s4.shapes.add_textbox(Inches(1.0 + col * 5.9), Inches(1.95 + row * 2.6), Inches(5.2), Inches(2.0))
        tf = tbox.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = a_title
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.space_after = Pt(8)
        p2 = tf.add_paragraph()
        p2.text = a_desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 5: ARS FORMULA
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5)
    add_header(s5, "The Metric: Agent Reliability Score (ARS)")

    f_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.1))
    f_card.fill.solid()
    f_card.fill.fore_color.rgb = CARD_BG
    f_card.line.color.rgb = ACCENT_GREEN
    f_card.line.width = Pt(1.5)

    ftb = s5.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(1.7))
    ftf = ftb.text_frame
    ftf.word_wrap = True
    p_f = ftf.paragraphs[0]
    p_f.text = "Raw ARS = (Success Rate × 0.35) + (Recovery Rate × 0.25) + (Cost Efficiency × 0.15) + (Speed Efficiency × 0.15) + (Consistency × 0.10)\nSafety-Adjusted ARS = max(0, Raw ARS − Total Safety Penalties)"
    p_f.font.size = Pt(15)
    p_f.font.bold = True
    p_f.font.color.rgb = ACCENT_GREEN
    p_f.space_after = Pt(8)

    p_f2 = ftf.add_paragraph()
    p_f2.text = "Mathematical Rigor: Evaluates task success, recovery out of faults faced, cost ceiling ($0.0125 budget), 10s latency ceiling, and run-to-run consistency. Unsafe shell actions, fabricated numbers, or silent drops trigger immediate -25 to -40 pt safety deductions."
    p_f2.font.size = Pt(11)
    p_f2.font.color.rgb = TEXT_WHITE

    tiers = [
        (">= 85.0: High Reliability", "High reliability in the current simulation suite; resilient architecture with state checkpointing or retry policies that reliably passes fault injection."),
        ("70.0 - 84.9: Reliable w/ Guardrails", "Satisfies CI quality gate (ARS >= 75.0); e.g., LangGraph @ 84.12, Custom JSON @ 78.90. Requires supervisory guardrails on cascading outages."),
        ("< 50.0: Critical Failure Risk", "Unhedged loop baseline (Naive ReAct @ 36.45). Lacks backoff/fallback logic; repeated faults cause severe degradation or task abortion.")
    ]
    for idx, (tr_n, tr_d) in enumerate(tiers):
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 3.9), Inches(4.2), Inches(3.7), Inches(2.5))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_CYAN if idx == 0 else (ACCENT_PURPLE if idx == 1 else ACCENT_RED)
        card.line.width = Pt(1)

        tbox = s5.shapes.add_textbox(Inches(1.0 + idx * 3.9), Inches(4.35), Inches(3.3), Inches(2.2))
        tf = tbox.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = tr_n
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.space_after = Pt(6)
        p2 = tf.add_paragraph()
        p2.text = tr_d
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 6: BENCHMARK RESULTS
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6)
    add_header(s6, "Benchmark Results: Four Architectures Under Identical Seeded Chaos")

    rows, cols = 5, 7
    left, top, width, height = Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.8)
    table_shape = s6.shapes.add_table(rows, cols, left, top, width, height)
    tbl = table_shape.table

    headers = ["Agent Variant", "Implementation Paradigm", "Success Rate (95% CI)", "Fault Recovery", "Avg Cost", "Avg Latency", "ARS Rating"]
    for i, h in enumerate(headers):
        cell = tbl.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        for p in cell.text_frame.paragraphs:
            p.font.bold = True
            p.font.size = Pt(11)
            p.font.color.rgb = ACCENT_CYAN

    data = [
        ["ReAct w/ Retry & Fallback", "Backoff + Fallback", "91.7% [85.3%, 95.4%]", "90.0% (27/30)", "$0.000188", "0.23s", "89.65"],
        ["LangGraph Agent", "State Checkpoints", "83.3% [75.7%, 88.9%]", "80.0% (24/30)", "$0.000224", "0.37s", "84.12"],
        ["Custom JSON Agent", "Schema Policies", "77.5% [69.2%, 84.1%]", "70.0% (21/30)", "$0.000156", "0.50s", "78.90"],
        ["Naive ReAct Loop", "Baseline Unhedged", "40.0% [31.7%, 48.9%]", "6.7% (2/30)", "$0.000129", "0.41s", "36.45"],
    ]
    for row_idx, row_data in enumerate(data):
        for col_idx, val in enumerate(row_data):
            cell = tbl.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = CARD_BG
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_WHITE if row_idx < 3 else ACCENT_RED

    note_box = s6.shapes.add_textbox(Inches(0.8), Inches(4.8), Inches(11.7), Inches(2.2))
    tf_n = note_box.text_frame
    tf_n.word_wrap = True
    p_n = tf_n.paragraphs[0]
    p_n.text = "Key Finding: Retry, backoff, and fallback logic improve success by 51.7 percentage points and recovery by 83.3 percentage points over the unhedged baseline."
    p_n.font.size = Pt(13)
    p_n.font.bold = True
    p_n.font.color.rgb = ACCENT_GREEN
    p_n.space_after = Pt(4)

    p_n2 = tf_n.add_paragraph()
    p_n2.text = "• Why It Matters: Same task. Same seed. Same failures. Different agent architecture. Radically different reliability.\n• Statistical Rigor: 120 evaluations per agent | 12 tasks × 10 seeded runs | Simulation Mode with 95% Wilson score binomial confidence intervals.\n• Mode Caveat: Results generated in deterministic Simulation Mode; live Bifrost results are separately reproducible with a running gateway."
    p_n2.font.size = Pt(11)
    p_n2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 7: COUNTERFACTUAL REPLAY
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7)
    add_header(s7, "Counterfactual Replay: Re-run Failed Scenarios with One Controlled Intervention")

    # Card 1: Original Run
    c_orig = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8))
    c_orig.fill.solid()
    c_orig.fill.fore_color.rgb = CARD_BG
    c_orig.line.color.rgb = ACCENT_RED
    tb_o = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(3.2), Inches(4.4))
    tf_o = tb_o.text_frame
    tf_o.word_wrap = True
    po1 = tf_o.paragraphs[0]
    po1.text = "Original Run — HTTP 500 Outage"
    po1.font.size = Pt(14)
    po1.font.bold = True
    po1.font.color.rgb = ACCENT_RED
    po1.space_after = Pt(10)
    po2 = tf_o.add_paragraph()
    po2.text = "• Agent: Naive ReAct Loop\n• Result: FAILED\n• ARS Score: 20.0 pts\n• Steps Taken: 6 steps\n• Cost: $0.000410\n• Root Cause: Unhandled downstream tool outage; zero retry or fallback logic."
    po2.font.size = Pt(12)
    po2.font.color.rgb = TEXT_MUTED

    # Card 2: Counterfactual Replay
    c_rep = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.7), Inches(1.8), Inches(3.6), Inches(4.8))
    c_rep.fill.solid()
    c_rep.fill.fore_color.rgb = CARD_BG
    c_rep.line.color.rgb = ACCENT_GREEN
    tb_r = s7.shapes.add_textbox(Inches(4.9), Inches(2.0), Inches(3.2), Inches(4.4))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    pr1 = tf_r.paragraphs[0]
    pr1.text = "Counterfactual Replay — Patched"
    pr1.font.size = Pt(14)
    pr1.font.bold = True
    pr1.font.color.rgb = ACCENT_GREEN
    pr1.space_after = Pt(10)
    pr2 = tf_r.add_paragraph()
    pr2.text = "• Intervention: Exponential backoff retry + Bifrost multi-provider failover\n• Result: PASSED (RECOVERED)\n• ARS Score: 92.0 pts\n• Steps Taken: 4 steps (saved 2)\n• Cost: $0.000210\n• Telemetry: Secondary route synthesized answer seamlessly."
    pr2.font.size = Pt(12)
    pr2.font.color.rgb = TEXT_MUTED

    # Card 3: Measured Impact & Safety Callout
    c_imp = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.8))
    c_imp.fill.solid()
    c_imp.fill.fore_color.rgb = CARD_BG
    c_imp.line.color.rgb = ACCENT_CYAN
    tb_i = s7.shapes.add_textbox(Inches(8.8), Inches(2.0), Inches(3.5), Inches(4.4))
    tf_i = tb_i.text_frame
    tf_i.word_wrap = True
    pi1 = tf_i.paragraphs[0]
    pi1.text = "Measured Impact & Safety Rule"
    pi1.font.size = Pt(14)
    pi1.font.bold = True
    pi1.font.color.rgb = ACCENT_CYAN
    pi1.space_after = Pt(10)
    pi2 = tf_i.add_paragraph()
    pi2.text = "Quantified Improvement:\n• +100% Task Success\n• -48.7% Cost Reduction\n• +72.0 ARS Improvement\n\n🛡️ Safety Callout:\nRecovery means completing the task, using a fallback, or safely reporting that the task cannot be completed. Fabricating missing data is a safety breach (-25 to -40 pts)—not recovery."
    pi2.font.size = Pt(11)
    pi2.font.color.rgb = TEXT_WHITE

    # -------------------------------------------------------------
    # SLIDE 8: CI/CD QUALITY GATE
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s8)
    add_header(s8, "Production CI/CD Quality Gate: Automated Regression Prevention")

    ci_cards = [
        ("Automated PR Evaluation", "Runs on every pull request via GitHub Actions (agent-reliability-gate.yml). Evaluates agent changes against seeded benchmark test schedules in automated CI containers."),
        ("Strict Quality Gate Criteria", "Enforces production thresholds before code merges:\n• Minimum ARS Rating >= 75.0\n• Minimum Fault Recovery SLA >= 70.0%\n• Cost Ceiling: <= $0.0005 per task\n• 15/15 Unit Verification Suite Passing"),
        ("Pull Request Blocking", "If an unhedged prompt, model swap, or tool tweak causes ARS to drop below 75.0, the pipeline fails the CI check and blocks the pull request automatically.")
    ]
    for idx, (ci_t, ci_d) in enumerate(ci_cards):
        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 3.9), Inches(1.8), Inches(3.7), Inches(4.8))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_GREEN if idx == 1 else ACCENT_CYAN
        card.line.width = Pt(1)

        tbox = s8.shapes.add_textbox(Inches(1.0 + idx * 3.9), Inches(2.1), Inches(3.3), Inches(4.2))
        tf = tbox.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = ci_t
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.space_after = Pt(14)
        p2 = tf.add_paragraph()
        p2.text = ci_d
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 9: REAL-WORLD IMPACT & ROADMAP
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s9)
    add_header(s9, "Real-World Impact & Roadmap: From Prototype to Reliability Platform")

    s9_cards = [
        ("Early Regression Detection", "Helps enterprise teams detect reliability, cost, and safety regressions before deployment, preventing customer-facing outages and runaway LLM billing."),
        ("Transparent Cost Attribution", "Provides empirical cost-per-task and latency attribution across multiple LLM providers, validating architecture decisions with hard numbers."),
        ("Multi-Modal Chaos (Q1 2027)", "Extend chaos harness to multi-modal agent inputs: corrupted vision frames, truncated audio streams, and partitioned multi-agent communication networks (A2A)."),
        ("Automated Patch Synthesis (Q2 2027)", "Synthesizing resilient retry wrappers and fallback policies directly from counterfactual replay traces without manual engineering.")
    ]
    for idx, (c_t, c_d) in enumerate(s9_cards):
        row = idx // 2
        col = idx % 2
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + col * 5.9), Inches(1.8 + row * 2.6), Inches(5.6), Inches(2.3))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = ACCENT_CYAN if col == 0 else ACCENT_PURPLE
        card.line.width = Pt(1)

        tbox = s9.shapes.add_textbox(Inches(1.0 + col * 5.9), Inches(1.95 + row * 2.6), Inches(5.2), Inches(2.0))
        tf = tbox.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = c_t
        p1.font.size = Pt(15)
        p1.font.bold = True
        p1.font.color.rgb = TEXT_WHITE
        p1.space_after = Pt(8)
        p2 = tf.add_paragraph()
        p2.text = c_d
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 10: CONCLUSION & REPRODUCIBILITY
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s10)
    add_header(s10, "Designed for Production Reliability Workflows")

    card10 = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    card10.fill.solid()
    card10.fill.fore_color.rgb = CARD_BG
    card10.line.color.rgb = ACCENT_GREEN
    card10.line.width = Pt(1.5)

    tb10 = s10.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(11.1), Inches(4.4))
    tf10 = tb10.text_frame
    tf10.word_wrap = True

    p_10_1 = tf10.paragraphs[0]
    p_10_1.text = "Deterministic Local CLI Reproduction (Seed 42):"
    p_10_1.font.size = Pt(16)
    p_10_1.font.bold = True
    p_10_1.font.color.rgb = ACCENT_GREEN
    p_10_1.space_after = Pt(6)

    p_cmd = tf10.add_paragraph()
    p_cmd.text = "python main.py --suite chaos_suite --runs 10 --seed 42 --export all"
    p_cmd.font.size = Pt(15)
    p_cmd.font.bold = True
    p_cmd.font.color.rgb = ACCENT_CYAN
    p_cmd.space_after = Pt(16)

    p_10_2 = tf10.add_paragraph()
    p_10_2.text = "• Zero-Key Transparency: Simulation Mode requires no API keys and opens no external network sockets. Live Bifrost Mode requires a locally running Bifrost gateway (localhost:8080) and provider credentials.\n• Open Telemetry Evidence: 40 raw run files, 4 audit reports, and 2 CSV matrices committed to git repository.\n• Title Partner: Maxim AI Bifrost (AI Gateway) | Track Partner: Tavily (Real-Time Search & Extract API)\n• GitHub Repository: github.com/Mohan-M04/agentbench-arena (MIT License)"
    p_10_2.font.size = Pt(12)
    p_10_2.font.color.rgb = TEXT_WHITE
    p_10_2.space_after = Pt(14)

    p_10_3 = tf10.add_paragraph()
    p_10_3.text = "Thank you! Ready for judge evaluation and live dual observatory demonstrations."
    p_10_3.font.size = Pt(13)
    p_10_3.font.italic = True
    p_10_3.font.color.rgb = ACCENT_PURPLE

    output_path = REPO_ROOT / "AgentBench_Arena_Hackathon_Pitch_Deck.pptx"
    prs.save(str(output_path))
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_deck()
