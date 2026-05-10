# Run with: streamlit run app.py

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from pathlib import Path
from src.debate import run_debate

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Analyst",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 Multi-Agent Analyst")
st.caption("A Planner, Researcher, and Critic debate any topic to produce a structured analytical report")

# ── Agent styling ──────────────────────────────────────────────────────────
AGENT_CONFIG = {
    "Planner":    {"icon": "🔵", "color": "#1A56DB"},
    "Researcher": {"icon": "🟢", "color": "#057A55"},
    "Critic":     {"icon": "🔴", "color": "#C81E1E"},
    "System":     {"icon": "⚙️",  "color": "#6B7280"},
}


def render_event(event):
    """Render a single debate event as a styled message block."""
    cfg   = AGENT_CONFIG.get(event.agent, AGENT_CONFIG["System"])
    icon  = cfg["icon"]
    color = cfg["color"]
    label = f"{icon} **{event.agent}**"
    if event.round_num > 0:
        label += f" · Round {event.round_num}"
    label += f" · *{event.stage}*"

    st.markdown(
        f"""<div style="border-left: 3px solid {color};
                        padding: 10px 16px;
                        margin: 8px 0;
                        border-radius: 0 8px 8px 0;
                        background: {'#F0F9FF' if event.agent == 'Planner'
                                else '#F0FDF4' if event.agent == 'Researcher'
                                else '#FFF5F5' if event.agent == 'Critic'
                                else '#F9FAFB'}">
            <small style="color:{color};font-weight:600">{label}</small>
            </div>""",
        unsafe_allow_html=True,
    )
    st.markdown(event.content)
    st.divider()


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    max_rounds = st.slider(
        "Max debate rounds",
        min_value=1, max_value=4, value=2,
        help="More rounds = deeper analysis but longer runtime"
    )

    st.divider()
    st.header("Example topics")
    examples = [
        "The impact of AI on software engineering jobs in 2026",
        "Is remote work more productive than office work?",
        "The future of electric vehicles vs hydrogen fuel cells",
        "Will LLMs replace traditional search engines?",
        "The risks and benefits of open source AI models",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.topic = ex

    st.divider()
    st.header("Saved reports")
    reports = sorted(Path("reports").glob("*.md"), reverse=True)
    if reports:
        for r in reports[:5]:
            with st.expander(r.stem[:40]):
                st.markdown(r.read_text())
    else:
        st.caption("No reports yet.")


# ── Main area ──────────────────────────────────────────────────────────────
topic = st.text_input(
    "Analysis topic:",
    value=st.session_state.get("topic", ""),
    placeholder="Enter any topic to analyse...",
)

col1, col2 = st.columns([1, 4])
run_btn = col1.button("▶ Run debate", type="primary", disabled=not topic.strip())
col2.markdown(
    "<small style='color:#6B7280'>The debate takes 2-4 minutes depending on rounds selected</small>",
    unsafe_allow_html=True,
)

if run_btn and topic.strip():
    st.divider()

    # Two-column layout — debate on left, live report on right
    left, right = st.columns([3, 2])

    with left:
        st.subheader("🗣️ Live debate")
        debate_container = st.container()

    with right:
        st.subheader("📄 Final report")
        report_placeholder = st.empty()
        report_placeholder.info("Report will appear here once the debate concludes...")

    # Run debate and render events as they arrive
    with debate_container:
        final_report = None
        report_path  = None

        for event in run_debate(topic, max_rounds=max_rounds):
            render_event(event)

            # When the final report arrives, update the right panel
            if event.stage == "final" and event.agent == "Planner":
                final_report = event.content
                report_placeholder.markdown(final_report)

            elif event.stage == "final" and event.agent == "System" and "saved" in event.content:
                report_path = event.content

    # Summary bar below
    if final_report:
        st.divider()
        st.success(f"✓ Analysis complete — {report_path or 'report generated'}")
        st.download_button(
            label="⬇️ Download report",
            data=final_report,
            file_name=f"analysis_{topic[:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )