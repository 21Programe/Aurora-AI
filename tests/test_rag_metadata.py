from pathlib import Path

import pytest

from aurora.database import AuroraDatabase
from aurora.rag import RAGSubsystem


def test_rag_schema_has_source_metadata(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "rag.db")
    db.initialize()
    with db.connect() as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(base_conhecimento_rag)")}
    assert {"source_hash", "chunk_index"}.issubset(columns)


def test_rag_rejects_non_pdf(tmp_path: Path):
    source = tmp_path / "notes.txt"
    source.write_text("teste", encoding="utf-8")
    rag = RAGSubsystem(AuroraDatabase(tmp_path / "rag.db"))
    with pytest.raises(ValueError, match="somente arquivos PDF"):
        rag.ingest_pdf(str(source))
