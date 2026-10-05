"""Ferramenta explícita para controles de privacidade do Aurora."""

from aurora.services import AuroraPrivacyService
from aurora.agent.tool_spec import ToolSpec, ToolRisk


class PrivacyTool:
    """Expõe apenas operações de privacidade aprovadas pelo serviço."""

    def __init__(self, service: AuroraPrivacyService | None = None) -> None:
        self.service = service or AuroraPrivacyService()

    def export_data(self) -> dict:
        return self.service.export_user_data()

    def cleanup_history(self, retention_days: int) -> int:
        return self.service.cleanup_history(retention_days)

    def delete_rag_source(self, source_hash: str) -> int:
        return self.service.delete_rag_source(source_hash)


def privacy_tool_specs(tool: PrivacyTool | None = None) -> tuple[ToolSpec, ...]:
    tool = tool or PrivacyTool()
    return (
        ToolSpec("privacy.export", "exporta os dados armazenados", tool.export_data, category="privacy", risk=ToolRisk.HIGH),
        ToolSpec("privacy.cleanup_history", "remove histórico conforme retenção", tool.cleanup_history, category="privacy", destructive=True, risk=ToolRisk.HIGH),
        ToolSpec("privacy.delete_rag_source", "remove uma fonte do conhecimento RAG", tool.delete_rag_source, category="privacy", destructive=True, risk=ToolRisk.HIGH),
    )
