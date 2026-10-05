from pathlib import Path

import numpy as np

from aurora.database import AuroraDatabase
from aurora.memory import ContextMemory


class FakeRAG:
    def embed(self, text: str):
        if "Python" in text:
            return np.array([1.0, 0.0], dtype="float32")
        return np.array([0.0, 1.0], dtype="float32")


def test_memory_can_initialize_without_loading_a_model(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "memory.db")
    memory = ContextMemory(database=db, rag=FakeRAG())

    assert memory.database.db_path.name == "memory.db"
    memory.carregar_indice_memoria_longa()


def test_memory_retrieves_semantically_closest_interaction(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "memory.db")
    memory = ContextMemory(database=db, rag=FakeRAG())

    assert memory.memorize_interaction("Quero estudar Python", "Vamos praticar.")
    assert memory.memorize_interaction("Quero estudar redes", "Vamos praticar TCP/IP.")

    result = memory.retrieve("Python", top_k=1)

    assert "Python" in result
    assert "redes" not in result


def test_memory_rejects_invalid_top_k(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "memory.db")
    memory = ContextMemory(database=db, rag=FakeRAG())
    try:
        memory.retrieve("Python", top_k=0)
    except ValueError:
        pass
    else:
        raise AssertionError("top_k inválido deveria ser rejeitado")


def test_memory_empty_question_returns_empty(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "memory.db")
    memory = ContextMemory(database=db, rag=FakeRAG())
    assert memory.retrieve("   ") == ""
