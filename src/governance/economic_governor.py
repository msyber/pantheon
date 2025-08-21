# src/pantheon/governance/economic_governor.py
from src.config.config_loader import ConfigLoader
from src.observability import logger


class EconomicGovernor:
    """
    Monitors the financial cost of a mission and enforces a budget.
    """
    def __init__(self, mission_config: dict, llm_provider: str, model: str):
        governance_config = mission_config.get("governance", {})
        eco_gov_config = governance_config.get("economic_governor", {})
        self.budget = float(eco_gov_config.get("budget_usd", 0.0))
        self.agent_costs = {}
        self.llm_provider = llm_provider
        self.model = model

        config_loader = ConfigLoader()
        llm_costs_config = config_loader.load_llm_costs()

        # Retrieve cost per token for the specific LLM provider and model
        model_costs = llm_costs_config.get("llm_costs", {}).get(llm_provider, {}).get(model, {})
        self.input_cost_per_token = model_costs.get("input_cost_per_million_tokens", 0.0) / 1_000_000
        self.output_cost_per_token = model_costs.get("output_cost_per_million_tokens", 0.0) / 1_000_000

        if self.input_cost_per_token == 0.0 or self.output_cost_per_token == 0.0:
            logger.warning(f"[EcoGov] Input or output cost per token not found for {self.llm_provider}/{self.model}. Cost tracking will be inaccurate.")

    def track_cost(self, agent_id: str, input_tokens: int, output_tokens: int):
        """
        Updates the current cost based on input and output token usage for a specific agent.
        """
        cost = (input_tokens * self.input_cost_per_token) + (output_tokens * self.output_cost_per_token)
        if agent_id not in self.agent_costs:
            self.agent_costs[agent_id] = 0.0
        self.agent_costs[agent_id] += cost
        total_cost = self.get_total_cost()
        logger.info(f"[EcoGov] Cost for {agent_id}: ${cost:.6f} | Total Cost: ${total_cost:.6f} | Budget: ${self.budget:.2f}")
    def get_total_cost(self) -> float:
        """
        Calculates the total cost across all agents.
        """
        return sum(self.agent_costs.values())

    def is_budget_exceeded(self) -> bool:
        """
        Checks if the mission has gone over budget.
        """
        total_cost = self.get_total_cost()
        if self.budget > 0 and total_cost > self.budget:
            logger.critical(f"[EcoGov] ALERT: Budget exceeded! Cost: ${total_cost:.2f}, Budget: ${self.budget:.2f}")
            return True
        return False

    def get_cost_breakdown(self) -> str:
        """
        Returns a formatted string with the cost breakdown per agent.
        """
        breakdown = "Cost Breakdown per Agent:\n"
        for agent_id, cost in self.agent_costs.items():
            breakdown += f"- {agent_id}: ${cost:.6f}\n"
        breakdown += f"Total Mission Cost: ${self.get_total_cost():.6f}"
        return breakdown
