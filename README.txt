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