from aurora.sentinel import SystemSentinel


def test_gpu_fallback_without_nvidia():
    sentinel = SystemSentinel(
        threshold_ram=100,
        threshold_cpu=100,
        threshold_gpu_temp=100,
        monitor_interval=3600,
    )
    try:
        result = sentinel.obter_dados_gpu()
        assert len(result) == 3
        assert all(isinstance(value, float) for value in result)
    finally:
        sentinel.stop()
