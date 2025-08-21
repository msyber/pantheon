# src/pantheon/workflows/langgraph_workflow.py
import operator
from typing import Annotated, Sequence, TypedDict

import tiktoken
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import END, StateGraph

from src.observability import logger
from src.workflows.base_workflow import BaseWorkflow


class LangGraphWorkflow(BaseWorkflow):
    """
    Executes a workflow using LangGraph.
    """

    def __init__(self, mission_config: dict, agents: dict, tasks: dict, economic_governor):
        super().__init__(mission_config, agents, tasks)
        self.tasks = tasks
        self.economic_governor = economic_governor
        self.workflow = self._build_graph()

    def _build_graph(self):
        class AgentState(TypedDict):
            messages: Annotated[Sequence[BaseMessage], operator.add]
            task: dict
            agent: object
            tools: Sequence[object]

        def agent_node(state: AgentState):
            prompt = "\n".join([f"{m.content}" for m in state["messages"]])
            tool_names = ", ".join([tool.name for tool in state["tools"]]).strip() # Ensure no trailing comma
            tools_string = "\n".join([f"{tool.name}: {tool.description}" for tool in state["tools"]])

            inputs_for_executor = {
                "input": prompt,
                "tools": tools_string,
                "tool_names": tool_names,
                "task": state["task"] # Explicitly pass the task object
            }
            result = state["agent"].agent_executor.invoke(inputs_for_executor)
            return {"messages": [AIMessage(content=result["output"])]}

        def tool_node(state: AgentState):
            tool_calls = state["messages"][-1].tool_calls
            tool_messages = []
            for tool_call in tool_calls:
                tool = {tool.name: tool for tool in state["tools"]}[tool_call["name"]]
                output = tool.run(tool_call["args"])
                tool_messages.append(ToolMessage(content=str(output), tool_call_id=tool_call["id"]))
            return {"messages": tool_messages}

        def should_continue(state: AgentState):
            if isinstance(state["messages"][-1], ToolMessage):
                return "agent"
            if not state["messages"][-1].tool_calls:
                return END
            return "tools"

        workflow = StateGraph(AgentState)
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")

        return workflow.compile()

    def execute(self) -> dict:
        """
        Executes the workflow using LangGraph.
        """
        logger.info("--- Workflow Engine: Starting LangGraph Workflow ---")

        results_log = []
        for step in self.mission_config.get("workflow_definition", {}).get("steps", []):
            step_type = step.get("type", "task")

            if step_type == "task":
                task_id = step.get("task_id")
                agent_id = step.get("agent_id")

                task = self.tasks.get(task_id)
                agent = self.agents.get(agent_id)

                logger.info(f"Executing task '{task_id}' with agent '{agent_id}' via LangGraph...")

                initial_state = {
                    "task": task,
                    "agent": agent,
                    "tools": agent.tools,
                    "messages": [HumanMessage(content=task.description)]
                }

                final_state = self.workflow.invoke(initial_state)
                result = final_state["messages"][-1].content
                results_log.append(result)

                # Cost tracking
                encoding = tiktoken.get_encoding("cl100k_base")
                output_tokens = len(encoding.encode(result))
                input_tokens = len(encoding.encode(task.description))
                self.economic_governor.track_cost(agent_id, input_tokens, output_tokens)

            elif step_type == "human_approval":
                prompt = step.get("prompt")
                logger.info("--- [HITL] Approval Required ---")
                logger.info(f"PROMPT: {prompt}")
                logger.warning("Non-interactive environment detected. Defaulting to 'no'.")
                results_log.append("Mission aborted by human supervisor.")
                break

        return {"result": "\n\n".join(results_log)}
