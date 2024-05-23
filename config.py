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
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
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
    PROMPT = (
        "На основе следующих сообщений в чате подготовь краткое содержание "
        "разговора, перечислив темы, на которые общались активные пользователи"
        " и что было сказано ими. Лучше использовать косвенную речь, "
        "Например: Антон считает, что вакансий для джунов сейчас на рынке "
        "мало, но Алиса говорит, что зато процесс найма идет намного быстрее. "
        "Предыдущее предложение только пример, не надо вставлять его в краткое"
        " содержание. Это пример из каких примерно блоков оно должно состоять."
        " Составь краткое содержание в таком стиле исходя из сообщений ниже. "
        " Краткое содержание умещаться в 20-25 предложений на русском языке.\n"
        "Сообщения:\n"
    )


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
