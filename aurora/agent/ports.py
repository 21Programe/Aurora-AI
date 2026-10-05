"""Portas para percepção e fala, sem acoplamento a provedores."""
from typing import Protocol


class VisionPort(Protocol):
    def observe(self, source: str) -> str: ...


class SpeechInputPort(Protocol):
    def transcribe(self, audio_source: str) -> str: ...


class SpeechOutputPort(Protocol):
    def synthesize(self, text: str) -> None: ...
