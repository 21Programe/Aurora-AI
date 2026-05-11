"""
Configuração centralizada do Aurora IA
======================================

Este módulo gerencia todas as configurações do sistema de forma
segura, portável e escalável usando variáveis de ambiente.

Uso:
    from aurora.config import settings
    db_path = settings.DB_PATH
    model_dir = settings.MODEL_DIR
"""

import os
import logging
from pathlib import Path
from typing import Optional


class Settings:
    """
    Configurações centralizadas do Aurora IA.
    
    Suporta variáveis de ambiente para customização em produção.
    Todos os caminhos são portáveis (Windows/Linux/Mac).
    """
    
    # ========================
    # DIRETÓRIOS (Portáveis)
    # ========================
    
    # Diretório base (suporta AURORA_HOME ou usa ./aurora_core)
    BASE_DIR: Path = Path(os.getenv("AURORA_HOME", "./aurora_core"))
    
    # Criar estrutura de diretórios automaticamente
    @classmethod
    def _ensure_dirs(cls) -> None:
        """Cria todos os diretórios necessários."""
        cls.BASE_DIR.mkdir(parents=True, exist_ok=True)
        for attr in dir(cls):
            value = getattr(cls, attr)
            if isinstance(value, Path) and "_DIR" in attr:
                value.mkdir(parents=True, exist_ok=True)
    
    # Diretórios principais
    LOG_DIR: Path = BASE_DIR / "logs"
    MODEL_DIR: Path = BASE_DIR / "models"
    SANDBOX_DIR: Path = BASE_DIR / "sandbox"
    MEMORIA_DIR: Path = BASE_DIR / "memoria"
    RAG_DIR: Path = BASE_DIR / "rag"
    APROVADOS_DIR: Path = BASE_DIR / "aprovados"
    
    # Banco de dados
    DB_PATH: Path = MEMORIA_DIR / "aurora_memory.db"
    
    # ========================
    # LLM (Modelo de Linguagem)
    # ========================
    
    LLM_MODEL_NAME: str = "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"
    LLM_MODEL_PATH: Path = MODEL_DIR / LLM_MODEL_NAME
    
    # Parâmetros de GPU
    LLM_GPU_LAYERS: int = int(os.getenv("LLM_GPU_LAYERS", "25"))
    LLM_CONTEXT: int = int(os.getenv("LLM_CONTEXT", "8192"))
    LLM_BATCH_SIZE: int = int(os.getenv("LLM_BATCH_SIZE", "512"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.6"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))
    
    # Penalidades (anti-repetição)
    LLM_FREQUENCY_PENALTY: float = float(os.getenv("LLM_FREQUENCY_PENALTY", "1.2"))
    LLM_PRESENCE_PENALTY: float = float(os.getenv("LLM_PRESENCE_PENALTY", "1.2"))
    
    # Timeout para LLM
    LLM_LOCK_TIMEOUT: float = float(os.getenv("LLM_LOCK_TIMEOUT", "10.0"))
    
    # ========================
    # RAG (Retrieval-Augmented Generation)
    # ========================
    
    RAG_ENCODER_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "3"))
    RAG_CHUNK_SIZE: int = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
    
    # Cache de modelos embeddings
    RAG_CACHE_DIR: Path = MODEL_DIR / "embeddings_cache"
    
    # ========================
    # SANDBOX (Execução Segura)
    # ========================
    
    SANDBOX_TIMEOUT: int = int(os.getenv("SANDBOX_TIMEOUT", "8"))
    SANDBOX_BLACKLIST: list = [
        "os.remove",
        "shutil.rmtree",
        "subprocess",
        "os.system",
        "exec",
        "eval",
        "__import__",
    ]
    
    # ========================
    # SISTEMA (Sentinel/Monitoramento)
    # ========================
    
    # Limites de recursos
    RAM_THRESHOLD: int = int(os.getenv("RAM_THRESHOLD", "85"))  # %
    CPU_THRESHOLD: int = int(os.getenv("CPU_THRESHOLD", "90"))  # %
    GPU_TEMP_THRESHOLD: int = int(os.getenv("GPU_TEMP_THRESHOLD", "82"))  # °C
    
    # Intervalo de monitoramento
    MONITOR_INTERVAL: int = int(os.getenv("MONITOR_INTERVAL", "15"))  # segundos
    
    # ========================
    # INTERFACE GRÁFICA
    # ========================
    
    GUI_WIDTH: int = 1400
    GUI_HEIGHT: int = 750
    GUI_THEME: str = "dark"
    GUI_COLOR_THEME: str = "blue"
    
    # ========================
    # LOGGING
    # ========================
    
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Path = LOG_DIR / "aurora.log"
    LOG_MAX_BYTES: int = 10_000_000  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    LOG_FORMAT: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # ========================
    # VALIDAÇÃO
    # ========================
    
    @classmethod
    def validate(cls) -> bool:
        """
        Valida as configura��ões.
        
        Returns:
            bool: True se todas as configurações são válidas
            
        Raises:
            ValueError: Se alguma configuração crítica está inválida
        """
        errors = []
        
        # Verificar diretórios críticos
        if not cls.BASE_DIR.exists():
            errors.append(f"BASE_DIR não existe: {cls.BASE_DIR}")
        
        # Verificar modelo GGUF (aviso, não erro crítico)
        if not cls.LLM_MODEL_PATH.exists():
            logging.warning(
                f"⚠️ Modelo GGUF não encontrado em: {cls.LLM_MODEL_PATH}"
            )
        
        # Verificar valores numéricos válidos
        if not (0 <= cls.RAM_THRESHOLD <= 100):
            errors.append(f"RAM_THRESHOLD deve estar entre 0-100: {cls.RAM_THRESHOLD}")
        
        if not (0 <= cls.CPU_THRESHOLD <= 100):
            errors.append(f"CPU_THRESHOLD deve estar entre 0-100: {cls.CPU_THRESHOLD}")
        
        if not (0 < cls.SANDBOX_TIMEOUT <= 60):
            errors.append(f"SANDBOX_TIMEOUT deve estar entre 1-60s: {cls.SANDBOX_TIMEOUT}")
        
        if errors:
            raise ValueError("\n".join(errors))
        
        return True
    
    @classmethod
    def get_env(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Obtém valor de variável de ambiente com tipo seguro.
        
        Args:
            key: Nome da variável
            default: Valor padrão
            
        Returns:
            Valor da variável ou default
        """
        return os.getenv(key, default)


# Instância global única (Singleton)
settings = Settings()

# Criar diretórios na importação
settings._ensure_dirs()

# Validar configurações
try:
    settings.validate()
except ValueError as e:
    logging.error(f"Erro na configuração: {e}")
    raise
