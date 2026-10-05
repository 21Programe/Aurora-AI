import pytest

from aurora.agent.tool_spec import ToolSpec


def test_tool_spec_requires_name_and_callable():
    spec = ToolSpec("echo", "retorna entrada", lambda value: value)
    assert spec.handler("ok") == "ok"
    assert spec.requires_authorization is True
    assert spec.category == "general"

    with pytest.raises(ValueError):
        ToolSpec("", "inválida", lambda: None)

    with pytest.raises(TypeError):
        ToolSpec("bad", "inválida", object())


def test_tool_spec_requires_category():
    with pytest.raises(ValueError):
        ToolSpec("privacy", "controle", lambda: None, category=" ")
