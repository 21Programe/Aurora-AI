from aurora.services import AuroraPersistenceService


class FakeMemory:
    def __init__(self):
        self.calls = []

    def memorize_interaction(self, user, answer):
        self.calls.append((user, answer))
        return True


def test_persistence_service_saves_interaction_and_memory():
    from aurora.database import AuroraDatabase

    database = AuroraDatabase()
    memory = FakeMemory()
    service = AuroraPersistenceService(database=database, memory=memory)

    assert service.save_interaction("user", "answer") is True
    assert memory.calls == [("user", "answer")]
    assert database.fetch_history(1) == [("user", "answer")]


def test_persistence_service_builds_llm_history():
    from aurora.database import AuroraDatabase

    database = AuroraDatabase()
    service = AuroraPersistenceService(database=database)

    database.insert("historico", ("mensagem_usuario", "resposta_aurora"), ("u1", "a1"))

    history = service.build_history_context("system", limit=1)

    assert history == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "u1"},
        {"role": "assistant", "content": "a1"},
    ]
