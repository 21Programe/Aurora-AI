from aurora.ai_service import AuroraAIService


class FakeLLM:
    def __init__(self):
        self.loaded = True
        self.messages = None

    def chat(self, messages):
        self.messages = messages
        return "resposta de teste"


def test_ai_service_delegates_chat():
    llm = FakeLLM()
    service = AuroraAIService(llm)

    messages = [{"role": "user", "content": "Olá"}]

    assert service.chat(messages) == "resposta de teste"
    assert llm.messages == messages
    assert service.model_loaded is True
