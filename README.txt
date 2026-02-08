YouTube to MP3 Downloader 

Un script de Python sencillo y fiable para descargar vídeos de YouTube como archivos de audio MP3. Esta herramienta guarda automáticamente los archivos en una ubicación de fácil acceso en tu Escritorio.

## 🌟 Nuevas Funcionalidades: Listas de Reproducción

Ahora el script detecta automáticamente si la URL proporcionada es un vídeo individual o una **lista de reproducción (playlist)** completa.

* **Descarga en lote**: Procesa todos los vídeos de una lista con un solo enlace.
* **Orden inteligente**: Los archivos de las listas se enumeran automáticamente (ej. "01 - Título.mp3") para mantener el orden original de la lista.

✅ Características 

* 
**Interfaz Simple**: Solo pega la URL de YouTube y descarga.


* **Soporte de Listas**: Descarga álbumes o colecciones completas automáticamente.
* 
**Opciones de Calidad**: Elige entre 128kbps, 192kbps o 320kbps.


* 
**Ubicación Inteligente**: Guarda automáticamente en la carpeta `Desktop/YouTube_MP3`.


* 
**Buscador de Archivos**: Si los archivos se pierden, la búsqueda integrada ayuda a localizarlos.


* 
**Metadatos**: Preserva el título del vídeo, la miniatura y la información del artista.


* 
**Fiable**: Utiliza `yt-dlp`, una bifurcación de youtube-dl mantenida activamente.


## 🛠️ Instalación

### 1. Instalar Python

* Descárgalo de [python.org](https://python.org).
* Asegúrate de marcar **"Add Python to PATH"** durante la instalación.

### 2. Instalar Paquetes Requeridos

Abre la Terminal o Símbolo del sistema y ejecuta:

```bash
pip install yt-dlp
``` 

### 3. Instalar FFmpeg (Requerido para la conversión a MP3)
**Windows:**
1. Descarga desde [ffmpeg.org](https://ffmpeg.org/download.html).
2. [cite_start]Extrae en `C:\ffmpeg`[cite: 4].
3. Añade `C:\ffmpeg\bin` a tus variables de entorno (PATH).

**macOS/Linux:**
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

## 🚀 Uso

### Inicio Rápido
```bash
python youtube-downloader.py

```

### Proceso de Descarga

1. Ejecuta el script.
2. Introduce la URL de YouTube (Vídeo o Playlist) cuando se te solicite.
3. Elige la calidad de audio (se recomienda 192kbps).
4. Elige la ubicación de guardado (por defecto es `Desktop/YouTube_MP3`).


5. El MP3 se descarga automáticamente.


6. La carpeta se abre automáticamente al finalizar.

## ❓ Solución de Problemas

* **Error "Archivo no encontrado"**: El script crea una carpeta en tu Escritorio llamada `YouTube_MP3`. Revisa allí primero.


* 
**Error de FFmpeg**: El script necesita FFmpeg para convertir el audio a formato MP3. Asegúrate de que esté correctamente instalado en el PATH.


* 
**Error de Módulo**: Asegúrate de haber instalado los requisitos con `pip install yt-dlp`.



## ⚖️ Aviso Legal

* Usa esta herramienta con responsabilidad.
* Solo descarga contenido para el que tengas permiso.
* Respeta las leyes de derechos de autor.
* Herramienta para uso personal y educativo únicamente.
=======
# YouTube to MP3 Downloader

A simple, reliable Python script to download YouTube videos as MP3 audio files. This tool automatically saves files to an easy-to-find location on your Desktop.

## Features

- ✅ **Simple Interface**: Just paste a YouTube URL and download
- 🎵 **Quality Options**: Choose between 128kbps, 192kbps, or 320kbps MP3
- 📁 **Smart File Location**: Automatically saves to Desktop/YouTube_MP3 folder
- 🔍 **File Finder**: If files go missing, built-in search helps locate them
- 🖼️ **Metadata**: Preserves video title, thumbnail, and artist info
- 🎯 **Reliable**: Uses yt-dlp (actively maintained fork of youtube-dl)

## Installation

### 1. Install Python
- Download from [python.org](https://python.org)
- Make sure to check "Add Python to PATH" during installation

### 2. Install Required Packages
Open Command Prompt/Terminal and run:
```bash
pip install yt-dlp
```

### 3. Install FFmpeg (Required for MP3 conversion)

**Windows:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install ffmpeg
```

## Usage

### Quick Start
```bash
python youtube-downloader.py
```

### What Happens
1. Run the script
2. Enter YouTube URL when prompted
3. Choose audio quality (192kbps recommended)
4. Choose save location (default is Desktop/YouTube_MP3)
5. The MP3 downloads automatically
6. Folder opens automatically when done

### Example
```
Enter YouTube URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
Select quality (1-3) [2]: 2
Select location (1-3) [1]: 1

✅ SUCCESS! Downloaded:
📁 Rick Astley - Never Gonna Give You Up.mp3
📏 Size: 4.27 MB
📍 Location: C:\Users\YourName\Desktop\YouTube_MP3
```

## Troubleshooting

### "File not found" error
The script creates a folder on your Desktop called `YouTube_MP3`. Check there first.

### "Module not found" error
Make sure you installed the requirements:
```bash
pip install yt-dlp
```

### "FFmpeg not found" error
Install FFmpeg using instructions above. The script needs it to convert to MP3.

### Download fails
- Check your internet connection
- Make sure the YouTube URL is correct
- Try again - sometimes YouTube blocks temporary requests

## Legal Notice

⚠️ **Use Responsibly**
- Only download content you have permission to download
- Respect copyright laws
- This tool is for educational purposes and personal use only
- Do not download copyrighted content without authorization

## Support

If you encounter issues:
1. Make sure all requirements are installed
2. Check that FFmpeg is in your PATH
3. Try a different YouTube video
4. Restart the script

## Files Created

The script creates:
- `youtube-downloader.py` - Main program
- `YouTube_MP3` folder on Desktop - Where downloads are saved

No other files are needed - it's a single-file solution!
