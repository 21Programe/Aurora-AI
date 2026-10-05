from aurora.sentinel import SystemSentinel


def test_sentinel_can_start_and_stop_without_waiting_full_interval():
    sentinel = SystemSentinel(monitor_interval=60, autostart=False)
    assert sentinel.running is False

    sentinel.start()
    assert sentinel.running is True
    assert sentinel.monitor_thread is not None

    sentinel.stop(join_timeout=1)
    assert sentinel.running is False
    assert sentinel.monitor_thread.is_alive() is False


def test_sentinel_start_is_idempotent():
    sentinel = SystemSentinel(monitor_interval=60, autostart=False)
    sentinel.start()
    first_thread = sentinel.monitor_thread

    sentinel.start()

    assert sentinel.monitor_thread is first_thread
    sentinel.stop(join_timeout=1)


def test_sentinel_rejects_invalid_interval():
    try:
        SystemSentinel(monitor_interval=0, autostart=False)
    except ValueError:
        pass
    else:
        raise AssertionError("Intervalo inválido deveria ser rejeitado")
