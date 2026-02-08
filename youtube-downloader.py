#!/usr/bin/env python3
"""
YouTube to MP3 Downloader - Playlist Supported Version
"""

import os
import sys
import yt_dlp
from pathlib import Path
import platform

def get_default_download_path():
    """Get system-specific default download path"""
    system = platform.system()
    
    if system == "Windows":
        downloads = Path.home() / "Downloads"
    elif system == "Darwin":  # macOS
        downloads = Path.home() / "Downloads"
    else:  # Linux and others
        downloads = Path.home() / "Downloads"
    
    youtube_downloads = downloads / "YouTube_MP3"
    youtube_downloads.mkdir(exist_ok=True)
    return str(youtube_downloads)

def download_youtube_as_mp3(url, output_path=None, quality="192"):
    """
    Download YouTube video(s) or playlist as MP3
    """
    if output_path is None:
        output_path = get_default_download_path()
    
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    # Configuración de yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        # 'noplaylist': False permite descargar listas completas
        'noplaylist': False, 
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': quality,
        }],
        # Si es una lista, añade el índice al principio para mantener el orden
        'outtmpl': os.path.join(output_path, '%(playlist_index)s - %(title)s.%(ext)s' if 'list=' in url else '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
            }
        },
    }
    
    try:
        print(f"🔗 Procesando: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path
            
    except Exception as e:
        print(f"❌ Error en la descarga: {e}")
        return None

def simple_download():
    """Simple command-line download without menu"""
    print("=" * 60)
    print("YouTube to MP3 Downloader (Soporte para Listas)")
    print("=" * 60)
    
    try:
        import yt_dlp
    except ImportError:
        print("Por favor, instala yt-dlp: pip install yt-dlp")
        return
    
    url = input("\nIntroduce la URL (Video o Playlist): ").strip()
    if not url:
        return
    
    print("\nCalidad:")
    print("1. Alta (320kbps)")
    print("2. Media (192kbps) [Default]")
    print("3. Estándar (128kbps)")
    
    choice = input("Selecciona (1-3) [2]: ").strip()
    quality_map = {"1": "320", "2": "192", "3": "128"}
    quality = quality_map.get(choice, "192")
    
    print("\nUbicación:")
    print("1. Carpeta Downloads/YouTube_MP3")
    print("2. Directorio actual")
    
    loc_choice = input("Selecciona (1-2) [1]: ").strip()
    output_path = os.getcwd() if loc_choice == "2" else get_default_download_path()
    
    print(f"\n🚀 Iniciando descarga en: {output_path}...")
    result = download_youtube_as_mp3(url, output_path, quality)
    
    if result:
        print(f"\n🎉 ¡Proceso finalizado! Revisa la carpeta: {output_path}")
        # Abrir carpeta automáticamente
        try:
            if platform.system() == "Windows":
                os.startfile(output_path)
            elif platform.system() == "Darwin":
                os.system(f'open "{output_path}"')
        except:
            pass

if __name__ == "__main__":
    simple_download()
    input("\nPresiona Enter para salir...")