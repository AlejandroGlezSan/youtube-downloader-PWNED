import os
from pathlib import Path

# Rutas globales
BASE_PATH = Path.home() / "Downloads" / "YouTube_PWNED"
BASE_PATH.mkdir(parents=True, exist_ok=True)
FAV_FILE = BASE_PATH / "favorites.json"

# Constantes de configuración
VLC_ARGS = "--no-xlib --quiet --no-lua --network-caching=3000"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"