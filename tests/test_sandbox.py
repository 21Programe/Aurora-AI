from aurora.sandbox import CodeInjectionTester


def test_executor_runs_python_with_current_interpreter():
    executor = CodeInjectionTester()
    result = executor.execute("print('ok')")
    assert result.success is True
    assert result.output == "ok"


def test_executor_uses_temporary_working_directory():
    executor = CodeInjectionTester()
    result = executor.execute(
        "from pathlib import Path; print(Path.cwd().name.startswith('aurora_exec_'))"
    )
    assert result.success is True
    assert result.output == "True"


def test_executor_times_out_long_running_code():
    executor = CodeInjectionTester(timeout=1)
    result = executor.execute("while True: pass")
    assert result.timed_out is True


def test_executor_truncates_large_output():
    executor = CodeInjectionTester(max_output_chars=20)
    result = executor.execute("print('x' * 100)")
    assert result.success is True
    assert "[saída truncada]" in result.output
    assert len(result.output) < 100


def test_executor_filters_known_api_keys_from_child_environment():
    executor = CodeInjectionTester()
    env = executor._build_environment()
    assert "GEMINI_API_KEY" not in env
    assert "OPENAI_API_KEY" not in env
