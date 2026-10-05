from aurora.llm import LocalLLM


def test_llm_is_lazy():
    llm = LocalLLM("/tmp/model.gguf")
    assert llm.loaded is False
