"""Planejamento conservador do agente.

O planner apenas produz intenção estruturada; ele não executa ferramentas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AgentPlan:
    objective: str
    action: str
    tool: Optional[str] = None
    reason: str = ""


class AgentPlanner:
    def plan(self, objective: str, action: str, tool: Optional[str] = None, reason: str = "") -> AgentPlan:
        if not objective.strip() or not action.strip():
            raise ValueError("objetivo e ação são obrigatórios")
        return AgentPlan(objective.strip(), action.strip(), tool, reason.strip())
