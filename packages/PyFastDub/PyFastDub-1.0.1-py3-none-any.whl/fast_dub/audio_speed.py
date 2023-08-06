import copy
import os
import subprocess
import tempfile

from imageio_ffmpeg import get_ffmpeg_exe

from fast_dub.pydub_overlay import AudioSegment

FFMPEG_EXE = get_ffmpeg_exe()


def speed_change(audio: AudioSegment, speed_changes: float, allow_copy: bool = True, log_level: str = 'panic'
                 ) -> AudioSegment:
    if speed_changes == 1.: return audio if allow_copy else copy.copy(audio)

    atempo = []
    if speed_changes < .5:
        _n = speed_changes
        while _n < .5:
            atempo.append(.5)
            _n *= 2
        atempo.append(_n)
    elif speed_changes > 100.:
        _n = speed_changes
        while _n > 100.:
            atempo.append(100.)
            _n /= 2
        atempo.append(_n)
    else:
        atempo.append(speed_changes)

    with tempfile.TemporaryDirectory() as tmp:
        inp = os.path.join(tmp, 'inp.mp3')
        out = os.path.join(tmp, 'out.mp3')
        audio.export(inp)
        subprocess.check_call([FFMPEG_EXE, '-v', log_level, '-i', inp,
                               '-af', ','.join([f'atempo={i}' for i in atempo]),
                               out, '-y'])
        return AudioSegment.from_file(out)
