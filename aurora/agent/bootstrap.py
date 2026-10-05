"""Bootstrap oficial das ferramentas do Aurora.

O bootstrap somente registra capacidades aprovadas. Nenhuma permissão de
execução é concedida automaticamente.
"""

from pathlib import Path

from aurora.agent.tool_registry import ToolRegistry
from aurora.tools.filesystem import FilesystemTool, filesystem_tool_specs
from aurora.tools.privacy import PrivacyTool, privacy_tool_specs
from aurora.tools.web import WebTool, web_tool_specs


def build_tool_registry(
    *,
    filesystem_root: Path,
    web_timeout: float = 10.0,
    web_allowed_hosts: tuple[str, ...] = (),
    privacy_tool: PrivacyTool | None = None,
) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register_many(filesystem_tool_specs(FilesystemTool(filesystem_root)))
    registry.register_many(
        web_tool_specs(WebTool(timeout=web_timeout, allowed_hosts=web_allowed_hosts))
    )
    registry.register_many(privacy_tool_specs(privacy_tool))
    return registry
