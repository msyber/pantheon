import os

import yaml


class ConfigLoader:
    def __init__(self, base_config_path="config"):
        self.base_config_path = base_config_path

    def _load_yaml(self, file_path: str) -> dict:
        full_path = os.path.join(self.base_config_path, file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Configuration file not found: {full_path}")
        with open(full_path, 'r') as f:
            return yaml.safe_load(f)

    def load_mission_config(self, mission_id: str) -> dict:
        return self._load_yaml(os.path.join("missions", f"{mission_id}.yaml"))

    def load_llm_config(self, llm_provider_id: str) -> dict:
        return self._load_yaml(os.path.join("llm_providers", f"{llm_provider_id}.yaml"))

    def load_agent_definitions(self, agent_definitions_file: str) -> dict:
        return self._load_yaml(os.path.join("agents", agent_definitions_file))

    def load_tool_config(self, tool_id: str) -> dict:
        return self._load_yaml(os.path.join("tools", tool_id))

    def load_workflow_config(self, workflow_id: str) -> dict:
        return self._load_yaml(os.path.join("workflows", f"{workflow_id}.yaml"))

    def load_llm_costs(self) -> dict:
        return self._load_yaml(os.path.join("llm_providers", "llm_costs.yaml"))
