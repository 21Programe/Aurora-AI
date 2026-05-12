"""
AURORA IA - Cyber Security OS
==============================

Sistema de inteligência artificial para defesa cibernética.
Arquitetura modular, portável e production-ready.

Uso:
    python -m aurora.gui.app

Documentação:
    https://aurora-ia.readthedocs.io
"""

import sys
from pathlib import Path

# Adicionar aurora ao path
sys.path.insert(0, str(Path(__file__).parent))

from aurora.config import settings
from aurora.logger import logger

# Inicializar configurações
try:
    settings.validate()
    logger.info("✅ Configurações validadas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao validar configurações: {e}", exc_info=True)
    raise

__version__ = "0.1.0"
__author__ = "Diego (21Programe)"
__license__ = "MIT"

__all__ = [
    "settings",
    "logger",
    "__version__",
    "__author__",
]
