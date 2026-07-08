from typing import TypedDict, Annotated, Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode, tools_condition


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def build_graph(
    llm: BaseChatModel,
    tools: list[BaseTool],
) -> CompiledStateGraph:
    async def agent_node(state: AgentState):
        response = await llm.ainvoke(state["messages"])
        return {"messages": [response]}

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", ToolNode(tools))
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    return workflow.compile()
