import os
import sys
import tempfile

import pyttsx3
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

from fast_dub import srt
from fast_dub.audio_speed import speed_change
from fast_dub.pydub_overlay import AudioSegment
from fast_dub.set_voice import set_voice

ENGINE = pyttsx3.init()


def _get_terminal_width() -> int:
    try:
        columns = os.get_terminal_size(sys.stdout.fileno()).columns
    except (AttributeError, ValueError, OSError):
        columns = 0
    return columns


# noinspection PyUnboundLocalVariable
def fast_dub(name: str, voice: str = None, target_name: str = 'target',
             volume_down: int = 15, with_video: bool = True) -> None:
    ret_to_cwd = os.getcwd()
    name = os.path.abspath(name)
    os.chdir(name)
    tmp_dir = tempfile.TemporaryDirectory()
    tmp = tmp_dir.name
    target_out_video = f'{target_name}.mp4'
    target_out_audio = f'{target_name}.mp3'

    result_out_audio = os.path.join('result', target_out_audio)
    result_out_video = os.path.join('result', target_out_video)

    target_out_audio = os.path.join(tmp, target_out_audio)

    if with_video and os.path.isfile(result_out_video) or os.path.isfile(result_out_audio) and not with_video:
        print('Exist. Skipping...')
        return
    tmp_file = os.path.join(tmp, f'one_{target_name}.mp3')

    # Set voice
    if voice: set_voice(voice, ENGINE)
    # ..

    # Srt file parsing
    with open(f'{target_name}.srt', encoding='UTF-8') as f:
        text = f.read()
    subtitles = srt.parse(text)
    # ..

    len_subtitles_end = len(subtitles)

    # Subtitle dubbing
    audio = AudioSegment.silent(subtitles[0].ms.start)
    len_subtitles_end = len(subtitles)

    # Subtitle dubbing
    for i, it_line in tqdm(enumerate(subtitles, 1), total=len_subtitles_end, unit='line', dynamic_ncols=True):
        is_not_last = i != len_subtitles_end
        if is_not_last: audio_dur = (next_start := subtitles[i].ms.start) - it_line.ms.start
        text: str = it_line.text.strip()
        if text:
            text_lines = text.splitlines()
            if (first_line := text_lines[0]).startswith('!:'):
                set_voice(first_line[2:], ENGINE)
                text = '\n'.join(text_lines[1:])
            ENGINE.save_to_file(text, tmp_file)
            ENGINE.runAndWait()
            dubed = AudioSegment.from_file(tmp_file)
        else:
            dubed = AudioSegment.silent(audio_dur)

        duration = it_line.ms.duration
        left_border = it_line.ms.start - audio.ms_duration
        right_border = (next_start - it_line.ms.end) if is_not_last else 0.
        free = (left_border
                + duration
                + right_border)

        dubed_ms = dubed.ms_duration
        if dubed_ms > free:
            dubed = speed_change(dubed, dubed_ms / free)
            dubed_ms = dubed.ms_duration

        audio = audio.append(AudioSegment.silent((free - dubed_ms) / 2. if (dubed_ms > (duration + right_border)) else
                                                 left_border)).append(dubed)
    # ..

    change_to = audio.ms_duration / subtitles[-1].ms.end
    print(f'Change audio speed to x{change_to}')
    audio = speed_change(audio, change_to)

    if not os.path.isdir('result'): os.mkdir('result')

    audio.export(result_out_audio)

    if with_video:
        video_clip = VideoFileClip(target_out_video)
        video_clip.audio.write_audiofile(target_out_audio)
        (AudioSegment.from_file(target_out_audio) - volume_down).export(target_out_audio)
        video_clip.audio = CompositeAudioClip((AudioFileClip(target_out_audio), AudioFileClip(result_out_audio)))
        video_clip.write_videofile(result_out_video)

    tmp_dir.cleanup()
    os.chdir(ret_to_cwd)
