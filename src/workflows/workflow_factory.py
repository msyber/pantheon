# src/pantheon/workflows/workflow_factory.py
from src.workflows.crewai_workflow import CrewAIWorkflow
from src.workflows.langgraph_workflow import LangGraphWorkflow


class WorkflowFactory:
    @staticmethod
    def create_workflow(mission_config: dict, agents: dict, tasks: list, economic_governor, orchestrator_override: str = None):
        """
        Creates a workflow engine instance based on the orchestrator adapter specified in the mission config.
        """
        orchestrator = orchestrator_override or mission_config.get("orchestrator_adapter", "crewai") # Default to crewai

        if orchestrator == "crewai":
            return CrewAIWorkflow(mission_config, agents, tasks, economic_governor)
        elif orchestrator == "langgraph":
            return LangGraphWorkflow(mission_config, agents, tasks, economic_governor)
        else:
            raise ValueError(f"Unsupported orchestrator adapter: {orchestrator}")
