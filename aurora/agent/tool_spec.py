"""Contrato declarativo para ferramentas do agente."""
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[..., Any]
    requires_authorization: bool = True
    category: str = "general"
    destructive: bool = False

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("nome da ferramenta é obrigatório")
        if not callable(self.handler):
            raise TypeError("handler deve ser chamável")
        if not self.category.strip():
            raise ValueError("categoria da ferramenta é obrigatória")
