"""Adaptadores locais simples para as portas multimodais."""


class TextVisionAdapter:
    def observe(self, source: str) -> str:
        return source


class TextSpeechInputAdapter:
    def transcribe(self, audio_source: str) -> str:
        return audio_source


class TextSpeechOutputAdapter:
    def __init__(self):
        self.last_text = ""

    def synthesize(self, text: str) -> None:
        self.last_text = text
