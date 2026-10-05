"""Políticas explícitas de autorização para ferramentas do Aurora."""

from dataclasses import dataclass, field
from typing import FrozenSet
import secrets

from aurora.agent.tool_spec import ToolSpec


@dataclass(frozen=True)
class ToolPolicy:
    allowed_tools: FrozenSet[str] = field(default_factory=frozenset)
    allowed_categories: FrozenSet[str] = field(default_factory=frozenset)
    confirmation_token: str = field(default_factory=lambda: secrets.token_urlsafe(24), repr=False)

    def allows_spec(self, spec: ToolSpec) -> bool:
        if spec.name not in self.allowed_tools and spec.category not in self.allowed_categories:
            return False
        return True

    def allows(self, tool_name: str) -> bool:
        return tool_name in self.allowed_tools

    def require(self, tool_name: str) -> None:
        if not self.allows(tool_name):
            raise PermissionError(f"ferramenta não autorizada: {tool_name}")

    def decision(self, spec: ToolSpec) -> tuple[bool, str]:
        """Retorna decisão explícita e motivo para auditoria."""
        if spec.name not in self.allowed_tools and spec.category not in self.allowed_categories:
            return False, "tool_or_category_not_authorized"
        if spec.destructive:
            return True, "authorized_destructive_requires_confirmation"
        return True, f"authorized_risk_{spec.risk.value}"
        return True, "authorized"
