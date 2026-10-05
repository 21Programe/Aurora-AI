"""Estado observável do agente Aurora."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class AgentMode(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    OBSERVING = "observing"
    LISTENING = "listening"
    SPEAKING = "speaking"
    USING_TOOL = "using_tool"
    ERROR = "error"


@dataclass
class AgentState:
    mode: AgentMode = AgentMode.IDLE
    objective: Optional[str] = None
    current_task: Optional[str] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set_mode(self, mode: AgentMode) -> None:
        self.mode = mode

    def set_objective(self, objective: Optional[str]) -> None:
        self.objective = objective

    def snapshot(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "objective": self.objective,
            "current_task": self.current_task,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }
