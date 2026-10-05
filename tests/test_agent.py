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
