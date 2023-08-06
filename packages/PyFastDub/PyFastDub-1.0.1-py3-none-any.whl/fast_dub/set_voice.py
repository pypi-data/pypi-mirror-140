import pyttsx3

_voices = pyttsx3.init().getProperty('voices')
VOICES_NAMES = {i.name.lower(): i for i in _voices}
VOICES_ID = {i.id: i for i in _voices}


class UnknownVoice(Exception): pass


def set_voice(voice: str, engine: pyttsx3.Engine):
    voice_name = voice.lower()
    print(voice_name)
    voice_property = engine.getProperty('voice')
    voice = VOICES_NAMES.get(voice_name)
    if not voice: raise UnknownVoice(f'{voice_name} not in {str(tuple(VOICES_NAMES.keys()))}')
    if VOICES_ID.get(voice_property).name.lower() != voice_name:
        engine.setProperty('voice', voice.id)
