# app/gui.py
import customtkinter as ctk
import threading
import json
import time
from typing import Dict, Any, List, Optional, cast
from app.player_engine import PlayerEngine
from utils.helpers import FAV_FILE, USER_AGENT
from utils.logger import get_logger

logger = get_logger(__name__)

class YouTubePwnedGUI(ctk.CTk):
    # UI update loop (declarada antes para analizadores estáticos)
    def update_ui_playback(self) -> None:
        try:
            engine = self.engine
            if engine is not None:
                length = engine.player.get_length()
                current = engine.player.get_time()
                if length > 0 and current is not None:
                    percent = (current / length) * 100 if length > 0 else 0
                    try:
                        self.progress.set(percent)
                    except Exception:
                        pass
                    curr_str = time.strftime('%M:%S', time.gmtime(max(0, int(current // 1000))))
                    total_str = time.strftime('%M:%S', time.gmtime(max(0, int(length // 1000))))
                    self.time_label.configure(text=f"{curr_str} / {total_str}")

                    try:
                        curr_sec = current / 1000
                        for segment in getattr(self, "sponsor_segments", []):
                            s, e = segment.get('segment', (None, None))
                            if s is None or e is None:
                                continue
                            if s <= curr_sec <= e:
                                engine.player.set_time(int(e * 1000))
                                self.status_label.configure(text="Sponsor saltado", text_color="cyan")
                    except Exception:
                        logger.exception("Sponsor skip error")
        except Exception:
            logger.exception("update_ui_playback error")
        finally:
            try:
                self.after(1000, self.update_ui_playback)
            except Exception:
                pass

    def __init__(self):
        super().__init__()
        self.title("YouTube-PWNED Browser")
        self.geometry("1300x850")

        self.favorites: List[Dict[str, str]] = self.load_favorites()
        self.current_video_data: Dict[str, str] = {}
        self.engine: Optional[PlayerEngine] = None
        self.sponsor_segments: List[Any] = []

        self.setup_ui()

        def _init_engine():
            try:
                wid = self.vlc_frame.winfo_id()
                if wid:
                    self.engine = PlayerEngine(wid)
                    logger.info("PlayerEngine inicializado con window id: %s", wid)
                    self.after(1000, self.update_ui_playback)
                    self.after(1500, self.load_trending)
                else:
                    self.after(100, _init_engine)
            except Exception as e:
                logger.exception("Error inicializando PlayerEngine: %s", e)
                self.after(500, _init_engine)

        self.after(100, _init_engine)

    def load_favorites(self) -> List[Dict[str, str]]:
        if FAV_FILE.exists():
            try:
                with open(FAV_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                logger.exception("favorites.json corrupto o ilegible")
                return []
        return []

    def save_favorites(self) -> None:
        try:
            with open(FAV_FILE, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.exception("No se pudo guardar favorites.json")

    def setup_ui(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=300)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="YT-PWNED", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=12)

        self.entry = ctk.CTkEntry(self.sidebar, placeholder_text="Buscar videos o pegar URL...")
        self.entry.pack(padx=12, pady=(0,8), fill="x")
        self.entry.bind("<Return>", lambda e: self.search_videos())

        self.btn_search = ctk.CTkButton(self.sidebar, text="Buscar", command=self.search_videos)
        self.btn_search.pack(padx=12, pady=(0,12), fill="x")

        self.btn_download = ctk.CTkButton(self.sidebar, text="Descargar MP3", command=self.start_download, state="disabled", fg_color="#28a745")
        self.btn_download.pack(padx=12, pady=8, fill="x")

        ctk.CTkLabel(self.sidebar, text="Favoritos", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(10,4))
        self.fav_frame = ctk.CTkScrollableFrame(self.sidebar, height=220, fg_color="transparent")
        self.fav_frame.pack(padx=12, pady=(0,12), fill="both", expand=False)
        self.render_favorites()

        self.status_label = ctk.CTkLabel(self.sidebar, text="Listo", text_color="gray", wraplength=260)
        self.status_label.pack(side="bottom", pady=12, padx=12)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=12, pady=12)

        self.vlc_frame = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.vlc_frame.pack(fill="both", expand=True)

        ctrl = ctk.CTkFrame(self.main_frame)
        ctrl.pack(fill="x", pady=8)
        self.btn_play_pause = ctk.CTkButton(ctrl, text="▶", width=40, command=self.toggle_playback)
        self.btn_play_pause.pack(side="left", padx=6)
        self.progress = ctk.CTkSlider(ctrl, from_=0, to=100, command=self.seek_video)
        self.progress.pack(side="left", fill="x", expand=True, padx=6)
        self.time_label = ctk.CTkLabel(ctrl, text="00:00 / 00:00")
        self.time_label.pack(side="right", padx=6)

        self.results_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Resultados", height=220)
        self.results_frame.pack(fill="x", pady=(12,0))
        self.empty_label = ctk.CTkLabel(self.results_frame, text="Sin resultados", text_color="gray")
        self.empty_label.pack(pady=8)

    def render_favorites(self) -> None:
        for w in self.fav_frame.winfo_children():
            w.destroy()
        for fav in self.favorites:
            title = fav.get('title', '')[:36] + ("…" if len(fav.get('title','')) > 36 else "")
            row = ctk.CTkFrame(self.fav_frame)
            row.pack(fill="x", pady=2, padx=4)
            btn = ctk.CTkButton(row, text=title, fg_color="transparent", anchor="w", command=lambda f=fav: self.play_video(f['id'], f.get('title','')))
            btn.pack(side="left", fill="x", expand=True)
            del_btn = ctk.CTkButton(row, text="✖", width=30, fg_color="#e74c3c", command=lambda f=fav: self.remove_favorite(f['id']))
            del_btn.pack(side="right", padx=(6,0))

    def remove_favorite(self, video_id: str) -> None:
        self.favorites = [f for f in self.favorites if f.get('id') != video_id]
        self.save_favorites()
        self.render_favorites()

    def clear_results(self) -> None:
        for w in self.results_frame.winfo_children():
            w.destroy()
        self.empty_label = ctk.CTkLabel(self.results_frame, text="Sin resultados", text_color="gray")
        self.empty_label.pack(pady=8)

    def add_result_card(self, video: Dict[str, Any]) -> None:
        if getattr(self, "empty_label", None) and self.empty_label.winfo_exists():
            try:
                self.empty_label.pack_forget()
            except Exception:
                pass

        v_id = video.get('id')
        if not v_id:
            return
        title = video.get('title', 'Sin título')
        card = ctk.CTkFrame(self.results_frame)
        card.pack(fill="x", pady=4, padx=6)
        ctk.CTkLabel(card, text=title[:80], anchor="w").pack(side="left", padx=8, pady=6, fill="x", expand=True)
        ctk.CTkButton(card, text="▶ Ver", width=80, command=lambda: self.play_video(v_id, title)).pack(side="right", padx=8)

    def search_videos(self) -> None:
        query = self.entry.get().strip()
        logger.info("Search query: %s", query)
        if not query:
            return
        self.status_label.configure(text="Buscando...", text_color="orange")
        self.clear_results()

        def _search():
            try:
                import yt_dlp
                opts: Dict[str, Any] = {'quiet': True, 'extract_flat': True}
                with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                    q = f"ytsearch10:{query}" if not query.startswith("http") else query
                    info = ydl.extract_info(q, download=False)
                    entries: List[Any] = info.get('entries', []) if isinstance(info, dict) and info.get('entries') else (info if isinstance(info, list) else [])
                    for e in entries:
                        if e and e.get('id'):
                            self.after(0, self.add_result_card, e)
                self.after(0, lambda: self.status_label.configure(text="Búsqueda lista", text_color="green"))
                logger.info("Búsqueda completada para: %s (resultados: %d)", query, len(entries))
            except Exception as e:
                logger.exception("Error en búsqueda: %s", e)
                self.after(0, lambda: self.status_label.configure(text=f"Error en búsqueda: {e}", text_color="red"))

        threading.Thread(target=_search, daemon=True).start()

    def load_trending(self) -> None:
        logger.info("Cargando portada (trending)...")
        self.status_label.configure(text="Cargando portada...", text_color="orange")
        self.clear_results()

        def _trending():
            try:
                import yt_dlp
                opts: Dict[str, Any] = {
                    'quiet': True,
                    'extract_flat': False,
                    'noplaylist': False,
                    'geo_bypass': True,
                    'nocheckcertificate': True,
                    'http_headers': {'User-Agent': USER_AGENT},
                }
                url = "https://www.youtube.com/feed/trending"
                entries: List[Any] = []
                with yt_dlp.YoutubeDL(cast(dict, opts)) as ydl:
                    try:
                        info = ydl.extract_info(url, download=False)
                    except Exception as e:
                        logger.warning("yt_dlp trending direct failed: %s", e)
                        info = None

                    if isinstance(info, dict) and info.get('entries'):
                        entries = info.get('entries', [])
                    elif isinstance(info, list):
                        entries = info
                    else:
                        logger.info("Usando fallback ytsearch para trending")
                        try:
                            q = "ytsearch10:trending"
                            info2 = ydl.extract_info(q, download=False)
                            entries = info2.get('entries', []) if isinstance(info2, dict) and info2.get('entries') else (info2 if isinstance(info2, list) else [])
                        except Exception as e2:
                            logger.exception("Fallback ytsearch falló: %s", e2)
                            entries = []

                for e in entries:
                    if not e:
                        continue
                    vid = e.get('id') or e.get('url') or e.get('webpage_url')
                    title = e.get('title') or e.get('fulltitle') or ""
                    if vid:
                        self.after(0, self.add_result_card, {'id': vid, 'title': title})

                self.after(0, lambda: self.status_label.configure(text="Portada cargada", text_color="green"))
                logger.info("Portada cargada (resultados mostrados: %d)", len(entries))
            except Exception as e:
                logger.exception("Error cargando portada: %s", e)
                self.after(0, lambda: self.status_label.configure(text=f"Error portada: {e}", text_color="red"))

        threading.Thread(target=_trending, daemon=True).start()

    def play_video(self, video_id: str, title: str) -> None:
        clean_id = video_id.split('&')[0].split('?')[0]
        self.current_video_data = {'id': clean_id, 'title': title}
        self.status_label.configure(text="Obteniendo enlace...", text_color="orange")
        self.btn_download.configure(state="disabled")

        def _task():
            try:
                retries = 0
                while self.engine is None and retries < 50:
                    retries += 1
                    time.sleep(0.1)
                engine = self.engine
                if engine is None:
                    logger.error("Engine no inicializado")
                    self.after(0, lambda: self.status_label.configure(text="Engine no listo", text_color="red"))
                    return

                stream = engine.get_stream_data(f"https://www.youtube.com/watch?v={clean_id}")
                if stream:
                    self.after(0, lambda: engine.play(stream))
                    self.after(0, lambda: self.btn_download.configure(state="normal"))
                    self.after(0, lambda: self.status_label.configure(text="Reproduciendo", text_color="green"))
                    threading.Thread(target=self.fetch_sponsor_segments, args=(clean_id,), daemon=True).start()
                    logger.info("Reproduciendo video %s - %s", clean_id, title)
                else:
                    self.after(0, lambda: self.status_label.configure(text="No se obtuvo stream", text_color="red"))
                    logger.warning("No stream obtenido para %s", clean_id)
            except Exception as e:
                logger.exception("Error en play_video: %s", e)
                self.after(0, lambda: self.status_label.configure(text="Error reproducción", text_color="red"))

        threading.Thread(target=_task, daemon=True).start()

    def toggle_playback(self) -> None:
        try:
            engine = self.engine
            if engine is None:
                return
            if engine.player.is_playing():
                engine.player.pause()
                self.btn_play_pause.configure(text="▶")
            else:
                engine.player.play()
                self.btn_play_pause.configure(text="⏸")
        except Exception:
            logger.exception("toggle_playback error")

    def seek_video(self, value: float) -> None:
        try:
            engine = self.engine
            if engine is None:
                return
            length = engine.player.get_length()
            if length > 0:
                engine.player.set_time(int((value / 100) * length))
        except Exception:
            logger.exception("seek_video error")

    def fetch_sponsor_segments(self, video_id: str) -> None:
        try:
            import requests
            r = requests.get(f"https://sponsor.ajay.app/api/skipSegments?videoID={video_id}&category=sponsor", timeout=3)
            self.sponsor_segments = r.json() if r.status_code == 200 else []
            logger.info("Sponsor segments fetched: %d for %s", len(self.sponsor_segments), video_id)
        except Exception:
            self.sponsor_segments = []
            logger.exception("fetch_sponsor_segments error")

    def start_download(self) -> None:
        if not self.current_video_data:
            return
        self.status_label.configure(text="Descargando...", text_color="orange")
        url = f"https://www.youtube.com/watch?v={self.current_video_data['id']}"

        def _download_task():
            try:
                engine = self.engine
                if engine:
                    engine.download_mp3(url)
                else:
                    temp_engine = PlayerEngine(None)
                    temp_engine.download_mp3(url)
                self.after(0, lambda: self.status_label.configure(text="MP3 guardado", text_color="green"))
                logger.info("Descarga completada para %s", url)
            except Exception as e:
                logger.exception("Error en descarga: %s", e)
                self.after(0, lambda: self.status_label.configure(text="Error descarga", text_color="red"))

        threading.Thread(target=_download_task, daemon=True).start()

    def toggle_favorite(self) -> None:
        if not self.current_video_data:
            return
        v_id = self.current_video_data['id']
        if any(f.get('id') == v_id for f in self.favorites):
            self.favorites = [f for f in self.favorites if f.get('id') != v_id]
        else:
            self.favorites.append(self.current_video_data.copy())
        self.save_favorites()
        self.render_favorites()
        logger.info("Favorites updated (count=%d)", len(self.favorites))

if __name__ == "__main__":
    app = YouTubePwnedGUI()
    app.mainloop()
