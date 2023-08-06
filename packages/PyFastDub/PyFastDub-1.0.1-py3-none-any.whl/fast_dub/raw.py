import argparse

import pyttsx3

from fast_dub import fast_dub

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-t', '--name', type=str,
                            help='Dir with <target>.mp4 and <target>.srt (<target>: -tn --target-name parameter)')
    arg_parser.add_argument('-v', '--voice', type=str, help='Voice (-vl --voices)')
    arg_parser.add_argument('-vl', '--voices', action='store_true', help='Show all voices and exit')
    arg_parser.add_argument('-tn', '--target-name', type=str, help='Targets nick')
    arg_parser.add_argument('-wo-v', '--without-video', action='store_false', dest='with_video',
                            help='Dub only subtitles without overlaying them on the video')
    arg_parser.add_argument('-vd', '--volume-down', type=int, help='volume down level')
    args: argparse.Namespace = arg_parser.parse_args()
    if args.voices:
        print('\n'.join(str(v) for v in pyttsx3.init().getProperty('voices')))
        raise SystemExit(0)
    fast_dub(args.name or input('Имя папки: '), args.voice or input('Голос: '),
             args.target_name or (input('Имя целевых файлов (.mp4 и .srt) (target): ') or 'target'),
             args.volume_down or (int(input('Уменьшить громкость видео на (25): ').strip() or 20)),
             args.with_video or (input('С видео [Y,N]? (Y) ').strip().upper() or 'Y') == 'Y')
