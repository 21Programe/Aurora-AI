from pathlib import Path
import queue
import time

import pytest

from aurora.orchestrator import RedTeamTaskOrchestrator


def wait_until(predicate, timeout_s=2.0, interval_s=0.01):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval_s)
    return False


def test_orchestrator_completes_job():
    messages = queue.Queue()
    orchestrator = RedTeamTaskOrchestrator(messages, max_workers=2)
    try:
        job_id = orchestrator.submit_job("TEST_JOB", lambda: "Concluido")
        assert wait_until(
            lambda: orchestrator.active_jobs[job_id]["status"] != "RUNNING"
        )
        assert orchestrator.active_jobs[job_id]["status"] == "COMPLETED"
    finally:
        orchestrator.shutdown()


def test_orchestrator_records_failure_and_notifies_queue():
    messages = queue.Queue()
    orchestrator = RedTeamTaskOrchestrator(messages, max_workers=1)

    def failing_job():
        raise RuntimeError("falha controlada")

    try:
        job_id = orchestrator.submit_job("FAIL_JOB", failing_job)
        assert wait_until(
            lambda: orchestrator.active_jobs[job_id]["status"] != "RUNNING"
        )
        assert orchestrator.active_jobs[job_id]["status"] == "FAILED"
        alert = messages.get(timeout=1)
        assert "FAIL_JOB" in alert[1]
        assert "falha controlada" in alert[1]
    finally:
        orchestrator.shutdown()


def test_orchestrator_rejects_submission_after_shutdown():
    messages = queue.Queue()
    orchestrator = RedTeamTaskOrchestrator(messages, max_workers=1)
    orchestrator.shutdown()

    with pytest.raises(RuntimeError):
        orchestrator.submit_job("AFTER_SHUTDOWN", lambda: None)
