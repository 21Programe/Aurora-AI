from aurora.agent.runtime import AuroraAgent
from aurora.agent.state import AgentMode


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
    assert result == "fake response"
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
