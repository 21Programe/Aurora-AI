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
