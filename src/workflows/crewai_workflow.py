# src/pantheon/workflows/crewai_workflow.py
import tiktoken
from crewai import Crew

from src.governance.economic_governor import EconomicGovernor
from src.observability import logger
from src.workflows.base_workflow import BaseWorkflow
from src.workflows.human_in_the_loop import HITLManager


class CrewAIWorkflow(BaseWorkflow):
    """
    Executes a series of steps, including agent tasks and human approvals.
    """
    def __init__(self, mission_config: dict, agents: dict, tasks: dict, economic_governor: EconomicGovernor):
        super().__init__(mission_config, agents, tasks)
        self.hitl_manager = HITLManager()
        # tasks is now already a dictionary from TaskFactory
        self.tasks = tasks
        self.economic_governor = economic_governor

    def execute(self) -> dict:
        """
        Executes the workflow step-by-step and returns the final result.
        """
        logger.info("--- Workflow Engine: Starting CrewAI Workflow ---")

        workflow_steps = self.mission_config.get("workflow_definition", {}).get("steps", [])
        encoding = tiktoken.get_encoding("cl100k_base")
        results_log = []

        for step in workflow_steps:
            step_type = step.get("type", "task") # Default to "task" if not specified

            if step_type == "task":
                task_id = step.get("task_id")
                agent_id = step.get("agent_id")
                task = self.tasks.get(task_id)
                if not task:
                    raise ValueError(f"Task '{task_id}' not found in task definitions.")

                logger.info(f"Executing task '{task_id}' with agent '{agent_id}'...")

                # Note: Creating a new Crew for each task is inefficient but allows for
                # human-in-the-loop steps between tasks. For fully autonomous workflows,
                # a single Crew with all tasks could be used for better performance.
                # Execute a single task with a temporary crew
                single_task_crew = Crew(agents=[task.agent], tasks=[task], verbose=False)
                result = single_task_crew.kickoff()
                results_log.append(str(result))

                # Estimate token usage
                if hasattr(result, 'raw'):
                    output_tokens = len(encoding.encode(result.raw))
                elif isinstance(result, str):
                    output_tokens = len(encoding.encode(result))
                else:
                    output_tokens = 0

                input_tokens = len(encoding.encode(task.description))

                # Track cost per agent
                self.economic_governor.track_cost(agent_id, input_tokens, output_tokens)

            elif step_type == "human_approval":
                prompt = step.get("prompt")
                if not self.hitl_manager.request_approval(prompt):
                    aborted_message = "Mission aborted by human supervisor."
                    logger.warning(aborted_message)
                    results_log.append(aborted_message)
                    break # Stop the workflow if rejected

            else:
                raise ValueError(f"Unknown workflow step type: {step_type}")

        return {"result": "\n\n".join(results_log)}
