# app/gui.py
import customtkinter as ctk
import tkinter as tk
import threading
import time
import io
import urllib.request
from typing import Dict, Any, List, Optional, cast
from app.player_engine import PlayerEngine
from utils.helpers import USER_AGENT, BASE_PATH, MUSIC_PATH, VIDEO_PATH
from utils.logger import get_logger

logger = get_logger(__name__)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

THUMB_W, THUMB_H = 120, 68  # tamaño miniatura en feed
PLAYER_THUMB_W, PLAYER_THUMB_H = 640, 360  # miniatura en reproductor


def _fetch_image(url: str, width: int, height: int) -> Optional[tk.PhotoImage]:
    """Descarga imagen y la devuelve como PhotoImage escalada."""
    try:
        from PIL import Image, ImageTk
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = resp.read()
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img = img.resize((width, height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class YouTubePwnedGUI(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("YouTube-PWNED")
        self.geometry("1280x800")
        self.minsize(960, 640)

        self.current_video_data: Dict[str, str] = {}
        self.engine: Optional[PlayerEngine] = None
        self.sponsor_segments: List[Any] = []
        self._thumb_cache: Dict[str, Any] = {}   # cache de PhotoImage por video_id
        self._player_thumb_ref = None              # evitar GC de imagen del reproductor

        self.setup_ui()
        self.after(150, self._init_engine)

    # ──────────────────────────────────────────────
    # INIT ENGINE
    # ──────────────────────────────────────────────
    def _init_engine(self):
        try:
            wid = self.vlc_frame.winfo_id()
            if wid:
                self.engine = PlayerEngine(wid)
                logger.info("PlayerEngine inicializado: wid=%s", wid)
                self._poll_playback()
                self.after(300, self.load_trending)
            else:
                self.after(100, self._init_engine)
        except Exception as e:
            logger.exception("Error inicializando engine: %s", e)
            self.after(500, self._init_engine)

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────
    def setup_ui(self):
        # ── Topbar ──
        topbar = ctk.CTkFrame(self, height=52, fg_color="#0a0a0a", corner_radius=0)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        ctk.CTkLabel(topbar, text="▶  YT-PWNED",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#ff3333").pack(side="left", padx=14)

        self.search_entry = ctk.CTkEntry(topbar, placeholder_text="Buscar en YouTube...",
                                          width=400, height=34)
        self.search_entry.pack(side="left", padx=6, pady=9)
        self.search_entry.bind("<Return>", lambda e: self.search_videos())

        ctk.CTkButton(topbar, text="Buscar", width=80, height=34,
                       command=self.search_videos).pack(side="left", padx=3)

        ctk.CTkButton(topbar, text="🔥 Trending", width=100, height=34,
                       fg_color="#1e1e1e", hover_color="#2e2e2e",
                       command=self.load_trending).pack(side="left", padx=3)

        self.status_label = ctk.CTkLabel(topbar, text="Iniciando...",
                                          text_color="#666",
                                          font=ctk.CTkFont(size=11))
        self.status_label.pack(side="right", padx=14)

        # ── Cuerpo principal ──
        body = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        body.pack(fill="both", expand=True)

        # ── Panel izquierdo: reproductor ──
        left = ctk.CTkFrame(body, fg_color="#0f0f0f", corner_radius=0)
        left.pack(side="left", fill="both", expand=True)

        # Título
        self.video_title_label = ctk.CTkLabel(
            left, text="Selecciona un video",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#bbb", anchor="w", wraplength=680
        )
        self.video_title_label.pack(fill="x", padx=12, pady=(8, 2))

        # Frame del reproductor VLC (con canvas para la thumbnail de carga)
        player_container = ctk.CTkFrame(left, fg_color="black", corner_radius=6)
        player_container.pack(fill="both", expand=True, padx=12, pady=(0, 4))

        # Canvas para thumbnail de "cargando"
        self.thumb_canvas = tk.Canvas(player_container, bg="black",
                                       highlightthickness=0)
        self.thumb_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Frame VLC encima del canvas (se vuelve opaco cuando hay video)
        self.vlc_frame = ctk.CTkFrame(player_container, fg_color="black",
                                       corner_radius=0)
        self.vlc_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Controles
        ctrl = ctk.CTkFrame(left, fg_color="#181818", height=48, corner_radius=0)
        ctrl.pack(fill="x", padx=12, pady=(0, 2))
        ctrl.pack_propagate(False)

        self.btn_play_pause = ctk.CTkButton(ctrl, text="▶", width=42, height=34,
                                             command=self.toggle_playback)
        self.btn_play_pause.pack(side="left", padx=6, pady=7)

        self.btn_stop = ctk.CTkButton(ctrl, text="⏹", width=42, height=34,
                                       fg_color="#2a2a2a", hover_color="#3a3a3a",
                                       command=self.stop_playback)
        self.btn_stop.pack(side="left", padx=2)

        self.time_label = ctk.CTkLabel(ctrl, text="00:00 / 00:00",
                                        font=ctk.CTkFont(size=11), width=100)
        self.time_label.pack(side="left", padx=8)

        self.progress = ctk.CTkSlider(ctrl, from_=0, to=100,
                                       command=self.seek_video)
        self.progress.set(0)
        self.progress.pack(side="left", fill="x", expand=True, padx=6)

        ctk.CTkLabel(ctrl, text="🔊", font=ctk.CTkFont(size=12)).pack(side="left")
        self.volume_slider = ctk.CTkSlider(ctrl, from_=0, to=100, width=80,
                                            command=self.set_volume)
        self.volume_slider.set(80)
        self.volume_slider.pack(side="left", padx=(2, 10))

        # Barra de descarga
        dl_bar = ctk.CTkFrame(left, fg_color="#111", height=44, corner_radius=0)
        dl_bar.pack(fill="x", padx=12, pady=(0, 8))
        dl_bar.pack_propagate(False)

        self.btn_dl_mp3 = ctk.CTkButton(dl_bar, text="⬇ MP3", width=110, height=32,
                                          fg_color="#1db954", hover_color="#17a349",
                                          state="disabled", command=self.download_mp3)
        self.btn_dl_mp3.pack(side="left", padx=8, pady=6)

        self.btn_dl_video = ctk.CTkButton(dl_bar, text="⬇ MP4", width=110, height=32,
                                           fg_color="#1565c0", hover_color="#0d47a1",
                                           state="disabled", command=self.download_video)
        self.btn_dl_video.pack(side="left", padx=4)

        self.dl_status = ctk.CTkLabel(dl_bar, text="", text_color="#888",
                                       font=ctk.CTkFont(size=11))
        self.dl_status.pack(side="left", padx=10)

        # ── Panel derecho: feed ──
        right = ctk.CTkFrame(body, width=320, fg_color="#111", corner_radius=0)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Videos",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#ccc").pack(pady=(10, 2), padx=10, anchor="w")

        self.results_frame = ctk.CTkScrollableFrame(right, fg_color="transparent",
                                                     corner_radius=0)
        self.results_frame.pack(fill="both", expand=True, padx=4, pady=(0, 6))
        self._show_placeholder("Cargando...")

    # ──────────────────────────────────────────────
    # FEED
    # ──────────────────────────────────────────────
    def _show_placeholder(self, msg: str):
        for w in self.results_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.results_frame, text=msg, text_color="#555").pack(pady=24)

    def clear_results(self):
        for w in self.results_frame.winfo_children():
            w.destroy()

    def add_result_card(self, video: Dict[str, Any]):
        v_id = video.get('id')
        if not v_id:
            return
        title = video.get('title') or 'Sin título'
        duration = video.get('duration')
        dur_str = ""
        if duration:
            try:
                m, s = divmod(int(duration), 60)
                h, m2 = divmod(m, 60)
                dur_str = f"{h}:{m2:02d}:{s:02d}" if h else f"{m}:{s:02d}"
            except Exception:
                pass

        card = ctk.CTkFrame(self.results_frame, fg_color="#1a1a1a", corner_radius=8)
        card.pack(fill="x", pady=3, padx=4)

        # Fila con miniatura + info
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=6)

        # Miniatura
        thumb_label = ctk.CTkLabel(row, text="", width=THUMB_W, height=THUMB_H,
                                    fg_color="#222", corner_radius=4)
        thumb_label.pack(side="left", padx=(0, 8))

        # Cargar miniatura en background
        thumb_url = f"https://i.ytimg.com/vi/{v_id}/mqdefault.jpg"
        threading.Thread(
            target=self._load_thumb_card,
            args=(v_id, thumb_url, thumb_label),
            daemon=True
        ).start()

        # Info
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(info, text=title[:55] + ("…" if len(title) > 55 else ""),
                     anchor="nw", wraplength=160,
                     font=ctk.CTkFont(size=11),
                     justify="left").pack(anchor="nw")

        bottom = ctk.CTkFrame(info, fg_color="transparent")
        bottom.pack(fill="x", anchor="sw", pady=(4, 0))

        if dur_str:
            ctk.CTkLabel(bottom, text=dur_str, text_color="#666",
                          font=ctk.CTkFont(size=10)).pack(side="left")

        ctk.CTkButton(bottom, text="▶", width=32, height=26,
                       command=lambda: self.play_video(v_id, title)).pack(side="right")

    def _load_thumb_card(self, video_id: str, url: str, label: ctk.CTkLabel):
        """Descarga miniatura y la aplica al label del card."""
        if video_id in self._thumb_cache:
            img = self._thumb_cache[video_id]
        else:
            img = _fetch_image(url, THUMB_W, THUMB_H)
            if img:
                self._thumb_cache[video_id] = img

        if img:
            try:
                self.after(0, lambda: label.configure(image=img, text=""))
            except Exception:
                pass

    # ──────────────────────────────────────────────
    # THUMBNAIL EN REPRODUCTOR
    # ──────────────────────────────────────────────
    def _show_player_thumbnail(self, video_id: str):
        """Muestra la miniatura del video en el canvas del reproductor."""
        url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"

        def _load():
            img = _fetch_image(url, PLAYER_THUMB_W, PLAYER_THUMB_H)
            if img:
                def _draw():
                    try:
                        self._player_thumb_ref = img
                        self.thumb_canvas.delete("all")
                        w = self.thumb_canvas.winfo_width() or PLAYER_THUMB_W
                        h = self.thumb_canvas.winfo_height() or PLAYER_THUMB_H
                        self.thumb_canvas.create_image(w // 2, h // 2,
                                                        anchor="center", image=img)
                        # Texto "Cargando..."
                        self.thumb_canvas.create_text(
                            w // 2, h // 2 + 50,
                            text="⏳ Cargando stream...",
                            fill="#aaa", font=("Arial", 13)
                        )
                        # Ocultar VLC frame hasta que haya video
                        self.vlc_frame.lower(self.thumb_canvas)
                    except Exception:
                        pass
                self.after(0, _draw)

        threading.Thread(target=_load, daemon=True).start()

    def _hide_player_thumbnail(self):
        """Tapa el canvas con el frame VLC."""
        try:
            self.vlc_frame.lift(self.thumb_canvas)
        except Exception:
            pass

    # ──────────────────────────────────────────────
    # TRENDING / SEARCH
    # ──────────────────────────────────────────────
    def load_trending(self):
        self._set_status("Cargando trending...", "orange")
        self._show_placeholder("Cargando...")
        threading.Thread(target=self._fetch_trending, daemon=True).start()

    def _fetch_trending(self):
        try:
            import yt_dlp
            opts: Dict[str, Any] = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'playlistend': 20,
                'http_headers': {'User-Agent': USER_AGENT},
            }
            entries = []
            with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                for url in [
                    "https://www.youtube.com/feed/trending?bp=4gINGgt5dG1hX2NoYXJ0cw%3D%3D",
                    "https://www.youtube.com/feed/trending",
                ]:
                    try:
                        info = ydl.extract_info(url, download=False)
                        if isinstance(info, dict) and info.get('entries'):
                            entries = [e for e in info['entries'] if e and e.get('id')]
                            if entries:
                                break
                    except Exception:
                        continue

                if not entries:
                    info = ydl.extract_info("ytsearch15:trending 2026", download=False)
                    if isinstance(info, dict):
                        entries = [e for e in info.get('entries', []) if e and e.get('id')]

            self.after(0, self.clear_results)
            for e in entries[:20]:
                self.after(0, self.add_result_card, e)
            self.after(0, lambda: self._set_status(f"{len(entries)} videos", "green"))
            logger.info("Trending: %d entradas", len(entries))
        except Exception as e:
            logger.exception("Error trending: %s", e)
            self.after(0, lambda: self._set_status("Error cargando trending", "red"))

    def search_videos(self):
        query = self.search_entry.get().strip()
        if not query:
            return
        self._set_status("Buscando...", "orange")
        self.clear_results()
        threading.Thread(target=self._fetch_search, args=(query,), daemon=True).start()

    def _fetch_search(self, query: str):
        try:
            import yt_dlp
            opts: Dict[str, Any] = {
                'quiet': True,
                'extract_flat': True,
                'skip_download': True,
                'http_headers': {'User-Agent': USER_AGENT},
            }
            with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                q = f"ytsearch15:{query}" if not query.startswith("http") else query
                info = ydl.extract_info(q, download=False)
                entries = [e for e in (info.get('entries', []) if isinstance(info, dict) else [])
                           if e and e.get('id')]

            self.after(0, self.clear_results)
            for e in entries:
                self.after(0, self.add_result_card, e)
            self.after(0, lambda: self._set_status(f"{len(entries)} resultados", "green"))
            logger.info("Búsqueda '%s': %d", query, len(entries))
        except Exception as e:
            logger.exception("Búsqueda error: %s", e)
            self.after(0, lambda: self._set_status("Error en búsqueda", "red"))

    # ──────────────────────────────────────────────
    # PLAYBACK
    # ──────────────────────────────────────────────
    def play_video(self, video_id: str, title: str):
        clean_id = video_id.split('&')[0].split('?')[0]
        self.current_video_data = {'id': clean_id, 'title': title}
        self.video_title_label.configure(text=title, text_color="white")
        self._set_status("Obteniendo stream...", "orange")
        self.btn_dl_mp3.configure(state="disabled")
        self.btn_dl_video.configure(state="disabled")
        self.btn_play_pause.configure(text="⏳")
        self._show_player_thumbnail(clean_id)
        threading.Thread(target=self._play_task, args=(clean_id,), daemon=True).start()

    def _play_task(self, video_id: str):
        try:
            for _ in range(60):
                if self.engine:
                    break
                time.sleep(0.1)

            engine = self.engine
            if not engine:
                self.after(0, lambda: self._set_status("Engine no listo", "red"))
                return

            stream = engine.get_stream_url(f"https://www.youtube.com/watch?v={video_id}")
            if stream:
                self.after(0, lambda: engine.play(stream))
                self.after(0, self._hide_player_thumbnail)
                self.after(0, lambda: self.btn_dl_mp3.configure(state="normal"))
                self.after(0, lambda: self.btn_dl_video.configure(state="normal"))
                self.after(0, lambda: self._set_status("▶ Reproduciendo", "green"))
                self.after(0, lambda: self.btn_play_pause.configure(text="⏸"))
                threading.Thread(target=self._fetch_sponsors,
                                  args=(video_id,), daemon=True).start()
                logger.info("Reproduciendo %s", video_id)
            else:
                self.after(0, lambda: self._set_status("No se pudo obtener stream", "red"))
                self.after(0, lambda: self.btn_play_pause.configure(text="▶"))
        except Exception as e:
            logger.exception("_play_task error: %s", e)
            self.after(0, lambda: self._set_status("Error de reproducción", "red"))
            self.after(0, lambda: self.btn_play_pause.configure(text="▶"))

    def toggle_playback(self):
        engine = self.engine
        if not engine:
            return
        try:
            if engine.is_playing():
                engine.player.pause()
                self.btn_play_pause.configure(text="▶")
            else:
                engine.player.play()
                self.btn_play_pause.configure(text="⏸")
        except Exception:
            logger.exception("toggle_playback error")

    def stop_playback(self):
        engine = self.engine
        if not engine:
            return
        try:
            engine.stop()
            self.btn_play_pause.configure(text="▶")
            self.progress.set(0)
            self.time_label.configure(text="00:00 / 00:00")
        except Exception:
            pass

    def seek_video(self, value: float):
        engine = self.engine
        if not engine:
            return
        try:
            length = engine.player.get_length()
            if length > 0:
                engine.player.set_time(int((value / 100) * length))
        except Exception:
            pass

    def set_volume(self, value: float):
        engine = self.engine
        if not engine:
            return
        try:
            engine.player.audio_set_volume(int(value))
        except Exception:
            pass

    # ──────────────────────────────────────────────
    # PLAYBACK POLL
    # ──────────────────────────────────────────────
    def _poll_playback(self):
        try:
            engine = self.engine
            if engine:
                length = engine.player.get_length()
                current = engine.player.get_time()

                if length and length > 0 and current is not None and current >= 0:
                    self.progress.set(min((current / length) * 100, 100))
                    curr_s = time.strftime('%M:%S', time.gmtime(max(0, current // 1000)))
                    tot_s = time.strftime('%M:%S', time.gmtime(max(0, length // 1000)))
                    self.time_label.configure(text=f"{curr_s} / {tot_s}")

                playing = engine.is_playing()
                btn_txt = self.btn_play_pause.cget("text")
                if playing and btn_txt == "▶":
                    self.btn_play_pause.configure(text="⏸")
                elif not playing and btn_txt == "⏸" and length and length > 0:
                    self.btn_play_pause.configure(text="▶")

                # SponsorBlock
                if current and length and length > 0:
                    curr_sec = current / 1000
                    for seg in self.sponsor_segments:
                        s, e = seg.get('segment', (None, None))
                        if s is not None and e is not None and s <= curr_sec <= e:
                            engine.player.set_time(int(e * 1000))
                            self._set_status("⏭ Sponsor saltado", "cyan")
        except Exception:
            pass
        finally:
            self.after(800, self._poll_playback)

    # ──────────────────────────────────────────────
    # SPONSORS
    # ──────────────────────────────────────────────
    def _fetch_sponsors(self, video_id: str):
        engine = self.engine
        if not engine:
            return
        self.sponsor_segments = engine.fetch_sponsors(video_id)

    # ──────────────────────────────────────────────
    # DOWNLOADS
    # ──────────────────────────────────────────────
    def download_mp3(self):
        if not self.current_video_data:
            return
        url = f"https://www.youtube.com/watch?v={self.current_video_data['id']}"
        self.dl_status.configure(text="Descargando MP3...", text_color="orange")
        self.btn_dl_mp3.configure(state="disabled")
        threading.Thread(target=self._dl_task, args=(url, "mp3"), daemon=True).start()

    def download_video(self):
        if not self.current_video_data:
            return
        url = f"https://www.youtube.com/watch?v={self.current_video_data['id']}"
        self.dl_status.configure(text="Descargando MP4...", text_color="orange")
        self.btn_dl_video.configure(state="disabled")
        threading.Thread(target=self._dl_task, args=(url, "video"), daemon=True).start()

    def _dl_task(self, url: str, mode: str):
        try:
            engine = self.engine
            if engine is None:
                engine = PlayerEngine(None)
            if mode == "mp3":
                engine.download_mp3(url)
                msg = f"✅ MP3 guardado en Música/YouTube-PWNED"
                self.after(0, lambda: self.btn_dl_mp3.configure(state="normal"))
            else:
                engine.download_video(url)
                msg = f"✅ MP4 guardado en Vídeos/YouTube-PWNED"
                self.after(0, lambda: self.btn_dl_video.configure(state="normal"))
            self.after(0, lambda: self.dl_status.configure(text=msg, text_color="green"))
            logger.info("Descarga %s OK: %s", mode, url)
        except Exception as e:
            logger.exception("Descarga %s error: %s", mode, e)
            self.after(0, lambda: self.dl_status.configure(
                text=f"❌ Error: {str(e)[:60]}", text_color="red"))
            if mode == "mp3":
                self.after(0, lambda: self.btn_dl_mp3.configure(state="normal"))
            else:
                self.after(0, lambda: self.btn_dl_video.configure(state="normal"))

    # ──────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────
    def _set_status(self, text: str, color: str = "gray"):
        try:
            self.status_label.configure(text=text, text_color=color)
        except Exception:
            pass


if __name__ == "__main__":
    app = YouTubePwnedGUI()
    app.mainloop()