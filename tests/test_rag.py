from pathlib import Path

from aurora.database import AuroraDatabase
from aurora.rag import RAGSubsystem


def test_rag_can_initialize_without_heavy_dependencies(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "rag.db")
    rag = RAGSubsystem(database=db)

    assert rag.database.db_path == Path(tmp_path / "rag.db")
    rag.load_index()
    assert rag.initialized is True


class FakeRAG(RAGSubsystem):
    def embed(self, text: str):
        import numpy as np
        return np.array([1.0, 0.0], dtype="float32")


def test_rag_delete_source_removes_chunks(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "rag.db")
    rag = FakeRAG(database=db)
    source_hash = "a" * 64
    db.insert(
        "base_conhecimento_rag",
        ("origem", "conteudo_texto", "vetor_json", "source_hash", "chunk_index"),
        ("manual.pdf", "conteúdo privado", "[1.0, 0.0]", source_hash, 0),
    )
    assert rag.delete_source(source_hash) == 1
    with db.connect() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM base_conhecimento_rag WHERE source_hash = ?",
            (source_hash,),
        ).fetchone()[0]
    assert count == 0
