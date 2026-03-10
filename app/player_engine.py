# app/player_engine.py
import vlc
import yt_dlp
import requests
import os
import platform
import sys
import psutil
import time
from typing import Any, Dict, List, Optional, cast
from utils.helpers import VLC_ARGS, USER_AGENT, MUSIC_PATH, VIDEO_PATH
from utils.logger import get_logger

logger = get_logger(__name__)

_BASE_OPTS: Dict[str, Any] = {
    'quiet': True,
    'no_warnings': True,
    'noplaylist': True,
    'socket_timeout': 15,
    'http_headers': {'User-Agent': USER_AGENT},
    'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
}

STREAM_FORMAT = "18/22/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"


def _kill_ffmpeg_children():
    try:
        current = psutil.Process(os.getpid())
        for child in current.children(recursive=True):
            if 'ffmpeg' in child.name().lower():
                try:
                    child.terminate()
                    child.wait(timeout=3)
                except psutil.NoSuchProcess:
                    pass
                except psutil.TimeoutExpired:
                    child.kill()
                logger.info("Proceso ffmpeg zombie terminado: pid=%s", child.pid)
    except Exception as e:
        logger.debug("_kill_ffmpeg_children: %s", e)


class PlayerEngine:
    def __init__(self, window_id=None):
        args = VLC_ARGS.split() if isinstance(VLC_ARGS, str) else VLC_ARGS
        try:
            self.instance = vlc.Instance(args)
        except Exception:
            logger.exception("vlc.Instance con args falló.")
            self.instance = vlc.Instance()

        self.player = self.instance.media_player_new()

        if window_id:
            try:
                if platform.system() == "Windows":
                    self.player.set_hwnd(window_id)
                elif sys.platform == "darwin":
                    self.player.set_nsobject(window_id)
                else:
                    self.player.set_xwindow(window_id)
            except Exception as e:
                logger.exception("Error vinculando ventana VLC: %s", e)

    def get_stream_url(self, video_url: str) -> Optional[str]:
        opts = {**_BASE_OPTS, 'format': STREAM_FORMAT}
        try:
            with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    return None
                if isinstance(info, dict) and info.get('url'):
                    return info['url']
                formats = info.get('formats', []) if isinstance(info, dict) else []
                combined = [f for f in formats if f.get('url')
                            and f.get('vcodec', 'none') != 'none'
                            and f.get('acodec', 'none') != 'none']
                if combined:
                    return max(combined, key=lambda f: f.get('height') or 0)['url']
                for f in reversed(formats):
                    if f.get('url'):
                        return f['url']
                return None
        except Exception as e:
            logger.exception("get_stream_url error: %s", e)
            return None

    def play(self, stream_url: str) -> None:
        try:
            media = self.instance.media_new(stream_url)
            media.add_option(f":http-user-agent={USER_AGENT}")
            media.add_option(":network-caching=5000")
            self.player.set_media(media)
            self.player.play()
            logger.info("Reproduciendo stream")
        except Exception as e:
            logger.exception("play error: %s", e)

    def stop(self) -> None:
        try:
            self.player.stop()
        except Exception:
            pass

    def is_playing(self) -> bool:
        try:
            return bool(self.player.is_playing())
        except Exception:
            return False

    def download_mp3(self, url: str, quality: str = "192") -> None:
        opts: Dict[str, Any] = {
            **_BASE_OPTS,
            'quiet': False,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'outtmpl': os.path.join(str(MUSIC_PATH), '%(title)s.%(ext)s'),
        }
        try:
            with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                ydl.download([url])
            logger.info("Descarga MP3 completada → %s", MUSIC_PATH)
        finally:
            time.sleep(0.5)
            _kill_ffmpeg_children()

    def download_video(self, url: str) -> None:
        opts: Dict[str, Any] = {
            **_BASE_OPTS,
            'quiet': False,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(str(VIDEO_PATH), '%(title)s.%(ext)s'),
        }
        try:
            with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                ydl.download([url])
            logger.info("Descarga video completada → %s", VIDEO_PATH)
        finally:
            time.sleep(0.5)
            _kill_ffmpeg_children()

    def fetch_sponsors(self, video_id: str) -> List[Dict[str, Any]]:
        try:
            r = requests.get(
                f"https://sponsor.ajay.app/api/skipSegments?videoID={video_id}&category=sponsor",
                timeout=2
            )
            return r.json() if r.status_code == 200 else []
        except Exception:
            return []