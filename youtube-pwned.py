#!/usr/bin/env python3
import sys
from utils.logger import get_logger
logger = get_logger(__name__)

try:
    from app.gui import YouTubePwnedGUI
except Exception as e:
    logger.exception("No se pudo importar YouTubePwnedGUI desde app.gui: %s", e)
    YouTubePwnedGUI = None

def main():
    logger.info("Launcher iniciado")
    if YouTubePwnedGUI is None:
        print("Error: No se encontró la clase YouTubePwnedGUI en app.gui.")
        sys.exit(1)
    try:
        app = YouTubePwnedGUI()
        app.mainloop()
    except Exception as e:
        logger.exception("Error al ejecutar la aplicación: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
