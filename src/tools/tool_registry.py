# src/pantheon/tools/tool_registry.py
from crewai.tools import BaseTool

from src.config.config_loader import ConfigLoader
from src.observability import logger


# --- Placeholder Tools for MVP ---
# In a real system, these would be custom classes that interact with actual APIs.
class SiemLogReaderTool(BaseTool):
    name: str = "SIEM Log Reader"
    description: str = "Reads and searches SIEM security logs for a specific string indicator. The input to this tool should be a single query string."
    def _run(self, query: str) -> str:
        # Simulate reading logs and finding a suspicious event
        logger.debug(f"TOOL_LOG: Searching SIEM for '{query}'")
        return f"Log search results for query: '{query}'... Found 1 suspicious event related to IP 198.51.100.42. [Simulated]"

class ThreatDBQuerierTool(BaseTool):
    name: str = "Threat Database Querier"
    description: str = "Queries a threat intelligence database for information."
    def _run(self, indicator: str) -> str:
        # Simulate finding the IP in a threat database
        logger.debug(f"TOOL_LOG: Querying Threat DB for '{indicator}'")
        return f"Threat database results for indicator: '{indicator}'... IP is associated with known C2 server 'Zeus'. [Simulated]"

class FirewallRuleProposerTool(BaseTool):
    name: str = "Firewall Rule Proposer"
    description: str = "Drafts a firewall rule for review."
    def _run(self, rule_spec: str) -> str:
        # Simulate drafting a rule for a human to review
        logger.debug(f"TOOL_LOG: Drafting firewall rule '{rule_spec}'")
        return f"Firewall rule proposal drafted: '{rule_spec}'. Awaiting human approval. [Simulated]"

class IsolateHostTool(BaseTool):
    name: str = "Isolate Host"
    description: str = "Isolates a host from the network to contain a potential threat."
    def _run(self, host_ip: str) -> str:
        # Simulate isolating a host
        logger.debug(f"TOOL_LOG: Isolating host {host_ip}")
        return f"Host {host_ip} has been isolated from the network. [Simulated]"

class CreateTicketTool(BaseTool):
    name: str = "Create Ticket"
    description: str = "Creates a ticket in the ticketing system to track an incident."
    def _run(self, title: str, description: str) -> str:
        # Simulate creating a ticket
        logger.debug(f"TOOL_LOG: Creating ticket with title '{title}'")
        return f"Ticket created with title '{title}' and description '{description}'. [Simulated]"

# --- Tool Registry ---
class ToolRegistry:
    """
    Manages the lifecycle of tools, loading them from configuration
    and providing them to authorized agents.
    """
    def __init__(self, tool_config_file="cyber_tools.yaml"):
        # Mapping of tool IDs from the YAML to the actual tool class instances
        self.tool_map = {
            "siem_log_reader": SiemLogReaderTool(),
            "threat_db_querier": ThreatDBQuerierTool(),
            "firewall_rule_proposer": FirewallRuleProposerTool(),
            "isolate_host": IsolateHostTool(),
            "create_ticket": CreateTicketTool(),
        }
        config_loader = ConfigLoader()
        self.config = config_loader.load_tool_config(tool_config_file)

    def get_tool(self, tool_id: str) -> BaseTool | None:
        """
        Retrieves an instantiated tool object by its ID.
        """
        return self.tool_map.get(tool_id)

    def get_permission_for_tool(self, tool_id: str) -> str | None:
        """
        Retrieves the permission required to use a specific tool.
        """
        for tool_def in self.config.get("tools", []):
            if tool_def.get("id") == tool_id:
                return tool_def.get("permission_required")
        return None

    def get_all_tool_ids(self) -> list[str]:
        """
        Returns a list of all tool IDs defined in the configuration.
        """
        return [tool.get("id") for tool in self.config.get("tools", [])]
