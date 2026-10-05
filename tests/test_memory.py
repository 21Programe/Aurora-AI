from pathlib import Path

from aurora.database import AuroraDatabase
from aurora.memory import ContextMemory


def test_memory_can_initialize_without_loading_a_model(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "memory.db")
    memory = ContextMemory(database=db)

    assert memory.database.db_path.name == "memory.db"
    memory.carregar_indice_memoria_longa()
