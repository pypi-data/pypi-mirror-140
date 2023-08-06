import pydub


class AudioSegment(pydub.AudioSegment):
    __slots__ = ('ms_duration',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ms_duration = self.duration_seconds * 1000.

    def append(self, seg, _=None):
        """pydub.AudioSegment. Without crossfade."""
        seg1, seg2 = AudioSegment._sync(self, seg)
        return seg1._spawn(seg1._data + seg2._data)

    def __add__(self, other):
        return (self.append(other) if isinstance(other, AudioSegment)
                else self.apply_gain(other))
