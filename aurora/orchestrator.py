"""Orquestração assíncrona de tarefas do Aurora IA."""

import concurrent.futures
import threading
from typing import Any, Callable, Dict, Optional


class RedTeamTaskOrchestrator:
    """Executa tarefas em workers e mantém estado observável dos jobs."""

    def __init__(self, message_queue, max_workers: int = 10):
        if max_workers < 1:
            raise ValueError("max_workers deve ser >= 1")
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.message_queue = message_queue
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
        self.job_counter = 0
        self._lock = threading.Lock()
        self._shutdown = False

    def submit_job(self, job_name: str, fn: Callable[..., Any], *args, **kwargs) -> str:
        with self._lock:
            if self._shutdown:
                raise RuntimeError("Orquestrador já foi encerrado.")
            self.job_counter += 1
            job_id = f"PID_{self.job_counter:04X}"
            self.active_jobs[job_id] = {
                "name": job_name,
                "future": None,
                "status": "RUNNING",
            }
            future = self.executor.submit(
                self._execution_wrapper, job_id, job_name, fn, *args, **kwargs
            )
            self.active_jobs[job_id]["future"] = future
            return job_id

    def _execution_wrapper(self, job_id: str, job_name: str, fn: Callable[..., Any], *args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            with self._lock:
                if job_id in self.active_jobs:
                    self.active_jobs[job_id]["status"] = "COMPLETED"
            return result
        except Exception as exc:
            with self._lock:
                if job_id in self.active_jobs:
                    self.active_jobs[job_id]["status"] = "FAILED"
            self.message_queue.put(
                ("ALERTA DE SUBSISTEMA", f"Falha na thread {job_id} ({job_name}): {exc}")
            )
            return None

    def cleanup_failed_jobs(self) -> None:
        with self._lock:
            failed = [
                job_id for job_id, info in self.active_jobs.items()
                if info.get("status") == "FAILED"
            ]
            for job_id in failed:
                self.active_jobs.pop(job_id, None)

    def shutdown(self, wait: bool = True) -> None:
        with self._lock:
            self._shutdown = True
        self.executor.shutdown(wait=wait)
