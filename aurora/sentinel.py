"""
Sentinela de Recursos (Auto-Cura & Monitoramento)
===================================================

Monitor contínuo de CPU, RAM, GPU e saúde do sistema.
Limpeza automática de recursos e alertas de limite.
"""

import gc
import os
import subprocess
import threading
import time
from typing import Tuple, Optional

import psutil

from aurora.config import settings
from aurora.logger import logger

try:
    import ctypes
except ImportError:
    ctypes = None


class SystemSentinel:
    """
    Monitorador de recursos do sistema com auto-healing.
    
    Responsabilidades:
    - Monitorar CPU, RAM, GPU
    - Limpeza automática quando limiar atingido
    - Alertas de anomalias
    - Thread daemon de watchdog
    
    Attributes:
        threshold_ram: Limite de RAM (%)
        threshold_cpu: Limite de CPU (%)
        threshold_gpu_temp: Limite de temperatura GPU (°C)
        monitor_interval: Intervalo de monitoramento (s)
    """
    
    def __init__(
        self,
        threshold_ram: int = 85,
        threshold_cpu: int = 90,
        threshold_gpu_temp: int = 82,
        monitor_interval: int = 15,
    ):
        """
        Inicializa o sentinela.
        
        Args:
            threshold_ram: Limite RAM em % (default: 85)
            threshold_cpu: Limite CPU em % (default: 90)
            threshold_gpu_temp: Limite temperatura GPU (default: 82)
            monitor_interval: Intervalo monitoramento em s (default: 15)
        """
        self.threshold_ram = threshold_ram
        self.threshold_cpu = threshold_cpu
        self.threshold_gpu_temp = threshold_gpu_temp
        self.monitor_interval = monitor_interval
        self.running = True
        
        # Inicia thread de monitoramento
        self.monitor_thread = threading.Thread(
            target=self.monitor_loop,
            daemon=True,
            name="SystemSentinel",
        )
        self.monitor_thread.start()
        
        logger.info("🔐 Sentinela de Recursos iniciado")
    
    def obter_dados_gpu(self) -> Tuple[float, float, float]:
        """
        Obtém dados da GPU NVIDIA via nvidia-smi.
        
        Returns:
            Tupla (utilização%, temperatura°C, vram%)
            Retorna (0, 0, 0) se nvidia-smi não disponível
        """
        try:
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            res = subprocess.check_output(
                [
                    'nvidia-smi',
                    '--query-gpu=utilization.gpu,temperature.gpu,'
                    'memory.used,memory.total',
                    '--format=csv,noheader,nounits',
                ],
                encoding='utf-8',
                creationflags=flags,
            )
            util, temp, mem_used, mem_total = map(float, res.strip().split(', '))
            vram_percent = (mem_used / mem_total) * 100 if mem_total > 0 else 0
            return util, temp, vram_percent
        except Exception:
            return 0.0, 0.0, 0.0
    
    def _limpar_ram(self) -> None:
        """Limpa memória RAM."""
        try:
            gc.collect()
            
            # Windows: EmptyWorkingSet
            if os.name == "nt" and ctypes:
                try:
                    ctypes.windll.psapi.EmptyWorkingSet(
                        ctypes.windll.kernel32.GetCurrentProcess()
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao limpar working set: {e}")
            
            logger.info("💾 RAM limpa (garbage collection)")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao limpar RAM: {e}")
    
    def monitor_loop(self) -> None:
        """
        Loop principal de monitoramento (roda em thread daemon).
        """
        # Inicializar primeira leitura de CPU (sempre dá 0%)
        psutil.cpu_percent(interval=None)
        
        logger.info(f"🔄 Monitor iniciado: intervalo {self.monitor_interval}s")
        
        while self.running:
            try:
                time.sleep(self.monitor_interval)
                
                # 1. Monitorar RAM
                ram_percent = psutil.virtual_memory().percent
                if ram_percent > self.threshold_ram:
                    logger.warning(
                        f"⚠️ RAM ALTA ({ram_percent}%). "
                        f"Limpando memória..."
                    )
                    self._limpar_ram()
                
                # 2. Monitorar CPU
                cpu_percent = psutil.cpu_percent(interval=None)
                if cpu_percent > self.threshold_cpu:
                    logger.warning(
                        f"⚠️ CPU ALTA ({cpu_percent}%). "
                        f"Processador sob carga extrema."
                    )
                
                # 3. Monitorar GPU
                gpu_util, gpu_temp, gpu_vram = self.obter_dados_gpu()
                if gpu_temp > self.threshold_gpu_temp:
                    logger.warning(
                        f"🔥 GPU QUENTE ({gpu_temp}°C). "
                        f"Verifique fluxo de ar."
                    )
                if gpu_vram > 95:
                    logger.warning(
                        f"⚠️ VRAM CHEIA ({gpu_vram:.1f}%). "
                        f"Memória de vídeo crítica."
                    )
                
                # 4. Log de saúde (debug)
                if logger.level == 10:  # DEBUG
                    logger.debug(
                        f"📊 Saúde: RAM {ram_percent}% | "
                        f"CPU {cpu_percent}% | "
                        f"GPU {gpu_util}% @ {gpu_temp}°C"
                    )
            
            except Exception as e:
                logger.error(f"❌ Erro no monitor: {e}", exc_info=True)
    
    def stop(self) -> None:
        """Para o monitoramento."""
        self.running = False
        logger.info("🛑 Sentinela parado")
