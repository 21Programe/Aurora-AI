"""Serviço de aplicação para inferência local do Aurora IA."""

from typing import Dict, List, Optional

from aurora.llm import LocalLLM


class AuroraAIService:
    """Encapsula inferência e estado do modelo para a camada de aplicação."""

    def __init__(self, llm: Optional[LocalLLM] = None) -> None:
        self.llm = llm or LocalLLM()

    @property
    def model_loaded(self) -> bool:
        return self.llm.loaded

    def chat(self, messages: List[Dict[str, str]]) -> str:
        return self.llm.chat(messages)
