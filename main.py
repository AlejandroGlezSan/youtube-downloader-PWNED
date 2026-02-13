from utils.logger import get_logger
logger = get_logger(__name__)

from app.gui import YouTubePwnedGUI

if __name__ == "__main__":
    logger.info("Arrancando YouTube-PWNED GUI")
    app = YouTubePwnedGUI()
    app.mainloop()
    logger.info("Aplicación cerrada")
