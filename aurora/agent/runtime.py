"""Runtime mínimo e extensível do agente Aurora.

O runtime coordena estado e inferência sem conceder permissões implícitas
para executar ferramentas. Ferramentas serão registradas explicitamente em
uma camada posterior.
"""

from typing import Dict, List, Optional

from aurora.ai_service import AuroraAIService
from aurora.agent.state import AgentState, AgentMode


class AuroraAgent:
    def __init__(self, ai_service: Optional[AuroraAIService] = None) -> None:
        self.ai_service = ai_service or AuroraAIService()
        self.state = AgentState()
        self.tools: Dict[str, object] = {}

    def register_tool(self, name: str, tool: object) -> None:
        if not name or not name.strip():
            raise ValueError("nome da ferramenta é obrigatório")
        if name in self.tools:
            raise ValueError(f"ferramenta já registrada: {name}")
        self.tools[name] = tool

    def think(self, messages: List[Dict[str, str]]) -> str:
        self.state.set_mode(AgentMode.THINKING)
        try:
            return self.ai_service.chat(messages)
        finally:
            self.state.set_mode(AgentMode.IDLE)
