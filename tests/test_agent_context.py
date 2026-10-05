from aurora.agent.context import AgentContext


class FakeMemory:
    def retrieve(self, question, top_k=3):
        return "memoria relevante"


class FakeRAG:
    def retrieve(self, question, top_k=3):
        return "documento relevante"


def test_agent_context_combines_memory_and_rag():
    context = AgentContext(FakeMemory(), FakeRAG())
    result = context.build("Python")
    assert "MEMÓRIA:" in result
    assert "memoria relevante" in result
    assert "CONHECIMENTO:" in result


def test_agent_context_rejects_empty_question():
    context = AgentContext()
    try:
        context.build(" ")
    except ValueError:
        pass
    else:
        raise AssertionError("pergunta vazia deveria ser rejeitada")
