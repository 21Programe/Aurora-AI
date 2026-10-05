from aurora.agent.adapters import TextSpeechInputAdapter, TextSpeechOutputAdapter, TextVisionAdapter


def test_text_adapters_provide_replaceable_multimodal_ports():
    assert TextVisionAdapter().observe("frame") == "frame"
    assert TextSpeechInputAdapter().transcribe("audio-text") == "audio-text"
    output = TextSpeechOutputAdapter()
    output.synthesize("olá")
    assert output.last_text == "olá"
