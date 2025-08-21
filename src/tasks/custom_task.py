from pydantic import BaseModel, ConfigDict

from src.agents.base_agent import BaseAgent


class CustomTask(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    task_id: str
    description: str
    agent: BaseAgent
    expected_output: str
