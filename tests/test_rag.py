from pathlib import Path

from aurora.database import AuroraDatabase
from aurora.rag import RAGSubsystem


def test_rag_can_initialize_without_heavy_dependencies(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "rag.db")
    rag = RAGSubsystem(database=db)

    assert rag.database.db_path == Path(tmp_path / "rag.db")
    rag.load_index()
    assert rag.initialized is True
