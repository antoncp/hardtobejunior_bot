import os

import telebot
from dotenv import load_dotenv

from db import DataBase
from language_utilities import choose_noun_case

load_dotenv()
ADMIN_ID = os.environ.get("ADMIN_ID")
INSPECT_ID = os.environ.get("INSPECT_ID")
START_WORLD = "факульт"
FACULTY = {
    "мобил": "Мобилпафф",
    "фулст": "Фулстекслей",
    "фронд": "Фрондерин",
    "бекен": "Бекендор",
}
bot = telebot.TeleBot(os.getenv("TEL_TOKEN"))


@bot.message_handler(commands=["start"])
def start(message) -> None:
    """Handles answer of the bot on start command."""
    bot.send_message(
        message.chat.id,
        (
            "I'am watching you \N{eyes}, kids! Let's add some"
            "magic to this conversation \N{crystal ball}."
        ),
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["text"])
def handle_text(message) -> None:
    """Handles text messages in the chat.
    Searches for record command from admin to add new scores record
    to one of the faculties.
    """
    if (
        message.from_user.id == int(ADMIN_ID)
        and START_WORLD in message.text.lower()
    ):
        score = [_ for _ in message.text if _.isdigit()]
        if score:
            score = int("".join(score))
        faculty = [
            _
            for _ in message.text.split()
            if _.lower().startswith(tuple(FACULTY.keys()))
        ]
        if faculty:
            faculty = FACULTY[faculty[0][:5].lower()]
        if score and faculty:
            answer = new_score_record(faculty, score)
            answer_stat = read_records()
            bot.send_message(
                message.chat.id, answer + answer_stat, parse_mode="Markdown"
            )
    elif (
        message.from_user.id == int(ADMIN_ID)
        or message.from_user.id == int(INSPECT_ID)
    ) and message.text.lower() == "стата":
        answer_stat = read_records()
        bot.send_message(message.chat.id, answer_stat, parse_mode="Markdown")


def new_score_record(faculty: str, score: int) -> str:
    """Adds new scores record to the database."""
    db = DataBase()
    db.save_points(faculty, score)
    db.close()
    answer = (
        f"Факультет *{faculty}* получает `{choose_noun_case(score)}` "
        "\N{party popper}\n\n"
    )
    return answer


def read_records() -> str:
    """Fetch all scores statistic from the database."""
    db = DataBase()
    faculty_stat = db.get_all_points()
    db.close()
    header = "Статистика по факультетам на данный момент:\n\n"
    answer_stat = "\n".join(
        [
            f"*{faculty}*: `{choose_noun_case(score)}`"
            for faculty, score in faculty_stat
        ]
    )
    return header + answer_stat


if __name__ == "__main__":
    db = DataBase()
    db.create_database()
    db.close()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
