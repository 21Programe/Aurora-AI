from pathlib import Path

import pytest

from aurora.tools.filesystem import FilesystemTool
from aurora.tools.web import WebTool


def test_filesystem_tool_blocks_path_traversal(tmp_path: Path):
    tool = FilesystemTool(tmp_path)
    (tmp_path / "ok.txt").write_text("Aurora", encoding="utf-8")

    assert tool.read_text("ok.txt") == "Aurora"
    with pytest.raises(PermissionError):
        tool.read_text("../outside.txt")


def test_filesystem_tool_lists_only_authorized_root(tmp_path: Path):
    tool = FilesystemTool(tmp_path)
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    assert tool.list_files() == ["a.txt"]


def test_web_tool_validates_scheme_and_host():
    tool = WebTool(allowed_hosts=("example.com",))

    with pytest.raises(ValueError):
        tool.fetch_text("file:///etc/passwd")
    with pytest.raises(PermissionError):
        tool.fetch_text("https://not-authorized.example/")


def test_web_tool_rejects_private_host_without_allowlist():
    tool = WebTool()
    with pytest.raises(PermissionError):
        tool.fetch_text("http://127.0.0.1:8000/")


def test_web_tool_rejects_invalid_max_chars():
    tool = WebTool(allowed_hosts=("example.com",))
    with pytest.raises(ValueError):
        tool.fetch_text("https://example.com/", max_chars=0)


def test_privacy_tool_specs_classify_destructive_actions():
    from aurora.tools.privacy import PrivacyTool, privacy_tool_specs

    specs = {spec.name: spec for spec in privacy_tool_specs(PrivacyTool())}
    assert specs["privacy.export"].category == "privacy"
    assert specs["privacy.export"].destructive is False
    assert specs["privacy.cleanup_history"].destructive is True
    assert specs["privacy.delete_rag_source"].destructive is True
