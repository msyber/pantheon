# src/identity/permission_manager.py
from src.observability import logger


class PermissionManager:
    """
    Manages agent permissions based on their loaded profiles.
    """
    def __init__(self, agent_definitions: dict | None):
        self.permissions = {}
        if not isinstance(agent_definitions, dict):
            logger.warning(f"PermissionManager initialized with invalid agent_definitions (type: {type(agent_definitions)}). No permissions will be loaded.")
            return

        for agent_config in agent_definitions.get("agents", []):
            agent_id = agent_config.get("id")
            permissions = agent_config.get("identity", {}).get("permissions", [])
            if agent_id:
                self.permissions[agent_id] = set(permissions)
                logger.debug(f"Loaded permissions for agent '{agent_id}': {self.permissions[agent_id]}")

    def is_allowed(self, agent_id: str, required_permission: str) -> bool:
        """
        Checks if an agent has the required permission.
        """
        agent_permissions = self.permissions.get(agent_id, set())
        is_auth = required_permission in agent_permissions

        status = 'ALLOWED' if is_auth else 'DENIED'
        logger.debug(f"[Auth Check] Agent: {agent_id}, Required: '{required_permission}', Status: {status}")

        return is_auth
