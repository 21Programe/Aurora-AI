"""Cliente HTTP mínimo para consultas autorizadas do agente."""
import ipaddress
import socket
from urllib.parse import urlparse

import requests


class WebTool:
    def __init__(self, timeout: float = 10.0, allowed_hosts: tuple[str, ...] = ()):
        if timeout <= 0:
            raise ValueError("timeout deve ser positivo")
        self.timeout = timeout
        self.allowed_hosts = tuple(host.lower() for host in allowed_hosts)

    @staticmethod
    def _is_private_host(hostname: str) -> bool:
        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(hostname, None)}
        except socket.gaierror as exc:
            raise ValueError("host não pôde ser resolvido") from exc
        for address in addresses:
            try:
                ip = ipaddress.ip_address(address)
            except ValueError:
                continue
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return True
        return False

    def fetch_text(self, url: str, max_chars: int = 100_000) -> str:
        if max_chars < 1:
            raise ValueError("max_chars deve ser positivo")
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("URL HTTP/HTTPS inválida")
        host = parsed.hostname.lower()
        if self.allowed_hosts:
            if host not in self.allowed_hosts:
                raise PermissionError("host não autorizado")
        elif self._is_private_host(host):
            raise PermissionError("host privado não permitido sem allowlist")
        response = requests.get(
            url,
            timeout=self.timeout,
            allow_redirects=False,
            stream=True,
            headers={"User-Agent": "AuroraAI/agent-web-tool"},
        )
        response.raise_for_status()
        chunks = []
        total = 0
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if not chunk:
                continue
            remaining = max_chars - total
            if remaining <= 0:
                break
            piece = chunk[:remaining]
            chunks.append(piece)
            total += len(piece)
            if total >= max_chars:
                break
        return "".join(chunks)



def web_tool_specs(tool: WebTool) -> tuple:
    from aurora.agent.tool_spec import ToolSpec, ToolRisk
    return (
        ToolSpec("web.fetch_text", "consulta texto via HTTP/HTTPS com controles de host", tool.fetch_text, category="web", risk=ToolRisk.MEDIUM),
    )
