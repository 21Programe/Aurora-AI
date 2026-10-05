"""
AURORA IA - Cyber Security OS
==============================

Sistema de inteligência artificial para defesa cibernética.
Arquitetura modular em refatoração, com foco em portabilidade, testes e separação de responsabilidades.
"""

from aurora.config import settings
from aurora.logger import logger

__version__ = "0.1.0"
__author__ = "Diego (21Programe)"
__license__ = "MIT"

__all__ = [
    "settings",
    "logger",
    "__version__",
    "__author__",
]
