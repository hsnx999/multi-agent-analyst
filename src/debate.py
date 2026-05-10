from dataclasses import dataclass, field
from typing import Generator
from src.agents import PlannerAgent, ResearcherAgent, CriticAgent
from src.tools import save_report


@dataclass
class DebateEvent:
    """
    A single event in the debate — one agent speaking.
    The UI consumes these events to render the debate live.
    """
    agent: str          # "Planner", "Researcher", "Critic", "System"
    stage: str          # "planning", "researching", "critiquing", "judging", "final"
    content: str
    round_num: int = 0


@dataclass
class DebateResult:
    """Final result returned after debate completes."""
    topic: str
    report: str
    report_path: str
    rounds_taken: int
    events: list = field(default_factory=list)


def run_debate(
    topic: str,
    max_rounds: int = 3,
) -> Generator[DebateEvent, None, DebateResult]:
    """
    Run the full multi-agent debate as a generator.

    Yields DebateEvent objects as each agent speaks — this allows
    the Streamlit UI to render each message as it arrives rather
    than waiting for the full debate to complete.

    Returns a DebateResult when the debate concludes.

    Usage:
        for event in run_debate("AI impact on jobs"):
            print(f"{event.agent}: {event.content}")
    """
    # Initialise fresh agents for each debate
    planner    = PlannerAgent()
    researcher = ResearcherAgent()
    critic     = CriticAgent()

    events     = []
    debate_log = []   # running transcript for context

    def emit(agent: str, stage: str, content: str, round_num: int = 0) -> DebateEvent:
        event = DebateEvent(agent=agent, stage=stage,
                           content=content, round_num=round_num)
        events.append(event)
        debate_log.append(f"## {agent} ({stage})\n{content}")
        return event

    # ── Phase 1: Planning ──────────────────────────────────────────────────
    yield emit("System", "planning", f'Starting analysis on: "{topic}"')

    plan = planner.plan(topic)
    yield emit("Planner", "planning", plan)

    # ── Phase 2: Initial Research ──────────────────────────────────────────
    yield emit("System", "researching", "Researcher is gathering evidence...")

    draft = researcher.research(plan, topic)
    yield emit("Researcher", "researching", draft, round_num=1)

    # ── Phase 3: Debate Rounds ─────────────────────────────────────────────
    rounds_taken = 1
    current_content = draft

    for round_num in range(1, max_rounds + 1):
        rounds_taken = round_num

        # Critic challenges
        yield emit("System", "critiquing",
                  f"Critic is reviewing round {round_num} draft...")

        critique = critic.critique(current_content, round_num)
        yield emit("Critic", "critiquing", critique, round_num=round_num)

        # Planner judges consensus
        debate_so_far = "\n\n".join(debate_log[-4:])  # last 4 exchanges
        judgement = planner.judge(debate_so_far)
        yield emit("Planner", "judging", judgement, round_num=round_num)

        if "CONSENSUS REACHED" in judgement.upper():
            yield emit("System", "judging", "Consensus reached — moving to final report.")
            break

        # If max rounds reached, force consensus
        if round_num == max_rounds:
            yield emit("System", "judging",
                      f"Maximum rounds ({max_rounds}) reached — synthesising final report.")
            break

        # Researcher responds to critique
        yield emit("System", "researching",
                  f"Researcher is responding to objections (round {round_num + 1})...")

        revised = researcher.respond_to_critic(critique)
        yield emit("Researcher", "researching", revised, round_num=round_num + 1)
        current_content = revised

    # ── Phase 4: Final Report ──────────────────────────────────────────────
    yield emit("System", "final", "Synthesising final report...")

    full_debate_text = "\n\n---\n\n".join(debate_log)
    report = planner.synthesise(topic, full_debate_text)
    yield emit("Planner", "final", report)

    # Save to disk
    filepath = save_report(report, topic)
    yield emit("System", "final", f"Report saved to {filepath}")

    return DebateResult(
        topic=topic,
        report=report,
        report_path=filepath,
        rounds_taken=rounds_taken,
        events=events,
    )