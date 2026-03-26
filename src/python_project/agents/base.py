"""Base agent class for all specialized agents."""

from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel


class AgentResult(BaseModel):
    """Result from agent execution."""

    success: bool
    message: str
    data: Optional[dict[str, Any]] = None


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(self, agent_id: str, config: Any):
        self.agent_id = agent_id
        self.config = config

    @abstractmethod
    async def execute(self, task: Any) -> AgentResult:
        """Execute the agent's task."""
        pass

    def log(self, message: str) -> None:
        """Log agent activity."""
        print(f"[{self.agent_id}] {message}")
