"""Núcleo de inferência LLM local do Aurora IA.

O carregamento é lazy: importar este módulo não tenta carregar um GGUF.
Isso deixa testes e ferramentas de manutenção independentes da GPU/modelo.
"""

import threading
from typing import Any, Dict, List, Optional

import psutil

from aurora.config import settings
from aurora.logger import logger

try:
    from llama_cpp import Llama
except ImportError:  # pragma: no cover - depende do ambiente
    Llama = None


class LocalLLM:
    """Gerencia o modelo GGUF e serializa as chamadas de inferência."""

    def __init__(self, model_path: Optional[str] = None) -> None:
        self.model_path = model_path or str(settings.LLM_MODEL_PATH)
        self._model: Any = None
        self._lock = threading.Lock()

    @property
    def loaded(self) -> bool:
        return self._model is not None

    def load(self) -> bool:
        """Carrega o GGUF somente quando solicitado."""
        if self.loaded:
            return True

        if Llama is None:
            logger.warning("llama-cpp-python não está instalado.")
            return False

        try:
            cores_fisicos = psutil.cpu_count(logical=False) or 4
            self._model = Llama(
                model_path=self.model_path,
                n_gpu_layers=settings.LLM_GPU_LAYERS,
                n_threads=cores_fisicos,
                n_ctx=settings.LLM_CONTEXT,
                n_batch=settings.LLM_BATCH_SIZE,
                embedding=True,
                chat_format="llama-3",
                verbose=False,
            )
            logger.info("LLM local carregado: %s", self.model_path)
            return True
        except Exception:
            logger.exception("Falha ao carregar LLM local.")
            self._model = None
            return False

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Executa uma conversa local com timeout de lock configurável."""
        if not self.load():
            return "Erro Sistêmico Operacional."

        if not self._lock.acquire(timeout=settings.LLM_LOCK_TIMEOUT):
            return "Erro: LLM ocupado (timeout)."

        try:
            response = self._model.create_chat_completion(
                messages=messages,
                stream=False,
                temperature=settings.LLM_TEMPERATURE,
                frequency_penalty=settings.LLM_FREQUENCY_PENALTY,
                presence_penalty=settings.LLM_PRESENCE_PENALTY,
                max_tokens=settings.LLM_MAX_TOKENS,
            )
            choices = response.get("choices", [])
            if not choices:
                return ""
            return str(choices[0].get("message", {}).get("content", "")).strip()
        except Exception:
            logger.exception("Falha durante inferência LLM.")
            return "Falha de Integridade."
        finally:
            self._lock.release()
