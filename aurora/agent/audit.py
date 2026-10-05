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
    def __init__(self):
        self.events: list[AuditEvent] = []

    def record(self, action: str, tool: str, status: str, **metadata: Any) -> AuditEvent:
        event = AuditEvent(action, tool, status, datetime.now(timezone.utc).isoformat(), metadata)
        self.events.append(event)
        return event
