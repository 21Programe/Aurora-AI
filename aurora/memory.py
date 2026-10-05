"""Memória contextual de longo prazo do Aurora IA."""

import json
from typing import Optional

import numpy as np

from aurora.config import settings
from aurora.database import AuroraDatabase
from aurora.logger import logger
from aurora.rag import RAGSubsystem


class ContextMemory:
    """Armazena interações e recupera lembranças por similaridade semântica."""

    def __init__(
        self,
        database: Optional[AuroraDatabase] = None,
        rag: Optional[RAGSubsystem] = None,
    ) -> None:
        self.database = database or AuroraDatabase()
        self.database.initialize()
        self.rag = rag or RAGSubsystem(self.database)

    def memorize_interaction(self, user: str, aurora: str) -> bool:
        text = f"Usuário: '{user}'. Aurora: '{aurora}'."
        vector = self.rag.embed(text)
        if vector is None:
            return False

        try:
            self.database.insert(
                "memoria_contexto_longo",
                ("texto_interacao", "vetor_json"),
                (text, json.dumps(vector.tolist())),
            )
            self.rag.load_index()
            return True
        except Exception:
            logger.exception("Falha ao salvar memória contextual.")
            return False

    def retrieve(self, question: str, top_k: int = 3) -> str:
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

    def carregar_indice_memoria_longa(self) -> None:
        """Mantido para compatibilidade; a memória é consultada diretamente no SQLite."""
        self.database.initialize()
