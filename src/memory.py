# Each agent gets its own AgentMemory instance.
# Memory is just a list of messages — simple but powerful.

from dataclasses import dataclass, field
from typing import Literal


Role = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: Role
    content: str
    agent: str = ""   # which agent sent this — used by the UI


@dataclass
class AgentMemory:
    """
    Stores the full conversation history for one agent.
    Each agent maintains its own memory independently.

    The messages list is what gets sent to the LLM on every turn —
    the LLM sees the entire debate history from this agent's perspective.
    """
    agent_name: str
    messages: list = field(default_factory=list)

    def add_system(self, content: str):
        """Set the agent's system prompt — called once at initialisation."""
        self.messages.append(Message(role="system", content=content, agent=self.agent_name))

    def add_user(self, content: str):
        """Add a message from the orchestrator/debate loop to this agent."""
        self.messages.append(Message(role="user", content=content, agent="orchestrator"))

    def add_assistant(self, content: str):
        """Record this agent's own response."""
        self.messages.append(Message(role="assistant", content=content, agent=self.agent_name))

    def to_langchain_messages(self) -> list:
        """
        Convert to LangChain message format for the LLM call.
        LangChain expects HumanMessage, AIMessage, SystemMessage objects.
        """
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        result = []
        for msg in self.messages:
            if msg.role == "system":
                result.append(SystemMessage(content=msg.content))
            elif msg.role == "user":
                result.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                result.append(AIMessage(content=msg.content))
        return result

    def clear(self):
        """Reset memory — keep system prompt, clear everything else."""
        system = [m for m in self.messages if m.role == "system"]
        self.messages = system