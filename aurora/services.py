"""Serviços de aplicação para persistência e histórico do Aurora IA."""

from typing import Optional

from aurora.database import AuroraDatabase
from aurora.memory import ContextMemory
from aurora.orchestrator import RedTeamTaskOrchestrator


class AuroraPersistenceService:
    """Coordena histórico, relatórios e memória sem depender da GUI."""

    def __init__(
        self,
        database: Optional[AuroraDatabase] = None,
        memory: Optional[ContextMemory] = None,
    ) -> None:
        self.database = database or AuroraDatabase()
        self.database.initialize()
        self.memory = memory

    def save_interaction(
        self,
        user: str,
        aurora: str,
        orchestrator: Optional[RedTeamTaskOrchestrator] = None,
    ) -> bool:
        self.database.insert(
            "historico",
            ("mensagem_usuario", "resposta_aurora"),
            (user, aurora),
        )

        if self.memory is not None:
            if orchestrator is not None:
                orchestrator.submit_job(
                    "Index_Contexto_Longo",
                    self.memory.memorize_interaction,
                    user,
                    aurora,
                )
            else:
                self.memory.memorize_interaction(user, aurora)
        return True

    def build_history_context(self, system_instruction: str, limit: int = 12) -> list[dict]:
        history = [{"role": "system", "content": system_instruction}]
        for user, answer in reversed(self.database.fetch_history(limit)):
            history.append({"role": "user", "content": str(user)})
            history.append({"role": "assistant", "content": str(answer)})
        return history

    def save_vulnerability_report(self, target: str, kind: str, description: str) -> bool:
        self.database.insert(
            "relatorios_vuln",
            ("alvo", "tipo_vulnerabilidade", "descricao"),
            (target, kind, description),
        )
        return True
