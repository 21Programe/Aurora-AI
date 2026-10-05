import pytest

from aurora.agent.permissions import ToolPolicy
from aurora.agent.tool_router import ToolRouter


def test_router_registers_and_executes_explicit_tool():
    router = ToolRouter()
    router.register("sum", lambda **kwargs: kwargs["a"] + kwargs["b"])

    assert router.available() == ("sum",)
    assert router.execute("sum", a=2, b=3) == 5


def test_router_rejects_duplicate_or_non_callable_tools():
    router = ToolRouter()
    router.register("demo", lambda **_: True)

    with pytest.raises(ValueError):
        router.register("demo", lambda **_: False)
    with pytest.raises(TypeError):
        router.register("invalid", object())


def test_policy_denies_tools_by_default():
    policy = ToolPolicy()

    with pytest.raises(PermissionError):
        policy.require("terminal")


def test_policy_allows_explicit_tool():
    policy = ToolPolicy(frozenset({"web"}))
    policy.require("web")
