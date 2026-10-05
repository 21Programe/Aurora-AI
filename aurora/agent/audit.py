"""Auditoria estruturada das ações do agente Aurora."""
import re
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


SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|password|secret)\s*[:=]\s*[^\s,;]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
)


def _redact(value: Any) -> Any:
    if isinstance(value, str):
        result = value
        for pattern in SECRET_PATTERNS:
            result = pattern.sub(lambda match: match.group(0).split(":", 1)[0].split("=", 1)[0] + ": [REDACTED]", result)
        return result
    if isinstance(value, dict):
        return {str(key): _redact(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    return value


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
            _redact(dict(metadata)),
        )
        self.events.append(event)
        if len(self.events) > self.max_events:
            del self.events[: len(self.events) - self.max_events]
        return event

    def latest(self, *, action: str | None = None, tool: str | None = None) -> AuditEvent | None:
        """Retorna o evento mais recente que corresponde aos filtros."""
        for event in reversed(self.events):
            if action is not None and event.action != action:
                continue
            if tool is not None and event.tool != tool:
                continue
            return event
        return None

    def clear(self) -> None:
        self.events.clear()
