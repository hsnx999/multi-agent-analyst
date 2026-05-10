# Multi-Agent Analyst

A multi-agent debate system where a Planner, Researcher, and Critic
collaborate to produce structured analytical reports on any topic.
Each agent has a distinct personality, persistent memory, and genuinely
challenges the others — not just relaying information.

---

## Architecture

Three agents debate using the Debate pattern:

    Planner     Strategic orchestrator. Breaks topics into research questions,
                judges whether consensus is reached, writes the final report.

    Researcher  Evidence-driven analyst. Searches the web, builds a draft,
                then defends or revises under Critic pressure.

    Critic      Adversarial challenger. Identifies unsupported claims, logical
                gaps, and missing perspectives in the Researcher's draft.

The debate loop:

    1. Planner creates research questions
    2. Researcher searches web and builds initial draft
    3. Critic challenges specific claims with objections
    4. Planner judges: CONSENSUS REACHED or DEBATE CONTINUES
    5. If continues: Researcher responds, Critic re-evaluates
    6. Planner synthesises final structured report

Each agent maintains its own persistent memory across rounds —
agents remember the full debate history, not just their last turn.

---

## What makes this different from a single agent

A single agent asked to "analyse X" will produce a balanced answer
because it has no incentive to challenge itself. In this system:

- The Critic is prompted to be adversarial — it must find flaws
- The Researcher must defend positions with evidence, not just revise
- The Planner only calls consensus when objections are genuinely resolved
- The final report reflects a debate, not a monologue

---

## Tech stack

    Library          Role
    LangChain        Agent memory and LLM orchestration
    Groq LLaMA 3.3   70B model — strong enough for multi-turn reasoning
    Tavily           Web search API designed for AI agents
    Streamlit        Live debate UI with per-agent colour coding
    BeautifulSoup    Page scraping for deeper research

---

## Run it locally

Prerequisites: Python 3.10+, free API keys from groq.com and tavily.com

    git clone https://github.com/hsnx999/multi-agent-analyst.git
    cd multi-agent-analyst
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

Create a .env file:

    GROQ_API_KEY=your_groq_key
    TAVILY_API_KEY=your_tavily_key
    LANGCHAIN_TRACING_V2=false

Run the Streamlit UI:

    streamlit run app.py

Run from terminal:

    python analyst.py

---

## Project structure

    multi-agent-analyst/
    ├── app.py              Streamlit UI — live debate with per-agent colours
    ├── analyst.py          Terminal entry point with coloured output
    ├── src/
    │   ├── agents.py       Planner, Researcher, Critic agent classes
    │   ├── debate.py       Debate loop — orchestrates agent turns
    │   ├── memory.py       Per-agent persistent memory
    │   ├── prompts.py      Distinct system prompts for each personality
    │   └── tools.py        Web search, page scraping, report saving
    ├── reports/            Saved reports (git-ignored)
    └── requirements.txt

---

## What I learned building this

- How multi-agent systems differ from pipelines — agents decide, not scripts
- Why persistent memory per agent matters for coherent multi-turn debate
- How system prompts shape agent personality using the same underlying LLM
- The Debate pattern — adversarial agents produce stronger outputs than consensus-seeking ones
- How to yield events from a generator to stream UI updates in real time
- Managing token limits across multiple agents sharing a context window