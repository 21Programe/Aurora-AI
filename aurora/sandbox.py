"""Execução experimental de pequenos trechos Python para o Aurora IA.

IMPORTANTE: este módulo não fornece isolamento de segurança. O processo é
executado com as permissões do usuário atual. Para código não confiável, use
um ambiente externo realmente isolado.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


class CodeExecutionResult:
    def __init__(self, success: bool, output: str, timed_out: bool = False):
        self.success = success
        self.output = output
        self.timed_out = timed_out


class CodeInjectionTester:
    """Executor experimental com diretório temporário e timeout."""

    def __init__(self, timeout: int = 8, max_output_chars: int = 100_000):
        if timeout <= 0:
            raise ValueError("timeout deve ser positivo")
        if max_output_chars <= 0:
            raise ValueError("max_output_chars deve ser positivo")
        self.timeout = timeout
        self.max_output_chars = max_output_chars

    def test_code(self, code_str: str) -> str:
        result = self.execute(code_str)
        if result.timed_out:
            return "❌ Execução Terminada: Timeout estourado."
        if result.success:
            output = result.output or "Execução finalizada sem saída no console."
            return f"✅ Saída da Sandbox:\n{output}"
        return f"❌ Execução falhou:\n{result.output or 'Processo terminou com erro.'}"

    def execute(self, code_str: str) -> CodeExecutionResult:
        with tempfile.TemporaryDirectory(prefix="aurora_exec_") as temp_dir:
            script = Path(temp_dir) / "main.py"
            script.write_text(code_str, encoding="utf-8")

            try:
                completed = subprocess.run(
                    [sys.executable, str(script)],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env=self._build_environment(),
                )
            except subprocess.TimeoutExpired as exc:
                output = self._truncate(
                    (exc.stdout or "") + (exc.stderr or "")
                )
                return CodeExecutionResult(False, output, timed_out=True)
            except OSError as exc:
                return CodeExecutionResult(False, str(exc))

            output = completed.stdout if completed.returncode == 0 else completed.stderr
            return CodeExecutionResult(
                completed.returncode == 0,
                self._truncate(output),
            )

    @staticmethod
    def _build_environment() -> dict:
        env = os.environ.copy()
        return {
            key: value
            for key, value in env.items()
            if key.upper() not in {"GEMINI_API_KEY", "OPENAI_API_KEY"}
        }

    def _truncate(self, output: Optional[str]) -> str:
        value = output or ""
        if len(value) <= self.max_output_chars:
            return value.strip()
        return value[: self.max_output_chars].rstrip() + "\n[saída truncada]"
