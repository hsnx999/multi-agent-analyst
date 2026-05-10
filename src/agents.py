import os
from langchain_groq import ChatGroq
from src.memory import AgentMemory
from src.prompts import PLANNER_PROMPT, RESEARCHER_PROMPT, CRITIC_PROMPT
from src.tools import web_search, scrape_page


def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.3,   # slight creativity — agents should sound distinct
        max_tokens=4096,
    )


class PlannerAgent:
    """
    Strategic orchestrator. Plans research questions, judges
    whether consensus has been reached, and writes the final report.
    """
    def __init__(self):
        self.name = "Planner"
        self.memory = AgentMemory(agent_name="Planner")
        self.memory.add_system(PLANNER_PROMPT)
        self.llm = get_llm()

    def plan(self, topic: str) -> str:
        """Break the topic into structured research questions."""
        prompt = f"""The user wants an analytical report on the following topic:

"{topic}"

Generate 3-5 precise research questions that will guide the investigation.
Cover different angles — be specific and actionable."""

        self.memory.add_user(prompt)
        response = self.llm.invoke(self.memory.to_langchain_messages())
        self.memory.add_assistant(response.content)
        return response.content

    def judge(self, debate_summary: str) -> str:
        """
        Decide if the debate has reached consensus.
        Returns either 'CONSENSUS REACHED' or 'DEBATE CONTINUES: [reason]'
        """
        prompt = f"""Review the following debate exchange and decide if consensus
has been reached between the Researcher and Critic.

{debate_summary}

Output ONLY one of:
- CONSENSUS REACHED
- DEBATE CONTINUES: [specific unresolved issue]"""

        self.memory.add_user(prompt)
        response = self.llm.invoke(self.memory.to_langchain_messages())
        self.memory.add_assistant(response.content)
        return response.content

    def synthesise(self, topic: str, full_debate: str) -> str:
        """Write the final structured report from the full debate."""
        prompt = f"""The debate on "{topic}" has concluded. Here is the complete exchange:

{full_debate}

Write a comprehensive, structured analytical report in markdown format.
Include:
# [Topic Title]
## Executive Summary (3-5 sentences)
## Key Findings (bullet points with evidence)
## Counterarguments Considered
## Conclusion
## Confidence Level (High/Medium/Low and why)"""

        self.memory.add_user(prompt)
        response = self.llm.invoke(self.memory.to_langchain_messages())
        self.memory.add_assistant(response.content)
        return response.content


class ResearcherAgent:
    """
    Evidence-driven analyst. Searches the web, builds a draft,
    then defends or revises under Critic pressure.
    """
    def __init__(self):
        self.name = "Researcher"
        self.memory = AgentMemory(agent_name="Researcher")
        self.memory.add_system(RESEARCHER_PROMPT)
        self.llm = get_llm()

    def research(self, research_questions: str, topic: str) -> str:
        search1 = web_search(topic, max_results=3)[:1500]
        search2 = web_search(f"{topic} impact analysis 2026", max_results=3)[:1500]

        prompt = f"""Research the following questions about "{topic}":

{research_questions}

Web search results:

--- Search 1 ---
{search1}

--- Search 2 ---
{search2}

Build a concise analytical draft (max 400 words) covering the key questions.
Use specific facts from the search results. Be direct."""

        self.memory.add_user(prompt)
        response = self.llm.invoke(self.memory.to_langchain_messages())
        self.memory.add_assistant(response.content)
        return response.content

    def respond_to_critic(self, critique: str) -> str:
        additional_search = web_search(f"{critique[:80]} evidence", max_results=3)[:1000]

        prompt = f"""The Critic raised these objections:

{critique}

Additional evidence:
{additional_search}

Respond to each objection (max 300 words). Be direct about what you accept or reject."""

        self.memory.add_user(prompt)
        response = self.llm.invoke(self.memory.to_langchain_messages())
        self.memory.add_assistant(response.content)
        return response.content

class CriticAgent:
    """
    Adversarial challenger. Identifies weaknesses, gaps,
    and unsupported claims in the Researcher's draft.
    """
    def __init__(self):
        self.name = "Critic"
        self.memory = AgentMemory(agent_name="Critic")
        self.memory.add_system(CRITIC_PROMPT)
        self.llm = get_llm()

    def critique(self, draft: str, round_num: int) -> str:
        """
        Challenge the Researcher's draft or revised response.
        Gets progressively more focused in later rounds.
        """
        if round_num == 1:
            prompt = f"""Read the following research draft carefully:

{draft}

Identify 2-4 specific weaknesses, gaps, or unsupported claims.
Be pointed and specific — reference exact statements from the draft.
Do not accept anything uncritically."""
        else:
            prompt = f"""The Researcher has responded to your previous objections:

{draft}

Evaluate their response:
- Which objections were adequately addressed?
- Which remain unresolved or were deflected without evidence?
Focus only on the most important remaining issues (max 2 objections)."""

        self.memory.add_user(prompt)
        response = self.llm.invoke(self.memory.to_langchain_messages())
        self.memory.add_assistant(response.content)
        return response.content