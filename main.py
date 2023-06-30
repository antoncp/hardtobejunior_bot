import os

import telebot
from dotenv import load_dotenv

from db import DataBase

from language_utilities import choose_noun_case

load_dotenv()
ADMIN_ID = os.environ.get("ADMIN_ID")
START_WORLD = "факульт"
FACULTY = {
    "мобил": "Мобилпафф",
    "фулст": "Фулстекслей",
    "фронд": "Фрондерин",
    "бекен": "Бекендор",
}
bot = telebot.TeleBot(os.getenv("TEL_TOKEN"))


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        (
            "I'am watching you \N{eyes}, kids! Let's add some"
            "magic to this conversation \N{crystal ball}."
        ),
        parse_mode="Markdown",
    )


@bot.message_handler(content_types=["text"])
def handle_text(message):
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
            db = DataBase()
            db.save_points(faculty, score)
            faculty_stat = db.get_all_points()
            db.close()
            answer = (
                f"Факультет *{faculty}* получает `{choose_noun_case(score)}`. "
                "\N{party popper}\n\nСтатистика по факультетам "
                "на данный момент:\n\n"
            )
            answer_stat = "\n".join(
                [
                    f"*{faculty}*: `{choose_noun_case(score)}` бал."
                    for faculty, score in faculty_stat
                ]
            )
            bot.send_message(
                message.chat.id, answer + answer_stat, parse_mode="Markdown"
            )
    else:
        print(message.text)


if __name__ == "__main__":
    db = DataBase()
    db.create_database()
    db.close()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
