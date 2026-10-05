"""Persistência SQLite do Aurora IA.

Este módulo centraliza o acesso ao banco para evitar conexões SQL espalhadas
pelo código da aplicação.
"""

import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from aurora.config import settings


class AuroraDatabase:
    """Camada mínima de persistência SQLite para o Aurora."""

    TABLES = (
        "historico",
        "relatorios_vuln",
        "base_conhecimento_rag",
        "memoria_contexto_longo",
    )

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path or settings.DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(
            self.db_path,
            timeout=20,
            check_same_thread=False,
        )

    def initialize(self) -> None:
        """Cria as tabelas necessárias sem apagar dados existentes."""
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS historico (
                    id_interacao INTEGER PRIMARY KEY AUTOINCREMENT,
                    mensagem_usuario TEXT,
                    resposta_aurora TEXT,
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS relatorios_vuln (
                    id_relatorio INTEGER PRIMARY KEY AUTOINCREMENT,
                    alvo TEXT,
                    tipo_vulnerabilidade TEXT,
                    descricao TEXT,
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS base_conhecimento_rag (
                    id_chunk INTEGER PRIMARY KEY AUTOINCREMENT,
                    origem TEXT,
                    conteudo_texto TEXT,
                    vetor_json TEXT,
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS memoria_contexto_longo (
                    id_memoria INTEGER PRIMARY KEY AUTOINCREMENT,
                    texto_interacao TEXT,
                    vetor_json TEXT,
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    def clear_memory(self) -> None:
        """Apaga somente dados de memória/RAG usando uma whitelist fixa."""
        with self.connect() as conn:
            for table in ("historico", "base_conhecimento_rag", "memoria_contexto_longo"):
                conn.execute(f"DELETE FROM {table}")

    def fetch_history(self, limit: int = 12) -> list[tuple]:
        """Retorna o histórico recente para montagem do contexto da IA."""
        if limit < 1:
            raise ValueError("limit deve ser >= 1")
        with self.connect() as conn:
            return conn.execute(
                "SELECT mensagem_usuario, resposta_aurora "
                "FROM historico ORDER BY id_interacao DESC LIMIT ?",
                (limit,),
            ).fetchall()

    def fetch_vulnerability_reports(self) -> list[tuple]:
        """Retorna relatórios de vulnerabilidade para a interface."""
        with self.connect() as conn:
            return conn.execute(
                "SELECT id_relatorio, alvo, tipo_vulnerabilidade, descricao, data_hora "
                "FROM relatorios_vuln ORDER BY id_relatorio DESC"
            ).fetchall()

    def insert(self, table: str, columns: Iterable[str], values: Iterable[object]) -> None:
        """Insere dados após validar tabela, colunas e quantidade de valores."""
        if table not in self.TABLES:
            raise ValueError(f"Tabela não permitida: {table}")

        column_list = tuple(columns)
        value_list = tuple(values)

        if not column_list:
            raise ValueError("É necessário informar ao menos uma coluna.")
        if len(column_list) != len(value_list):
            raise ValueError("Quantidade de colunas e valores não corresponde.")
        if any(
            not isinstance(column, str) or not column.isidentifier()
            for column in column_list
        ):
            raise ValueError("Nome de coluna inválido.")

        placeholders = ", ".join("?" for _ in column_list)
        names = ", ".join(column_list)

        with self.connect() as conn:
            conn.execute(
                f"INSERT INTO {table} ({names}) VALUES ({placeholders})",
                value_list,
            )
