"""Check graph routing, tool-result delivery, and the chosen failure policy."""

import pytest
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from agent import OrderClient, build_agent


@pytest.fixture
def order_client(mocker):
    return mocker.create_autospec(OrderClient, instance=True, spec_set=True)


@pytest.fixture
def model_script(mocker):
    def make(*responses):
        model = mocker.Mock(spec=BaseChatModel)
        bound_model = mocker.Mock(spec=["invoke"])
        bound_model.invoke.side_effect = responses
        model.bind_tools.return_value = bound_model
        return model, bound_model

    return make


def order_status_tool_call(order_id):
    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_order_status",
                "args": {"order_id": order_id},
                "id": "call-1",
                "type": "tool_call",
            }
        ],
    )


def test_direct_answer_skips_order_lookup(model_script, order_client):
    model, bound_model = model_script(AIMessage(content="Hello!"))
    agent = build_agent(model, order_client)

    result = agent.invoke({"messages": [HumanMessage(content="Hello")]})

    assert result["messages"][-1].content == "Hello!"
    bound_model.invoke.assert_called_once()
    order_client.get_status.assert_not_called()


@pytest.mark.parametrize(
    ("order_id", "status", "answer"),
    [
        pytest.param("A-42", "shipped", "Order A-42 has shipped.", id="shipped"),
        pytest.param(
            "B-17", "processing", "Order B-17 is processing.", id="processing"
        ),
    ],
)
def test_tool_result_reaches_next_turn(
    model_script, order_client, order_id, status, answer
):
    order_client.get_status.return_value = status
    model, bound_model = model_script(
        order_status_tool_call(order_id),
        AIMessage(content=answer),
    )
    agent = build_agent(model, order_client)

    result = agent.invoke(
        {"messages": [HumanMessage(content=f"Where is order {order_id}?")]}
    )

    order_client.get_status.assert_called_once_with(order_id)
    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert len(tool_messages) == 1
    tool_result = tool_messages[0]
    assert (tool_result.tool_call_id, tool_result.content) == ("call-1", status)
    assert bound_model.invoke.call_count == 2
    second_input = bound_model.invoke.call_args_list[1].args[0]
    assert tool_result in second_input
    assert result["messages"][-1].content == answer


def test_order_timeout_stops_the_graph(model_script, order_client):
    order_client.get_status.side_effect = TimeoutError("order service unavailable")
    model, bound_model = model_script(order_status_tool_call("A-42"))
    agent = build_agent(model, order_client)

    with pytest.raises(TimeoutError, match="order service unavailable"):
        agent.invoke({"messages": [HumanMessage(content="Where is order A-42?")]})

    order_client.get_status.assert_called_once_with("A-42")
    bound_model.invoke.assert_called_once()
