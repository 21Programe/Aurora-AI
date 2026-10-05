"""Contrato declarativo para ferramentas do agente."""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


class ToolRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    handler: Callable[..., Any]
    requires_authorization: bool = True
    category: str = "general"
    destructive: bool = False
    risk: ToolRisk = ToolRisk.LOW

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("nome da ferramenta é obrigatório")
        if not callable(self.handler):
            raise TypeError("handler deve ser chamável")
        if not self.category.strip():
            raise ValueError("categoria da ferramenta é obrigatória")
        if not isinstance(self.risk, ToolRisk):
            raise TypeError("risk deve ser ToolRisk")
        if self.destructive and self.risk is ToolRisk.LOW:
            raise ValueError("ferramenta destrutiva não pode ter risco LOW")
