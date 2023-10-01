import os

import telebot
from dotenv import load_dotenv

from db import DataBase
from language_utilities import choose_noun_case
from url_parsing import find_url, read_url, send_conversation, writing_message

load_dotenv()
ADMIN_ID = os.environ.get("ADMIN_ID")
INSPECT_ID = os.environ.get("INSPECT_ID")
START_WORLD = "факульт"
REDUCT_WORLD = "минус"
NUM_MESSAGES = 30
FACULTY = {
    "мобил": "Мобилпафф",
    "фулст": "Фулстекслей",
    "фронд": "Фрондерин",
    "фронт": "Фрондерин",
    "бекен": "Бекендор",
    "геймд": "Геймдевран",
    "датаа": "Датааналирин",
    "дизай": "Дизайндей",
    "продж": "Проджектеран",
    "тесте": "Тестендор",
    "девоп": "Девопслей",
}
bot = telebot.TeleBot(os.getenv("TEL_TOKEN"))

bot.set_my_commands(
    [
        telebot.types.BotCommand("/read_link", "Что там за ссылкой?"),
    ]
)


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


@bot.message_handler(commands=["read_link"])
def link(message):
    """Tries to find the link in the last message and summarize the content."""
    if message.chat.type == "private" and message.from_user.id != int(
        INSPECT_ID
    ):
        return
    db = DataBase()
    last_message = db.read_last_message()
    db.close()
    target = find_url(last_message[0])
    if target:
        answer = read_url(target[0])
        if answer:
            bot.send_message(message.chat.id, answer)
        else:
            bot.send_message(
                message.chat.id,
                "Ошибка при загрузке ссылки...",
                parse_mode="Markdown",
            )
    else:
        answer = "Не получилось найти ссылку в предыдущем сообщении..."
        bot.send_message(message.chat.id, answer, parse_mode="Markdown")


@bot.message_handler(commands=["summ_1"])
def summary(message):
    """Summarizes last 30 messages in the chat."""
    if message.chat.type == "private" and message.from_user.id != int(
        INSPECT_ID
    ):
        return
    db = DataBase()
    messages = db.read_messages(NUM_MESSAGES)
    db.close()
    content = "<br><br>".join(
        [
            f"<b>{text[0]}:</b> {text[2]}"
            if text[1] is None
            else f"<b>{text[0]}, {text[1]}:</b> {text[2]}"
            for text in reversed(messages)
        ]
    )
    pre = "Последние 30 сообщений в этом чате в глазах бота:\n\n"
    answer = send_conversation(content)
    bot.send_message(message.chat.id, pre + answer)


@bot.message_handler(commands=["summ_2"])
def sum_me(message):
    """Summarizes last 30 user's messages in the chat"""
    user = message.from_user.id
    db = DataBase()
    messages = db.read_user_messages(user, NUM_MESSAGES)
    db.close()
    content = "<br><br>".join(
        [
            f"<b>{text[0]}:</b> {text[2]}"
            if text[1] is None
            else f"<b>{text[0]}, {text[1]}:</b> {text[2]}"
            for text in reversed(messages)
        ]
    )
    pre = f"{message.from_user.first_name} в глазах бота:\n\n"
    answer = send_conversation(content)
    bot.send_message(message.chat.id, pre + answer)


@bot.message_handler(content_types=["text"])
def handle_text(message) -> None:
    """Handles text messages in the chat.
    Searches for record command from admin to add new scores record
    to one of the faculties.
    """
    if (
        message.from_user.id == int(ADMIN_ID)
        or message.from_user.id == int(INSPECT_ID)
    ) and START_WORLD in message.text.lower():
        score = [_ for _ in message.text if _.isdigit()]
        minus = True if REDUCT_WORLD in message.text.lower() else False
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
            score = -score if minus else score
            answer = new_score_record(faculty, score, message.from_user.id)
            bot.send_message(message.chat.id, answer, parse_mode="Markdown")
    elif (
        message.from_user.id == int(ADMIN_ID)
        or message.from_user.id == int(INSPECT_ID)
    ) and message.text.lower() == "стата":
        answer_stat = read_records(int(ADMIN_ID))
        bot.send_message(message.chat.id, answer_stat, parse_mode="Markdown")
    elif (
        message.from_user.id == int(ADMIN_ID)
        or message.from_user.id == int(INSPECT_ID)
    ) and message.text.lower() == "тестстата":
        answer_stat = read_records(int(INSPECT_ID))
        bot.send_message(message.chat.id, answer_stat, parse_mode="Markdown")
    else:
        db = DataBase()
        db.save_message(
            message.date,
            message.chat.id,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name,
            message.text,
        )
        db.close()
        writing_message(message)


def new_score_record(faculty: str, score: int, id: int) -> str:
    """Adds new scores record to the database."""
    db = DataBase()
    if id == int(ADMIN_ID):
        db.save_points(faculty, score)
    else:
        db.test_save_points(faculty, score)
    db.close()
    if score >= 0:
        answer = (
            f"Фaкультет *{faculty}* получает `{choose_noun_case(score)}` "
            "\N{party popper}\n\n"
        )
    else:
        answer = (
            f"Фaкультет *{faculty}* теряет `{choose_noun_case(score)}` "
            "\N{unamused face}\n\n"
        )
    return answer


def read_records(id: int) -> str:
    """Fetch all scores statistic from the database."""
    db = DataBase()
    if id == int(ADMIN_ID):
        faculty_stat = db.get_all_points()
    else:
        faculty_stat = db.test_get_all_points()
    db.close()
    header = "Статистика на данный момент:\n\n"
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
