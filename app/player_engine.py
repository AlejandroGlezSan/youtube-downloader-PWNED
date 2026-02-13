# app/player_engine.py
import vlc
import yt_dlp
import requests
import os
import platform
import sys
import logging
from typing import Any, Dict, List, cast
from utils.helpers import VLC_ARGS, USER_AGENT, BASE_PATH
from utils.logger import get_logger

logger = get_logger(__name__)

class PlayerEngine:
    def __init__(self, window_id=None):
        args = VLC_ARGS.split() if isinstance(VLC_ARGS, str) else VLC_ARGS
        try:
            self.instance = vlc.Instance(args)
        except Exception:
            logger.exception("vlc.Instance con args falló, intentando sin args.")
            self.instance = vlc.Instance()

        self.player = self.instance.media_player_new()

        try:
            if window_id:
                if platform.system() == "Windows":
                    try:
                        self.player.set_hwnd(window_id)
                    except Exception:
                        logger.exception("set_hwnd falló")
                elif sys.platform == "darwin":
                    try:
                        self.player.set_nsobject(window_id)
                    except Exception:
                        logger.warning("set_nsobject no disponible")
                else:
                    try:
                        self.player.set_xwindow(window_id)
                    except Exception:
                        logger.warning("set_xwindow no disponible")
        except Exception as e:
            logger.exception("Error al vincular ventana VLC: %s", e)

    def get_stream_data(self, video_url: str, audio_only: bool = False) -> str | None:
        opts: Dict[str, Any] = {
            'format': 'bestaudio' if audio_only else 'best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True
        }
        try:
            # cast para satisfacer comprobadores de tipos que esperan el tipo interno de yt_dlp
            with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    logger.warning("yt_dlp no devolvió info para %s", video_url)
                    return None

                # Preferir info['url'] si existe
                if isinstance(info, dict) and info.get('url'):
                    return info['url']

                # Si hay formatos, elegir el mejor con url
                formats = (info.get('formats') if isinstance(info, dict) else None) or []
                if formats:
                    def _score(f: Dict[str, Any]) -> int:
                        return int(f.get('abr') or f.get('tbr') or f.get('height') or 0)
                    formats_sorted = sorted(formats, key=_score, reverse=True)
                    for f in formats_sorted:
                        if f.get('url'):
                            return f['url']

                logger.warning("No se encontró url de stream en info/formats para %s", video_url)
                return None
        except Exception as e:
            logger.exception("get_stream_data error: %s", e)
            return None

    def play(self, stream_url: str) -> None:
        try:
            media = self.instance.media_new(stream_url)
            media.add_option(f":http-user-agent={USER_AGENT}")
            try:
                media.add_option(":network-caching=3000")
            except Exception:
                pass
            self.player.set_media(media)
            self.player.play()
            logger.info("Reproduciendo stream")
        except Exception as e:
            logger.exception("Error al reproducir stream: %s", e)

    def download_mp3(self, url: str, quality: str = "192") -> None:
        opts: Dict[str, Any] = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': quality,
            }],
            'outtmpl': os.path.join(str(BASE_PATH), '%(title)s.%(ext)s'),
            'quiet': True
        }
        try:
            with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                ydl.download([url])
            logger.info("Descarga completada")
        except Exception as e:
            logger.exception("download_mp3 error: %s", e)

    def fetch_sponsors(self, video_id: str) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"https://sponsor.ajay.app/api/skipSegments?videoID={video_id}&category=sponsor", timeout=3)
            return r.json() if r.status_code == 200 else []
        except Exception:
            logger.exception("fetch_sponsors error")
            return []
