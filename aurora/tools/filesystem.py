"""Operações de arquivo com raiz explícita e sem traversal."""
from pathlib import Path


class FilesystemTool:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _safe_path(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise PermissionError("caminho fora da raiz autorizada") from exc
        return candidate

    def list_files(self, relative_path: str = ".") -> list[str]:
        path = self._safe_path(relative_path)
        if not path.is_dir():
            raise NotADirectoryError(path)
        return sorted(item.name for item in path.iterdir())

    def read_text(self, relative_path: str, max_chars: int = 100_000) -> str:
        if max_chars <= 0:
            raise ValueError("max_chars deve ser positivo")
        path = self._safe_path(relative_path)
        if not path.is_file():
            raise FileNotFoundError(path)
        return path.read_text(encoding="utf-8")[:max_chars]



def filesystem_tool_specs(tool: FilesystemTool) -> tuple:
    from aurora.agent.tool_spec import ToolSpec
    return (
        ToolSpec("filesystem.list", "lista arquivos dentro da raiz autorizada", tool.list_files, category="filesystem"),
        ToolSpec("filesystem.read", "lê texto dentro da raiz autorizada", tool.read_text, category="filesystem"),
    )
