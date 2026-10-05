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


def test_database_rejects_invalid_insert_shape(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "test.db")
    db.initialize()

    try:
        db.insert("historico", ("mensagem_usuario",), ("oi", "extra"))
    except ValueError:
        pass
    else:
        raise AssertionError("Quantidade incompatível deveria ser rejeitada")

    try:
        db.insert("historico", ("mensagem-usuario",), ("oi",))
    except ValueError:
        pass
    else:
        raise AssertionError("Coluna inválida deveria ser rejeitada")


def test_database_inserts_valid_row(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "test.db")
    db.initialize()

    db.insert(
        "historico",
        ("mensagem_usuario", "resposta_aurora"),
        ("teste", "resposta"),
    )

    with db.connect() as conn:
        row = conn.execute(
            "SELECT mensagem_usuario, resposta_aurora FROM historico"
        ).fetchone()

    assert row == ("teste", "resposta")


def test_database_rejects_empty_columns(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "test.db")
    db.initialize()

    try:
        db.insert("historico", (), ())
    except ValueError:
        pass
    else:
        raise AssertionError("Inserção sem colunas deveria ser rejeitada")


def test_database_history_retention_cleanup(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "test.db")
    db.initialize()
    with db.connect() as conn:
        conn.execute(
            "INSERT INTO historico (mensagem_usuario, resposta_aurora, data_hora) "
            "VALUES (?, ?, datetime('now', '-10 days'))",
            ("antigo", "resposta"),
        )
        conn.execute(
            "INSERT INTO historico (mensagem_usuario, resposta_aurora) VALUES (?, ?)",
            ("recente", "resposta"),
        )

    assert db.cleanup_history(7) == 1
    rows = db.fetch_history(10)
    assert rows == [("recente", "resposta")]


def test_database_history_retention_rejects_negative_days(tmp_path: Path):
    db = AuroraDatabase(tmp_path / "test.db")
    db.initialize()
    try:
        db.cleanup_history(-1)
    except ValueError:
        pass
    else:
        raise AssertionError("retenção negativa deveria ser rejeitada")
