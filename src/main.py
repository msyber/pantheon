import argparse

from crewai import Crew, Task

from src.agents.agent_factory import AgentFactory
from src.config.config_loader import ConfigLoader
from src.governance.economic_governor import EconomicGovernor
from src.memory.long_term_memory import LongTermMemory
from src.observability import logger
from src.tasks.task_factory import TaskFactory
from src.workflows.workflow_factory import WorkflowFactory


class MissionControl:
    def __init__(self, mission_id: str, llm_provider: str, orchestrator_override: str = None):
        self.mission_id = mission_id
        self.llm_provider = llm_provider

        logger.info(f"Initializing mission '{mission_id}' with LLM provider '{llm_provider}'.")

        self.config_loader = ConfigLoader()
        self.mission_config = self.config_loader.load_mission_config(mission_id)

        # The orchestrator can be overridden by a command-line argument
        self.orchestrator = orchestrator_override or self.mission_config.get("orchestrator_adapter")
        logger.info(f"Using orchestrator: {self.orchestrator}")

        # Determine the model name for cost calculation
        llm_config = self.config_loader.load_llm_config(self.llm_provider)
        model_name = llm_config.get("model")
        if not model_name:
            raise ValueError(f"Model name not found in config for provider '{self.llm_provider}'")

        agent_definitions_path = self.mission_config.get("agent_definitions") + ".yaml"
        agent_definitions = self.config_loader.load_agent_definitions(agent_definitions_path)

        self.agent_factory = AgentFactory(llm_provider=self.llm_provider)
        self.agents = self.agent_factory.create_agents(agent_definitions)

        self.task_factory = TaskFactory()
        self.tasks = self.task_factory.create_tasks(self.mission_config, self.agents, orchestrator_override=self.orchestrator)

        self.economic_governor = EconomicGovernor(
            mission_config=self.mission_config,
            llm_provider=self.llm_provider,
            model=model_name
        )
        self.workflow = WorkflowFactory.create_workflow(
            mission_config=self.mission_config, agents=self.agents, tasks=self.tasks,
            economic_governor=self.economic_governor, orchestrator_override=self.orchestrator
        )

    def run(self):
        """Assembles and runs the mission."""
        logger.info(f"--- Running Mission: {self.mission_id} ---")
        final_result_data = self.workflow.execute()
        final_result = final_result_data.get("result", "No result returned from workflow.")
        logger.info(f"--- Mission {self.mission_id} Completed ---")
        logger.info(f"Final Result: {final_result}")

        self._run_post_mission_learning(final_result)

        # Generate and log mission summary
        self._log_mission_summary(final_result)

        return final_result

    def _log_mission_summary(self, final_result: str):
        # ANSI escape codes for colors
        RESET = "\033[0m"
        BOLD = "\033[1m"
        CYAN = "\033[36m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        MAGENTA = "\033[35m"
        WHITE = "\033[37m"

        print(f"\n{CYAN}--- Mission Summary ---{RESET}")
        print(f"{BOLD}{WHITE}Mission Name:{RESET} {self.mission_id}")

        # Construct purpose from task descriptions
        purpose = f"{GREEN}Purpose:{RESET} "
        task_descriptions = []
        for task in self.mission_config.get("task_definitions", []):
            task_descriptions.append(task.get("description", ""))
        purpose += " ".join(task_descriptions)
        print(purpose)

        print(f"{YELLOW}LLM Used:{RESET} {self.llm_provider} ({self.economic_governor.model})")
        print(f"{YELLOW}Orchestrator Used:{RESET} {self.orchestrator}")
        print(f"\n{MAGENTA}{self.economic_governor.get_cost_breakdown()}{RESET}")
        print(f"{CYAN}-----------------------{RESET}")

    def _run_post_mission_learning(self, final_result: str):
        logger.info("--- Post-mission Learning Phase ---")
        ltm = LongTermMemory(self.mission_id)

        # Create the Archivist agent
        specialized_agents_config = self.config_loader.load_agent_definitions("specialized_agents.yaml")
        archivist_config = specialized_agents_config['agents'][0]

        # Use create_agent for a single agent instance
        archivist_agent = self.agent_factory.create_agent(archivist_config)

        # Define the learning task
        learning_task_description = (
            f"Analyze this mission result: '{final_result}'. "
            "Summarize the single most important lesson learned as a concise sentence."
        )

        logger.info("Executing learning task with Archivist agent...")
        lesson_learned = None
        archivist_input_tokens = 0 # Placeholder
        archivist_output_tokens = 0 # Placeholder
        archivist_agent_id = archivist_config.get("id", "AI Mission Archivist") # Get agent ID

        if self.orchestrator == "crewai":
            # If crewai orchestrator, convert to crewai.Task and use Crew
            crewai_learning_task = Task(
                description=learning_task_description,
                agent=archivist_agent._crewai_agent, # Use the underlying crewai.Agent
                expected_output="A single sentence summarizing the key lesson."
            )
            learning_crew = Crew(
                agents=[archivist_agent._crewai_agent],
                tasks=[crewai_learning_task],
                verbose=False
            )
            lesson_learned = learning_crew.kickoff()
            # TODO: Extract actual token usage from crewai_learning_task or learning_crew result
            # For now, using a rough estimate or placeholder
            archivist_input_tokens = len(learning_task_description.split()) * 2 # Rough estimate
            if lesson_learned:
                lesson_text = lesson_learned.raw if hasattr(lesson_learned, "raw") else str(lesson_learned)
                archivist_output_tokens = len(lesson_text.split()) * 2 # Rough estimate

        else:
            # For other orchestrators, directly invoke the agent with the task
            # description
            # This assumes the generic agent's invoke method can handle a simple prompt
            # and return a string output.
            result = archivist_agent.invoke({"input": learning_task_description, "tool_names": "", "tools": ""})
            lesson_learned = result.get(
                "output"
            ) # Assuming the generic agent returns a dict with 'output'
            # TODO: Extract actual token usage from result
            # For now, using a rough estimate or placeholder
            archivist_input_tokens = len(learning_task_description.split()) * 2 # Rough estimate
            if lesson_learned:
                archivist_output_tokens = len(lesson_learned.split()) * 2 # Rough estimate

        # Track cost for Archivist agent
        self.economic_governor.track_cost(
            agent_id=archivist_agent_id,
            input_tokens=archivist_input_tokens,
            output_tokens=archivist_output_tokens
        )

        # Add the lesson to Long-Term Memory
        if lesson_learned:
            # Handle both string and RichText output from crewAI or direct string output
            lesson_text = (
                lesson_learned.raw
                if hasattr(lesson_learned, "raw")
                else str(lesson_learned)
            )
            ltm.add_lesson(lesson_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a mission in Project Pantheon.")
    parser.add_argument("--mission_id", required=True, help="The ID of the mission to run.")
    parser.add_argument("--llm_provider", "--llm", default="google_gemini", help="The LLM provider to use (e.g., 'google_gemini', 'openai'). Defaults to 'google_gemini' if not specified.")
    parser.add_argument("--orchestrator", help="Override the orchestrator specified in the mission config.")

    args = parser.parse_args()

    try:
        control_plane = MissionControl(
            mission_id=args.mission_id,
            llm_provider=args.llm_provider,
            orchestrator_override=args.orchestrator
        )
        control_plane.run()
    except Exception as e:
        logger.exception(f"An error occurred during mission execution: {e}")
