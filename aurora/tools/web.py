"""Cliente HTTP mínimo para consultas autorizadas do agente."""
from urllib.parse import urlparse

import requests


class WebTool:
    def __init__(self, timeout: float = 10.0, allowed_hosts: tuple[str, ...] = ()):
        if timeout <= 0:
            raise ValueError("timeout deve ser positivo")
        self.timeout = timeout
        self.allowed_hosts = tuple(host.lower() for host in allowed_hosts)

    def fetch_text(self, url: str, max_chars: int = 100_000) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("URL HTTP/HTTPS inválida")
        if self.allowed_hosts and parsed.hostname.lower() not in self.allowed_hosts:
            raise PermissionError("host não autorizado")
        response = requests.get(url, timeout=self.timeout, allow_redirects=False)
        response.raise_for_status()
        return response.text[:max_chars]
