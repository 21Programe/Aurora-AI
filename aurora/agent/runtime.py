"""Runtime mínimo e extensível do agente Aurora.

O runtime coordena estado e inferência sem conceder permissões implícitas
para executar ferramentas. Ferramentas serão registradas explicitamente em
uma camada posterior.
"""

from typing import Dict, List, Optional

from aurora.ai_service import AuroraAIService
from aurora.agent.state import AgentState, AgentMode
from aurora.agent.permissions import ToolPolicy
from aurora.agent.tool_router import ToolRouter


class AuroraAgent:
    def __init__(self, ai_service: Optional[AuroraAIService] = None) -> None:
        self.ai_service = ai_service or AuroraAIService()
        self.state = AgentState()
        self.tools: Dict[str, object] = {}
        self.tool_router = ToolRouter()
        self.policy = ToolPolicy()

    def register_tool(self, name: str, tool: object) -> None:
        if not name or not name.strip():
            raise ValueError("nome da ferramenta é obrigatório")
        if name in self.tools:
            raise ValueError(f"ferramenta já registrada: {name}")
        self.tools[name] = tool
        self.tool_router.register(name, tool)

    def think(self, messages: List[Dict[str, str]]) -> str:
        self.state.set_mode(AgentMode.THINKING)
        try:
            return self.ai_service.chat(messages)
        finally:
            self.state.set_mode(AgentMode.IDLE)

    def use_tool(self, name: str, **kwargs):
        self.state.set_mode(AgentMode.USING_TOOL)
        try:
            self.policy.require(name)
            return self.tool_router.execute(name, **kwargs)
        finally:
            self.state.set_mode(AgentMode.IDLE)

    def authorize_tools(self, *names: str) -> None:
        self.policy = ToolPolicy(frozenset(names))
