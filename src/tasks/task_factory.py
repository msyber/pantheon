from crewai import Task

from src.agents.agent_factory import CrewAIAgentAdapter
from src.tasks.custom_task import CustomTask


class TaskFactory:
    def create_tasks(self, mission_config: dict, agents: dict, orchestrator_override: str = None) -> dict:
        """
        Creates a dictionary of Task objects from a mission configuration, keyed by task_id.

        Args:
            mission_config: The loaded YAML config for the mission.
            agents: A dictionary of instantiated Agent objects, keyed by their ID.
            orchestrator_override: The orchestrator being used, to determine if crewai.Task is needed.

        Returns:
            A dictionary of instantiated CustomTask or crewai.Task objects, keyed by task_id.
        """
        created_tasks_map = {}

        mission_inputs = mission_config.get("mission_inputs", {})
        task_definitions = mission_config.get("task_definitions", [])
        workflow_steps = mission_config.get("workflow_definition", {}).get("steps", [])

        # Create a mapping of task_id to description for easy lookup
        task_descriptions = {task.get("id"): task.get("description") for task in task_definitions}

        for step in workflow_steps:
            # If the step is a human approval step, skip it
            if step.get("type") == "human_approval":
                continue

            task_id = step.get("task_id")
            agent_id = step.get("agent_id")

            if not task_id or not agent_id:
                raise ValueError(f"Workflow step is missing 'task_id' or 'agent_id': {step}")

            agent = agents.get(agent_id)
            if not agent:
                raise ValueError(f"Agent with ID '{agent_id}' not found for task '{task_id}'")

            description = task_descriptions.get(task_id)
            if not description:
                raise ValueError(f"Task definition for ID '{task_id}' not found.")

            # Format the description with mission inputs
            if mission_inputs:
                description = description.format(**mission_inputs)

            # For now, we'll set a generic expected_output.
            # This can be refined in the config later.

            # If the orchestrator is crewai, create a crewai.Task
            if orchestrator_override == "crewai":
                if not isinstance(agent, CrewAIAgentAdapter):
                    raise TypeError("Agent must be a CrewAIAgentAdapter when using crewai orchestrator.")
                task = Task(
                    description=description,
                    agent=agent._crewai_agent, # Pass the underlying crewai.Agent
                    expected_output="A detailed report summarizing the results of the task."
                )
            else:
                # Otherwise, create a CustomTask (BaseModel)
                task = CustomTask(
                    task_id=task_id,
                    description=description,
                    agent=agent,
                    expected_output="A detailed report summarizing the results of the task."
                )
            created_tasks_map[task_id] = task

        return created_tasks_map
