import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pytest_mock import MockerFixture

from agent import OrderClient, build_agent


def model_script(mocker: MockerFixture, *responses: AIMessage):
    model = mocker.Mock(spec=BaseChatModel)
    model_with_tools = mocker.Mock()
    model_with_tools.invoke.side_effect = responses
    model.bind_tools.return_value = model_with_tools
    return model


def order_status_tool_call() -> AIMessage:
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_order_status",
                "args": {"order_id": "A-42"},
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )


def test_agent_looks_up_order_and_returns_status(mocker: MockerFixture):
    order_client = mocker.Mock(spec=OrderClient)
    order_client.get_status.return_value = "shipped"
    model = model_script(
        mocker,
        order_status_tool_call(),
        AIMessage(content="Order A-42 has shipped."),
    )
    agent = build_agent(model, order_client)

    result = agent.invoke({"messages": [HumanMessage(content="Where is order A-42?")]})

    order_client.get_status.assert_called_once_with("A-42")
    assert isinstance(result["messages"][-2], ToolMessage)
    assert result["messages"][-2].content == "shipped"
    assert result["messages"][-1].content == "Order A-42 has shipped."


def test_agent_propagates_order_service_timeout(mocker: MockerFixture):
    order_client = mocker.Mock(spec=OrderClient)
    order_client.get_status.side_effect = TimeoutError("order service unavailable")
    model = model_script(mocker, order_status_tool_call())
    agent = build_agent(model, order_client)

    with pytest.raises(TimeoutError, match="order service unavailable"):
        agent.invoke({"messages": [HumanMessage(content="Where is order A-42?")]})
