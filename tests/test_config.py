import pytest

from aurora.config import settings


def test_default_paths_are_portable():
    assert settings.BASE_DIR.name == "aurora_core"
    assert settings.LOG_DIR.parent == settings.BASE_DIR
    assert settings.MEMORIA_DIR.parent == settings.BASE_DIR


def test_thresholds_are_valid():
    assert 0 <= settings.RAM_THRESHOLD <= 100
    assert 0 <= settings.CPU_THRESHOLD <= 100
    assert 0 < settings.SANDBOX_TIMEOUT <= 60


def test_validate_returns_true():
    assert settings.validate() is True


def test_invalid_ram_threshold_raises():
    original = settings.RAM_THRESHOLD
    settings.RAM_THRESHOLD = 101
    try:
        with pytest.raises(ValueError):
            settings.validate()
    finally:
        settings.RAM_THRESHOLD = original


def test_model_configuration_is_portable():
    assert settings.LLM_MODEL_PATH.parent == settings.MODEL_DIR
    assert settings.RAG_ENCODER_MODEL
