"""Memória contextual de longo prazo do Aurora IA."""

import json
from datetime import datetime, timedelta, timezone
from typing import Optional

from aurora.config import settings

import numpy as np

from aurora.database import AuroraDatabase
from aurora.logger import logger
from aurora.rag import RAGSubsystem


class ContextMemory:
    """Armazena interações e recupera lembranças por similaridade semântica.

    A memória mantém sua própria recuperação sobre a tabela de histórico
    contextual. O índice do RAG é reservado exclusivamente para documentos.
    """

    def __init__(
        self,
        database: Optional[AuroraDatabase] = None,
        rag: Optional[RAGSubsystem] = None,
        retention_days: Optional[int] = None,
        max_text_chars: Optional[int] = None,
    ) -> None:
        self.database = database or AuroraDatabase()
        self.database.initialize()
        self.rag = rag or RAGSubsystem(self.database)
        self.retention_days = settings.MEMORY_RETENTION_DAYS if retention_days is None else retention_days
        self.max_text_chars = settings.MEMORY_MAX_TEXT_CHARS if max_text_chars is None else max_text_chars
        if self.retention_days < 0:
            raise ValueError("retention_days deve ser >= 0")
        if self.max_text_chars < 100:
            raise ValueError("max_text_chars deve ser >= 100")

    def memorize_interaction(self, user: str, aurora: str) -> bool:
        text = f"Usuário: '{user}'. Aurora: '{aurora}'."
        text = text[: self.max_text_chars]
        vector = self.rag.embed(text)
        if vector is None:
            return False

        try:
            self.database.insert(
                "memoria_contexto_longo",
                ("texto_interacao", "vetor_json"),
                (text, json.dumps(vector.tolist())),
            )
            return True
        except Exception:
            logger.exception("Falha ao salvar memória contextual.")
            return False

    def cleanup_expired(self) -> int:
        if self.retention_days == 0:
            return 0
        cutoff = (datetime.now(timezone.utc) - timedelta(days=self.retention_days)).strftime("%Y-%m-%d %H:%M:%S")
        with self.database.connect() as conn:
            cursor = conn.execute("DELETE FROM memoria_contexto_longo WHERE data_hora < ?", (cutoff,))
            return cursor.rowcount

    def delete_all(self) -> None:
        """Exclui toda a memória contextual persistida."""
        with self.database.connect() as conn:
            conn.execute("DELETE FROM memoria_contexto_longo")

    def retrieve(self, question: str, top_k: int = 3) -> str:
        if not question or not question.strip():
            return ""
        if top_k < 1:
            raise ValueError("top_k deve ser >= 1")
        self.cleanup_expired()
        vector = self.rag.embed(question)
        if vector is None:
            return ""

        with self.database.connect() as conn:
            rows = conn.execute(
                "SELECT texto_interacao, vetor_json "
                "FROM memoria_contexto_longo ORDER BY id_memoria"
            ).fetchall()

        scored = []
        for text, raw_vector in rows:
            try:
                stored = np.asarray(json.loads(raw_vector), dtype="float32")
                score = float(np.dot(vector, stored))
                scored.append((score, text))
            except (TypeError, ValueError, json.JSONDecodeError):
                continue

        scored.sort(key=lambda item: item[0], reverse=True)
        return "\n---\n".join(text for _, text in scored[:top_k])

    # Compatibilidade com a API legada.
    def memorizar_interacao(self, usuario: str, aurora: str) -> bool:
        return self.memorize_interaction(usuario, aurora)

    def resgatar_lembrancas(self, pergunta: str, limiar_top_k: int = 3) -> str:
        return self.retrieve(pergunta, limiar_top_k)

    def recuperar_contexto(self, pergunta: str, limiar_top_k: int = 3) -> str:
        return self.retrieve(pergunta, limiar_top_k)

    def carregar_indice_memoria_longa(self) -> None:
        """Mantido por compatibilidade; a memória é persistida no SQLite."""
        self.database.initialize()
