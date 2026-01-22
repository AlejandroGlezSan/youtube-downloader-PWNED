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

---

**Enjoy your music! 🎵**