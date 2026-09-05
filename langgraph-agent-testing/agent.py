from typing import Protocol

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


class OrderClient(Protocol):
    def get_status(self, order_id: str) -> str: ...


def build_agent(model: BaseChatModel, order_client: OrderClient):
    @tool
    def get_order_status(order_id: str) -> str:
        """Return the current status of an order."""
        return order_client.get_status(order_id)

    tools = [get_order_status]
    model_with_tools = model.bind_tools(tools)

    def call_model(state: MessagesState):
        response = model_with_tools.invoke(
            [
                SystemMessage(content="Help customers track their orders."),
                *state["messages"],
            ]
        )
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("model", call_model)
    builder.add_node("tools", ToolNode(tools, handle_tool_errors=False))
    builder.add_edge(START, "model")
    builder.add_conditional_edges("model", tools_condition)
    builder.add_edge("tools", "model")
    return builder.compile()
