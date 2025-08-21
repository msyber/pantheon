from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAgent(ABC):
    """
    Abstract base class for all agents in Pantheon.
    Defines the common interface that all agent implementations must adhere to.
    """

    def __init__(self, id: str, role: str, goal: str, backstory: str, tools: Optional[List[Any]] = None):
        self.id = id
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools if tools is not None else []

    @abstractmethod
    def invoke(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invokes the agent with a given input.
        The input dictionary should contain all necessary information for the agent to perform its task.
        """
        pass

    @property
    @abstractmethod
    def agent_executor(self) -> Any:
        """
        Returns the underlying agent executor.
        """
        pass
