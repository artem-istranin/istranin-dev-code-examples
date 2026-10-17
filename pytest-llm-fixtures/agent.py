"""A small documentation agent with explicit model and search contracts."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


class Decision(BaseModel):
    """Allow a search query or final answer, with a nonempty string value."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    action: Literal["search_docs", "answer"]
    value: Annotated[str, Field(min_length=1, pattern=r"\S")]


@dataclass(frozen=True)
class Observation:
    """Carry a completed search and its result into the next model call."""

    query: str
    result: str


class DecisionModel(Protocol):
    """Hide SDK responses and prompt formatting behind application data."""

    def decide(
        self, *, question: str, observations: tuple[Observation, ...]
    ) -> Decision:
        """Return a validated decision or raise a model-boundary error."""
        ...


class InvalidDecision(ValueError):
    """The provider returned incomplete text or an unsupported decision."""


class ModelUnavailable(RuntimeError):
    """The provider timed out or rejected the request due to rate limiting."""


class StepLimitExceeded(RuntimeError):
    """The agent exhausted its model-call budget without a final answer."""


def run_agent(
    model: DecisionModel,
    search_docs: Callable[[str], str],
    question: str,
    *,
    max_steps: int = 3,
) -> str:
    """Start fresh, dispatch searches, and stop on an answer, error, or budget."""
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    observations: tuple[Observation, ...] = ()
    for step in range(max_steps):
        decision = model.decide(question=question, observations=observations)
        if decision.action == "answer":
            return decision.value
        if step < max_steps - 1:
            result = search_docs(decision.value)
            observations += (Observation(query=decision.value, result=result),)
    raise StepLimitExceeded("No answer within the model-call budget")
