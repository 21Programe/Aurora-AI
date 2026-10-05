"""Monitoramento de recursos do sistema do Aurora IA."""

import gc
import os
import subprocess
import threading
import time
from typing import Callable, Optional, Tuple

import psutil

from aurora.logger import logger

try:
    import ctypes
except ImportError:
    ctypes = None


class SystemSentinel:
    """Monitora CPU, RAM e GPU com lifecycle explícito."""

    def __init__(
        self,
        threshold_ram: int = 85,
        threshold_cpu: int = 90,
        threshold_gpu_temp: int = 82,
        monitor_interval: int = 15,
        health_callback: Optional[Callable[[], None]] = None,
        autostart: bool = True,
    ):
        if monitor_interval <= 0:
            raise ValueError("monitor_interval deve ser positivo")
        self.threshold_ram = threshold_ram
        self.threshold_cpu = threshold_cpu
        self.threshold_gpu_temp = threshold_gpu_temp
        self.monitor_interval = monitor_interval
        self.health_callback = health_callback
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        if autostart:
            self.start()

    def start(self) -> None:
        """Inicia o watchdog uma única vez."""
        if self.running:
            return
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop,
            daemon=True,
            name="SystemSentinel",
        )
        self.monitor_thread.start()
        logger.info("Sentinela de recursos iniciado")

    def obter_dados_gpu(self) -> Tuple[float, float, float]:
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            result = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                encoding="utf-8",
                creationflags=flags,
            )
            util, temp, mem_used, mem_total = map(float, result.strip().split(", "))
            vram = (mem_used / mem_total) * 100 if mem_total > 0 else 0.0
            return util, temp, vram
        except (OSError, subprocess.SubprocessError, ValueError):
            return 0.0, 0.0, 0.0

    def _limpar_ram(self) -> None:
        try:
            gc.collect()
            if os.name == "nt" and ctypes:
                try:
                    ctypes.windll.psapi.EmptyWorkingSet(
                        ctypes.windll.kernel32.GetCurrentProcess()
                    )
                except Exception:
                    logger.exception("Falha ao reduzir working set.")
            logger.info("Garbage collection executado após alerta de RAM.")
        except Exception:
            logger.exception("Falha durante limpeza de RAM.")

    def monitor_loop(self) -> None:
        psutil.cpu_percent(interval=None)
        logger.info("Watchdog do Sentinel em execução.")

        while self.running:
            try:
                if self._stop_event_wait(self.monitor_interval):
                    break

                ram_percent = psutil.virtual_memory().percent
                if ram_percent > self.threshold_ram:
                    logger.warning("RAM acima do limite: %.1f%%", ram_percent)
                    self._limpar_ram()

                cpu_percent = psutil.cpu_percent(interval=None)
                if cpu_percent > self.threshold_cpu:
                    logger.warning("CPU acima do limite: %.1f%%", cpu_percent)

                gpu_util, gpu_temp, gpu_vram = self.obter_dados_gpu()
                if gpu_temp > self.threshold_gpu_temp:
                    logger.warning("Temperatura GPU acima do limite: %.1f°C", gpu_temp)
                if gpu_vram > 95:
                    logger.warning("VRAM acima de 95%%: %.1f%%", gpu_vram)

                if self.health_callback:
                    try:
                        self.health_callback()
                    except Exception:
                        logger.exception("Falha no callback de saúde do Sentinel.")
            except Exception:
                logger.exception("Erro no monitor do Sentinel.")

    def _stop_event_wait(self, seconds: int) -> bool:
        end = time.monotonic() + seconds
        while self.running and time.monotonic() < end:
            time.sleep(min(0.25, max(0.01, end - time.monotonic())))
        return not self.running

    def stop(self, join_timeout: float = 2.0) -> None:
        """Solicita parada e aguarda a thread por um período limitado."""
        self.running = False
        thread = self.monitor_thread
        if thread and thread.is_alive():
            thread.join(timeout=join_timeout)
        logger.info("Sentinela parado")
