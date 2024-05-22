import logging
import os
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv()


# Environment variables set up
class Settings:
    TEL_TOKEN = os.getenv("TEL_TOKEN")
    DEBUG = os.getenv("DEBUG") == "True"
    ADMIN_ID = int(os.environ.get("ADMIN_ID"))
    INSPECT_ID = int(os.environ.get("INSPECT_ID"))
    CHAT_ALERT = int(os.environ.get("CHAT_ALERT", 12345))
    YA_ID = os.environ.get("YA_ID")
    API_LOGIN = os.environ.get("API_LOGIN")
    API_PAS = os.environ.get("API_PAS")
    START_WORLD = "факульт"
    REDUCT_WORLD = "минус"
    NUM_MESSAGES = 50
    FACULTY = {
        "мобил": "Мобилпафф",
        "фулст": "Фулстекслей",
        "фронд": "Фрондерин",
        "фронт": "Фрондерин",
        "бекен": "Бекендор",
        "геймд": "Геймдевран",
        "аналит": "Датааналирин",
        "дизай": "Дизайндей",
        "продж": "Проджектеран",
        "тесте": "Тестендор",
        "девоп": "Девопслей",
    }


settings = Settings()

# Logs configuration
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RotatingFileHandler("db/all.log", maxBytes=5000000, backupCount=5)
    ],
    format="%(asctime)s %(levelname)s - %(module)s:%(lineno)d"
    " (%(funcName)s) - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
)

formatter = logging.Formatter(
    "%(asctime)s %(levelname)s - %(module)s:%(lineno)d"
    " (%(funcName)s) - %(message)s",
    datefmt="%d-%b-%Y %H:%M:%S",
)

# Custom logger for adjusted events
logger = logging.getLogger("Warning_logger")
warning_handler = logging.FileHandler("db/custom.log")
logger.setLevel(logging.DEBUG)
logger.addHandler(warning_handler)
warning_handler.setFormatter(formatter)
