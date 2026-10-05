"""Políticas explícitas de autorização para ferramentas do Aurora."""

from dataclasses import dataclass, field
from typing import FrozenSet


@dataclass(frozen=True)
class ToolPolicy:
    allowed_tools: FrozenSet[str] = field(default_factory=frozenset)

    def allows(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools

    def require(self, tool_name: str) -> None:
        if not self.allows(tool_name):
            raise PermissionError(f"ferramenta não autorizada: {tool_name}")
