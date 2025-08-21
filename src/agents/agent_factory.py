# src/pantheon/agents/agent_factory.py
from crewai import Agent

from src.agents.base_agent import BaseAgent
from src.identity.permission_manager import PermissionManager
from src.llm_providers.llm_factory import LLMFactory
from src.observability import logger
from src.tools.tool_registry import ToolRegistry


class CrewAIAgentAdapter(BaseAgent):
    def __init__(self, crewai_agent: Agent, id: str):
        super().__init__(
            id=id,
            role=crewai_agent.role,
            goal=crewai_agent.goal,
            backstory=crewai_agent.backstory,
            tools=crewai_agent.tools
        )
        self._crewai_agent = crewai_agent

    def invoke(self, input: dict) -> dict:
        # CrewAI agent's invoke method expects 'input', 'tools', 'tool_names'
        # We need to extract these from the generic input dict if they are there
        # Or pass the whole input if the underlying agent can handle it
        # For now, assuming the input dict directly maps to what crewai_agent.agent_executor.invoke expects
        return self._crewai_agent.agent_executor.invoke(input)

    @property
    def agent_executor(self):
        return self._crewai_agent.agent_executor


class AgentFactory:
    def __init__(self, llm_provider: str = None):
        self.llm_factory = LLMFactory()
        self.tool_registry = ToolRegistry()
        self.llm_provider = llm_provider

    def _get_agent_tools(self, agent_id: str, permission_manager: PermissionManager) -> list:
        """Equips an agent with tools based on its permissions."""
        agent_tools = []
        for tool_id in self.tool_registry.get_all_tool_ids():
            required_permission = self.tool_registry.get_permission_for_tool(tool_id)
            if permission_manager.is_allowed(agent_id, required_permission):
                tool = self.tool_registry.get_tool(tool_id)
                if tool:
                    agent_tools.append(tool)

        logger.info(f"Equipping agent '{agent_id}' with tools: {[tool.name for tool in agent_tools]}")
        return agent_tools

    def _build_agent_from_config(self, agent_config: dict, permission_manager: PermissionManager) -> BaseAgent:
        """Builds a single agent from its config, using a provided permission manager."""
        agent_id = agent_config.get("id")
        llm_provider_id = self.llm_provider or agent_config.get("llm_provider")

        if not agent_id or not llm_provider_id:
            raise ValueError(f"Agent config is missing 'id' or 'llm_provider': {agent_config}")

        llm = self.llm_factory.create_llm(llm_provider_id)
        agent_tools = self._get_agent_tools(agent_id, permission_manager)

        crewai_agent = Agent(
            role=agent_config.get("role"),
            goal=agent_config.get("goal"),
            backstory=agent_config.get("backstory", "As an advanced AI, you are part of a specialized team. Your goal is to collaborate effectively to complete the mission."),
            llm=llm,
            tools=agent_tools,
            verbose=True,
            allow_delegation=False,
        )
        return CrewAIAgentAdapter(crewai_agent, agent_id)

    def create_agent(self, agent_config: dict) -> BaseAgent:
        """
        Creates a single Agent object from a configuration dictionary.
        """
        # For a single agent, the permission manager only needs its own config.
        permission_manager = PermissionManager({"agents": [agent_config]})
        return self._build_agent_from_config(agent_config, permission_manager)

    def create_agents(self, agent_definitions: dict) -> dict[str, BaseAgent]:
        """
        Creates a list of Agent objects based on a resolved definition dictionary,
        and equips them with tools based on their permissions.
        """
        permission_manager = PermissionManager(agent_definitions)
        created_agents = {}

        for agent_config in agent_definitions.get("agents", []):
            agent_id = agent_config.get("id")
            created_agents[agent_id] = self._build_agent_from_config(agent_config, permission_manager)

        return created_agents
