from pathlib import Path

from aurora.database import AuroraDatabase


def test_database_initializes_and_clears_memory(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "test.db")
    db.initialize()

    with db.connect() as conn:
        conn.execute(
            "INSERT INTO historico (mensagem_usuario, resposta_aurora) VALUES (?, ?)",
            ("oi", "olá"),
        )

    db.clear_memory()

    with db.connect() as conn:
        count = conn.execute("SELECT COUNT(*) FROM historico").fetchone()[0]

    assert count == 0


def test_database_rejects_unknown_table(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "test.db")

    try:
        db.insert("nao_permitida", ("x",), ("y",))
    except ValueError:
        pass
    else:
        raise AssertionError("Tabela desconhecida deveria ser rejeitada")
