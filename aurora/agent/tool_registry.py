"""Registro central de ferramentas aprovadas pelo Aurora.

O registry separa descoberta de ferramentas da autorização. Registrar uma
ferramenta não concede permissão para executá-la.
"""

from aurora.agent.tool_spec import ToolSpec


class ToolRegistry:
    """Mantém um catálogo único e determinístico de ToolSpec."""

    def __init__(self) -> None:
        self._specs: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        if spec.name in self._specs:
            raise ValueError(f"ferramenta já registrada: {spec.name}")
        self._specs[spec.name] = spec

    def register_many(self, specs: tuple[ToolSpec, ...] | list[ToolSpec]) -> None:
        for spec in specs:
            self.register(spec)

    def get(self, name: str) -> ToolSpec:
        try:
            return self._specs[name]
        except KeyError as exc:
            raise KeyError(f"ferramenta não encontrada: {name}") from exc

    def all(self) -> tuple[ToolSpec, ...]:
        return tuple(self._specs[name] for name in sorted(self._specs))

    def by_category(self, category: str) -> tuple[ToolSpec, ...]:
        if not category.strip():
            raise ValueError("categoria é obrigatória")
        return tuple(spec for spec in self.all() if spec.category == category)

    def names(self) -> tuple[str, ...]:
        return tuple(spec.name for spec in self.all())
