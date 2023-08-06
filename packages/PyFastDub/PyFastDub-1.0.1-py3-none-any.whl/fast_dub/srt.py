from __future__ import annotations

import datetime
import json
import os
import re
import tempfile

import download_youtube_subtitle.main
from pytube import Caption

import fast_dub


class Line:
    __slots__ = ('ms', 'text', '_as_repr')

    class TimeLabel:
        __slots__ = ('start', 'duration', 'end', '_as_str')

        def __init__(self, start: float, end: float):
            self.duration = end - start
            self.start = start
            self.end = end
            self._as_str = f'<{start} --> {end}>'

        def __str__(self):
            return self._as_str

    def __init__(self, time_label: tuple[datetime.time, datetime.time], text: str):
        self.ms: Line.TimeLabel = self.TimeLabel(*
                                                 [(label.hour * 3600000)
                                                  + (label.minute * 60000)
                                                  + (label.second * 1000)
                                                  + (label.microsecond / 1000)
                                                  for label in time_label][:2]
                                                 )
        self.text: str = text
        self._as_repr = f'Line({self.ms}, {self.text!r})'

    def __repr__(self): return self._as_repr


def parse(text: str, skip_empty: bool = False) -> tuple[Line] | tuple:
    subtitles = ()
    for i in re.split(r'\n\n^\d+$\n', f'\n\n{text.lstrip()}', flags=re.M)[1:]:
        times, text = i.split('\n', 1)
        if not (text := text.strip()):
            continue
        # noinspection PyTypeChecker
        subtitles += Line(tuple(datetime.time(k.hour, k.minute, k.second, k.microsecond) for k in
                                [datetime.datetime.strptime(j, '%H:%M:%S,%f') for j in
                                 times.split(' --> ', 1)]), text),
    return tuple(line for line in subtitles if line.text.strip()) if skip_empty else subtitles


def from_json(json_: dict[str, dict[str, str]]) -> str:
    srt_s = ''
    for i, el in enumerate(json_['translation'], 1):
        # noinspection PyTypeChecker
        srt_s += (f'\n\n{i}\n{Caption.float_to_srt_time_format((start := int(el["start"])) / 1000.)}'
                  f' --> '
                  f'{Caption.float_to_srt_time_format((start + int(el["dur"])) / 1000.)}\n{el["text"]}')
    return srt_s[2:]


def download_srt(videoid: str, lang: str):
    tmp_dir = tempfile.TemporaryDirectory()
    target_json = os.path.join(tmp_dir.name, 'target.json')
    download_youtube_subtitle.main.main(videoid, lang, output_file=target_json, to_json=True)
    with open(target_json, encoding='UTF-8') as f:
        _json: dict[str, dict] = json.load(f)
    tmp_dir.cleanup()

    with open('target.srt', 'w', encoding='UTF-8') as srt_f:
        srt_f.write(fast_dub.srt.from_json(_json))
