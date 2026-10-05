"""Roteamento seguro de ferramentas do agente Aurora."""

from typing import Any, Dict


class ToolRouter:
    """Mantém ferramentas explicitamente registradas e executa por nome."""

    def __init__(self) -> None:
        self._tools: Dict[str, Any] = {}

    def register(self, name: str, tool: Any) -> None:
        if not name or not name.strip():
            raise ValueError("nome da ferramenta é obrigatório")
        if name in self._tools:
            raise ValueError(f"ferramenta já registrada: {name}")
        if not callable(tool):
            raise TypeError("ferramenta deve ser chamável")
        self._tools[name] = tool

    def available(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def execute(self, name: str, **kwargs: Any) -> Any:
        if name not in self._tools:
            raise KeyError(f"ferramenta não registrada: {name}")
        return self._tools[name](**kwargs)
