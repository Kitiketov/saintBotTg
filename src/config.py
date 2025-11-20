import logging

from src.settings.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    filename="py_log.log",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
)

settings = Settings()
logger = logging.getLogger("saintbot")
