# src/pantheon/workflows/base_workflow.py
from abc import ABC, abstractmethod


class BaseWorkflow(ABC):
    """
    Abstract base class for all workflow execution engines.
    """
    def __init__(self, mission_config: dict, agents: dict, tasks: list):
        self.mission_config = mission_config
        self.agents = agents
        self.tasks = tasks

    @abstractmethod
    def execute(self) -> str:
        """
        Executes the defined workflow and returns the final result.
        """
        pass
