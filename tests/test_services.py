import tempfile
from pathlib import Path

from aurora.database import AuroraDatabase
from aurora.services import AuroraPersistenceService


class FakeMemory:
    def __init__(self):
        self.calls = []

    def memorize_interaction(self, user, answer):
        self.calls.append((user, answer))
        return True


def make_service():
    temp_dir = tempfile.TemporaryDirectory()
    database = AuroraDatabase(Path(temp_dir.name) / "test.db")
    return temp_dir, database


def test_persistence_service_saves_interaction_and_memory():
    temp_dir, database = make_service()
    try:
        memory = FakeMemory()
        service = AuroraPersistenceService(database=database, memory=memory)

        assert service.save_interaction("user", "answer") is True
        assert memory.calls == [("user", "answer")]
        assert database.fetch_history(1) == [("user", "answer")]
    finally:
        temp_dir.cleanup()


def test_persistence_service_builds_llm_history():
    temp_dir, database = make_service()
    try:
        service = AuroraPersistenceService(database=database)
        database.insert("historico", ("mensagem_usuario", "resposta_aurora"), ("u1", "a1"))

        history = service.build_history_context("system", limit=1)

        assert history == [
            {"role": "system", "content": "system"},
            {"role": "user", "content": "u1"},
            {"role": "assistant", "content": "a1"},
        ]
    finally:
        temp_dir.cleanup()



def test_privacy_service_exports_data_and_cleans_history():
    from aurora.services import AuroraPrivacyService

    temp_dir, database = make_service()
    try:
        service = AuroraPrivacyService(database=database)
        database.insert("historico", ("mensagem_usuario", "resposta_aurora"), ("u", "a"))
        exported = service.export_user_data()
        assert exported["historico"][0]["mensagem_usuario"] == "u"
        assert service.cleanup_history(0) == 1
    finally:
        temp_dir.cleanup()
