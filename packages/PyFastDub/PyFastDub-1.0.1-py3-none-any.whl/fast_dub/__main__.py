import argparse
import os.path
import re
import string
import typing
import urllib.parse

import pafy
import pafy.g
from pafy.backend_youtube_dl import YtdlPafy

import fast_dub

API_KEYS = {pafy.g.api_key, 'AIzaSyCHxJ84-ryessLJfWZVWldiuVCnxtf0Nm4'}
_API_RET_TYPE = typing.TypeVar('_API_RET_TYPE')
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-url', '--yt-url', type=str)
arg_parser.add_argument('-l', '--lang', type=str)
arg_parser.add_argument('-v', '--voice', type=str)
arg_parser.add_argument('-vd', '--volume-down', type=int, default=15)
arg_parser.add_argument('-k', '--yt-api-key', type=str, default=pafy.g.api_key)
arg_parser.add_argument('--video-dir', type=str)
args: argparse.Namespace = arg_parser.parse_args()

videos_dir = args.video_dir or 'videos'
if os.path.dirname(__file__) == os.getcwd():
    videos_dir = os.path.join('..', videos_dir)
if not os.path.isdir(videos_dir): os.mkdir(videos_dir)
videos_dir = os.path.abspath(videos_dir)
print(f'Videos Directory: {videos_dir!r}')

any_punctuation = re.compile(r'[%s]' % '\\'.join(string.punctuation))


def bot(yt: YtdlPafy, lang: str = 'ru', voice: str = None, volume_down: int = 15, clean: bool = True):
    video_label: str = yt.title
    print(video_label.center(fast_dub._get_terminal_width(), '_'))
    video_label = any_punctuation.sub('_', video_label)
    if not os.path.isdir(video_label):
        os.mkdir(video_label)
    os.chdir(video_label)

    if not os.path.isfile('target.mp4'):
        def progress_callback(total: int, downloaded: float, ratio: float, rate: float, eta: float):
            print(end=f'\r[{round(ratio * 100., 2)}%] {round(downloaded):,}/{total:,}b. {round(rate, 1):,} kb/s: ETA'
                      f' {eta} '
                      f'sec.'.ljust(fast_dub._get_terminal_width()))

        try:
            with_api_key(lambda: yt.getbest('mp4').download('target.mp4', callback=progress_callback))
            print('\r'.ljust(fast_dub._get_terminal_width()))
        except OSError as e:
            print(f'{e}\nSkipping...\n')
            return
            # Save .srt file
    if not os.path.isfile('target.srt'):
        fast_dub.srt.download_srt(yt.videoid, lang)
    # ..

    fast_dub.fast_dub('.', voice, volume_down=volume_down)


def with_api_key(func: typing.Callable[[], _API_RET_TYPE]) -> _API_RET_TYPE:
    for key in API_KEYS:
        pafy.set_api_key(key)
        print(f'Trying API key: {api_key}')
        try:
            return func()
        except pafy.util.GdataError:
            continue


if __name__ == '__main__':
    yt_url = args.yt_url or input('Ссылка (YT) на видео / плейлист: ')
    lang = args.lang or input('Языковой код (ru): ').strip() or 'ru'
    voice = args.voice or input('Голос: ')
    volume_down = args.volume_down or int(input('Уменьшить громкость видео на (20): ').strip() or 15)
    api_key = args.yt_api_key

    if api_key is None: api_key = input(f"YouTube API Key ({','.join(API_KEYS)}): ").strip()
    API_KEYS = API_KEYS | {key.strip() for key in api_key.split(',')}

    if api_key: pafy.set_api_key(api_key)
    if urllib.parse.urlparse(yt_url).path == '/playlist':
        playlist = with_api_key(lambda: pafy.get_playlist2(yt_url))
        title: str = playlist.title
        print('Playlist:', title)
        title = os.path.join(videos_dir, title)
        if not os.path.isdir(title): os.mkdir(title)
        os.chdir(os.path.join(videos_dir, title))
        videos_dir = title
    else:
        playlist = with_api_key(lambda: (pafy.new(yt_url),))
    for yt_dl in playlist:
        os.chdir(videos_dir)
        bot(
            yt_dl,
            lang,
            voice,
            volume_down,
        )
