from aurora.agent.runtime import AuroraAgent
from aurora.agent.state import AgentMode
import pytest


class FakeAI:
    def chat(self, messages):
        return "ok"


def test_agent_tracks_state_during_thinking():
    agent = AuroraAgent(FakeAI())

    assert agent.state.mode is AgentMode.IDLE
    assert agent.think([{"role": "user", "content": "teste"}]) == "ok"
    assert agent.state.mode is AgentMode.IDLE


def test_agent_requires_unique_tool_names():
    agent = AuroraAgent(FakeAI())
    agent.register_tool("demo", object())

    try:
        agent.register_tool("demo", object())
    except ValueError:
        pass
    else:
        raise AssertionError("Ferramentas duplicadas deveriam ser rejeitadas")


def test_agent_requires_authorization_before_tool_execution():
    agent = AuroraAgent(FakeAI())
    agent.register_tool("demo", lambda **_: "executed")

    try:
        agent.use_tool("demo")
    except PermissionError:
        pass
    else:
        raise AssertionError("Ferramenta deveria exigir autorização")

    agent.authorize_tools("demo")
    assert agent.use_tool("demo") == "executed"
    assert agent.state.mode is AgentMode.IDLE


def test_agent_registers_tool_spec_and_audits_execution():
    from aurora.agent.tool_spec import ToolSpec

    agent = AuroraAgent(FakeAI())
    agent.register_spec(ToolSpec("echo", "eco", lambda value: value))
    agent.authorize_tools("echo")
    assert agent.use_tool("echo", value="ok") == "ok"
    assert agent.audit.events[-1].tool == "echo"
    assert agent.audit.events[-1].status == "success"


def test_agent_observe_listen_and_speak_interfaces():
    agent = AuroraAgent(FakeAI())
    agent.observe("imagem analisada")
    agent.listen("comando recebido")
    assert agent.speak("resposta") == "resposta"
    assert agent.state.snapshot()["mode"] == "idle"


def test_agent_rejects_empty_perception():
    agent = AuroraAgent(FakeAI())
    for method in (agent.observe, agent.listen, agent.speak):
        try:
            method("   ")
        except ValueError:
            pass
        else:
            raise AssertionError("entrada vazia deveria ser rejeitada")


def test_agent_builds_unified_context():
    from aurora.agent.context import AgentContext

    agent = AuroraAgent(FakeAI(), AgentContext())
    assert agent.build_context("teste") == ""


def test_agent_run_cycle_injects_context():
    from aurora.agent.context import AgentContext

    class Context:
        def build(self, question):
            return "contexto recuperado"

    agent = AuroraAgent(FakeAI(), Context())
    result = agent.run_cycle("objetivo", [{"role": "user", "content": "oi"}])
    assert result == "ok"
    assert agent.state.objective == "objetivo"


def test_agent_can_authorize_tool_category():
    from aurora.agent.tool_spec import ToolSpec

    agent = AuroraAgent(FakeAI())
    agent.register_spec(ToolSpec("privacy-export", "exporta dados", lambda: "ok", category="privacy"))
    try:
        agent.use_tool("privacy-export")
    except PermissionError:
        pass
    else:
        raise AssertionError("categoria deveria exigir autorização")

    agent.authorize_categories("privacy")
    assert agent.use_tool("privacy-export") == "ok"


def test_agent_requires_confirmation_for_destructive_tool():
    from aurora.agent.tool_spec import ToolSpec

    agent = AuroraAgent(FakeAI())
    agent.register_spec(ToolSpec("delete", "remove", lambda: "deleted", category="privacy", destructive=True))
    agent.authorize_categories("privacy")
    try:
        agent.use_tool("delete")
    except PermissionError:
        pass
    else:
        raise AssertionError("ação destrutiva deveria exigir confirmação")

    assert agent.use_tool("delete", confirmation_token=agent.confirmation_token()) == "deleted"


def test_tool_registry_is_deterministic_and_rejects_duplicates():
    from aurora.agent.tool_registry import ToolRegistry
    from aurora.agent.tool_spec import ToolSpec

    registry = ToolRegistry()
    registry.register_many([
        ToolSpec("web.fetch", "web", lambda: None, category="web"),
        ToolSpec("fs.read", "filesystem", lambda: None, category="filesystem"),
    ])
    assert registry.names() == ("fs.read", "web.fetch")
    assert registry.by_category("web")[0].name == "web.fetch"
    try:
        registry.register(ToolSpec("fs.read", "duplicado", lambda: None, category="filesystem"))
    except ValueError:
        pass
    else:
        raise AssertionError("registry deveria rejeitar nomes duplicados")


def test_agent_imports_registry_without_granting_permissions(tmp_path):
    from aurora.agent.bootstrap import build_tool_registry

    registry = build_tool_registry(filesystem_root=tmp_path, web_allowed_hosts=("example.com",))
    agent = AuroraAgent(FakeAI())
    agent.register_registry(registry)

    assert agent.registry.names() == registry.names()
    with pytest.raises(PermissionError):
        agent.use_tool("filesystem.list")


def test_agent_audits_denied_authorization_with_reason():
    from aurora.agent.tool_spec import ToolSpec

    agent = AuroraAgent(FakeAI())
    agent.register_spec(ToolSpec("private", "privada", lambda: "ok", category="filesystem"))
    with pytest.raises(PermissionError):
        agent.use_tool("private")
    event = agent.audit.events[-1]
    assert event.action == "authorize"
    assert event.status == "denied"
    assert event.metadata["reason"] == "tool_or_category_not_authorized"


def test_agent_audits_confirmation_denial():
    from aurora.agent.tool_spec import ToolSpec

    agent = AuroraAgent(FakeAI())
    agent.register_spec(ToolSpec("delete", "remove", lambda: "deleted", category="privacy", destructive=True))
    agent.authorize_categories("privacy")
    with pytest.raises(PermissionError):
        agent.use_tool("delete")
    event = agent.audit.events[-1]
    assert event.action == "confirm"
    assert event.status == "denied"
    assert event.metadata["reason"] == "confirmation_required"


def test_tool_spec_requires_meaningful_risk_for_destructive_actions():
    from aurora.agent.tool_spec import ToolRisk, ToolSpec

    spec = ToolSpec("delete", "remove", lambda: None, destructive=True, risk=ToolRisk.HIGH)
    assert spec.risk is ToolRisk.HIGH
    with pytest.raises(ValueError):
        ToolSpec("unsafe", "remove", lambda: None, destructive=True)


def test_policy_decision_includes_risk():
    from aurora.agent.permissions import ToolPolicy
    from aurora.agent.tool_spec import ToolRisk, ToolSpec

    spec = ToolSpec("web.fetch", "web", lambda: None, category="web", risk=ToolRisk.MEDIUM)
    policy = ToolPolicy(allowed_categories=frozenset({"web"}))
    assert policy.decision(spec) == (True, "authorized_risk_medium")


def test_audit_latest_filters_events():
    from aurora.agent.audit import AgentAuditLog

    audit = AgentAuditLog()
    audit.record("authorize", "web.fetch", "allowed", category="web", risk="medium")
    audit.record("execute", "web.fetch", "success")
    assert audit.latest(tool="web.fetch").action == "execute"
    assert audit.latest(action="authorize", tool="web.fetch").metadata["risk"] == "medium"
    assert audit.latest(tool="missing") is None


def test_audit_redacts_secret_values_from_multiple_formats():
    from aurora.agent.audit import AgentAuditLog

    event = AgentAuditLog().record(
        "test", "demo", "ok",
        api_key="SUPERSECRET",
        token="TOKENVALUE",
        authorization="Bearer ABCDEFG123",
    )
    text = str(event.metadata)
    assert "SUPERSECRET" not in text
    assert "TOKENVALUE" not in text
    assert "ABCDEFG123" not in text
