"""Auditoria estruturada das ações do agente Aurora."""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    action: str
    tool: str
    status: str
    timestamp: str
    metadata: dict[str, Any]


class AgentAuditLog:
    """Auditoria em memória com limite para evitar crescimento ilimitado."""

    def __init__(self, max_events: int = 1_000):
        if max_events < 1:
            raise ValueError("max_events deve ser positivo")
        self.max_events = max_events
        self.events: list[AuditEvent] = []

    def record(self, action: str, tool: str, status: str, **metadata: Any) -> AuditEvent:
        event = AuditEvent(
            action,
            tool,
            status,
            datetime.now(timezone.utc).isoformat(),
            dict(metadata),
        )
        self.events.append(event)
        if len(self.events) > self.max_events:
            del self.events[: len(self.events) - self.max_events]
        return event

    def clear(self) -> None:
        self.events.clear()
