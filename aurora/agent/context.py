"""Montagem determinística de contexto para o agente."""
from typing import Optional


class AgentContext:
    def __init__(self, memory=None, rag=None, max_chars: int = 20_000):
        if max_chars < 1:
            raise ValueError("max_chars deve ser positivo")
        self.memory = memory
        self.rag = rag
        self.max_chars = max_chars

    def build(self, question: str) -> str:
        if not question.strip():
            raise ValueError("pergunta não pode ser vazia")
        sections = []
        if self.memory is not None:
            remembered = self.memory.retrieve(question, top_k=3)
            if remembered:
                sections.append("MEMÓRIA:\n" + remembered)
        if self.rag is not None:
            knowledge = self.rag.retrieve(question, top_k=3)
            if knowledge:
                sections.append("CONHECIMENTO:\n" + knowledge)
        return "\n\n---\n\n".join(sections)[: self.max_chars]
