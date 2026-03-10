import platform
from pathlib import Path

# Carpetas del sistema según SO
_home = Path.home()

if platform.system() == "Windows":
    MUSIC_PATH = _home / "Music" / "YouTube-PWNED"
    VIDEO_PATH = _home / "Videos" / "YouTube-PWNED"
elif platform.system() == "Darwin":  # macOS
    MUSIC_PATH = _home / "Music" / "YouTube-PWNED"
    VIDEO_PATH = _home / "Movies" / "YouTube-PWNED"
else:  # Linux
    MUSIC_PATH = _home / "Music" / "YouTube-PWNED"
    VIDEO_PATH = _home / "Videos" / "YouTube-PWNED"

MUSIC_PATH.mkdir(parents=True, exist_ok=True)
VIDEO_PATH.mkdir(parents=True, exist_ok=True)

# BASE_PATH para logs y favoritos (neutral)
BASE_PATH = _home / "Documents" / "YouTube-PWNED"
BASE_PATH.mkdir(parents=True, exist_ok=True)

FAV_FILE = BASE_PATH / "favorites.json"

# VLC args
if platform.system() == "Linux":
    VLC_ARGS = "--no-xlib --quiet --no-lua --network-caching=3000"
else:
    VLC_ARGS = "--quiet --no-lua --network-caching=3000"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"