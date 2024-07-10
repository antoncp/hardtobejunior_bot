import os
import sys
from threading import Timer

import telebot

from api import (find_url, read_url, send_conversation, summ_with_groq,
                 writing_message)
from config import logger, settings
from db import DataBase
from health_endpoint import flask_thread, shutdown_event
from utilities import choose_noun_case, get_time

ADMIN_ID = settings.ADMIN_ID
INSPECT_ID = settings.INSPECT_ID
FRIDAY_MODE = False

bot = telebot.TeleBot(settings.TEL_TOKEN)

bot.set_my_commands(
    [
        telebot.types.BotCommand("/read_link", "Что там за ссылкой?"),
        telebot.types.BotCommand("/house_points", "Баллы факультетов"),
    ]
)

bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("/read_link", "Что там за ссылкой?"),
        telebot.types.BotCommand("/show_logs", "Показать логи"),
        telebot.types.BotCommand("/house_points", "Баллы факультетов"),
    ],
    scope=telebot.types.BotCommandScopeChat(INSPECT_ID),
)

if not settings.DEBUG:
    try:
        bot.set_my_commands(
            commands=[
                telebot.types.BotCommand("/read_link", "Что там за ссылкой?"),
                telebot.types.BotCommand("/house_points", "Баллы факультетов"),
            ],
            scope=telebot.types.BotCommandScopeChat(ADMIN_ID),
        )
    except Exception as e:
        message = (
            f"ОШИБКА установки команд для {ADMIN_ID}. Режим "
            f"DEBUG {settings.DEBUG}. Детали ошибки: {e}"
        )
        print(message)
        logger.warning(message)


@bot.message_handler(commands=["start"])
def start(message) -> None:
    """Handles answer of the bot on start command."""
    return bot.send_message(
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
    if message.chat.type == "private" and message.from_user.id != INSPECT_ID:
        return
    db = DataBase()
    last_message = db.read_last_message()
    db.close()
    logger.info(f"Поиск ссылки в сообщении: {last_message}")
    target = find_url(last_message[0])
    if target:
        logger.info(f"Найдена ссылка: {target}")
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


@bot.message_handler(commands=["show_logs"])
def show_logs(message):
    """Sends logs files of app to the admin."""
    if message.chat.id == INSPECT_ID:
        with open("db/all.log") as all_file:
            bot.send_document(message.chat.id, all_file, caption="Полный лог")
        with open("db/custom.log") as custom_file:
            bot.send_document(
                message.chat.id, custom_file, caption="История запросов"
            )


@bot.message_handler(commands=["house_points"])
def show_stat(message):
    """Shows statistic of score by faculty."""
    if message.chat.id == INSPECT_ID:
        answer_stat = read_records()
        bot.send_message(message.chat.id, answer_stat, parse_mode="Markdown")
        answer_stat = read_records(test=True)
        now = get_time(1)
        answer_stat = f'{now.strftime("%m/%d/%Y, %H:%M:%S")}\n\n' + answer_stat
        return bot.send_message(
            message.chat.id, answer_stat, parse_mode="Markdown"
        )
    else:
        answer_stat = read_records()
        return bot.send_message(
            message.chat.id, answer_stat, parse_mode="Markdown"
        )


@bot.message_handler(commands=["summ_1"])
def summary(message):
    """Summarizes last n-messages in the chat."""
    if message.from_user.id != INSPECT_ID:
        return
    db = DataBase()
    messages = db.read_messages(settings.NUM_MESSAGES)
    db.close()
    content = "; ".join(
        [
            f"{text[0]}: {text[2]}"
            if text[1] is None
            else f"{text[0]}, {text[1]}: {text[2]}"
            for text in reversed(messages)
        ]
    )
    file_path = "summary.txt"
    pre_answer = summ_with_groq(content)
    try:
        sys.stdout.write(str(pre_answer))
    except Exception as e:
        sys.stdout.write(f"Write out failed {e}")
    answer = (
        f"{pre_answer.choices[0].message.content}\n\n"
        f"Tokens: {pre_answer.usage.total_tokens}"
    )
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    with open(file_path, "rb") as file:
        bot.send_document(message.chat.id, file)
    os.remove(file_path)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=["summ_2"])
def sum_me(message):
    """Summarizes last 30 user's messages in the chat"""
    user = message.from_user.id
    db = DataBase()
    messages = db.read_user_messages(user, settings.NUM_MESSAGES)
    db.close()
    content = "<br><br>".join(
        [
            f"{text[0]}: {text[2]}"
            if text[1] is None
            else f"{text[0]}, {text[1]}: {text[2]}"
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
    admin = is_admin(message)
    if (
        message.from_user.id == ADMIN_ID
        or message.from_user.id == INSPECT_ID
        or admin
    ) and settings.START_WORLD in message.text.lower():
        score = [_ for _ in message.text if _.isdigit()]
        minus = (
            True if settings.REDUCT_WORLD in message.text.lower() else False
        )
        if score:
            score = int("".join(score))
            if str(score) not in message.text.lower():
                score = None
        faculty = []
        for word in message.text.split():
            for key in tuple(settings.FACULTY.keys()):
                if word.lower().startswith(key):
                    faculty.append(key)
                    break
        if faculty:
            faculty = settings.FACULTY[faculty[0].lower()]
        if score and faculty:
            score = -score if minus else score
            answer = new_score_record(faculty, score, message.from_user.id)
            return bot.send_message(
                message.chat.id, answer, parse_mode="Markdown"
            )
    elif (
        message.from_user.id == ADMIN_ID or message.from_user.id == INSPECT_ID
    ) and message.text.lower() == "тестстата":
        global FRIDAY_MODE
        FRIDAY_MODE = True
        answer_stat = read_records(test=True)
        return bot.send_message(
            message.chat.id, answer_stat, parse_mode="Markdown"
        )
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
    if id == INSPECT_ID:
        db.test_save_points(faculty, score)
    else:
        db.save_points(faculty, score)
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


def read_records(test: bool = False) -> str:
    """Fetch all scores statistic from the database."""
    db = DataBase()
    if not test:
        faculty_stat = db.get_all_points()
        header = "Статистика на данный момент:\n\n"
    else:
        faculty_stat = db.test_get_all_points()
        header = "Тестовая статистика на данный момент:\n\n"
    db.close()
    answer_stat = "\n".join(
        [
            f"*{faculty}*: `{choose_noun_case(score)}`"
            for faculty, score in faculty_stat
        ]
    )
    return header + answer_stat


def is_admin(message):
    """Check if user is a admin of the group"""
    status = bot.get_chat_member(message.chat.id, message.from_user.id).status
    if status == "creator" or status == "administrator":
        return True
    return False


def monitoring_friday_talks():
    """Every minute checks the Friday's talks conditions.
    If the Friday starts - sends a message to the chat.
    The same in the end of Friday.
    """
    one_minute_monitor = Timer(60.0, monitoring_friday_talks)
    one_minute_monitor.start()
    now = get_time(2)
    global FRIDAY_MODE
    if now.weekday() == 4:
        from_midnight = int(
            (
                now - now.replace(hour=0, minute=0, second=0, microsecond=0)
            ).total_seconds()
        )
        if from_midnight <= 70 and not FRIDAY_MODE:
            answer = (
                "\N{party popper} Идущие на флуд приветствуют тебя. "
                "Разговорчики не по теме в строю разрешены на время "
                "пятницы \N{party popper}"
            )
            bot.send_message(settings.CHAT_ALERT, answer)
            FRIDAY_MODE = True
        elif 100 < from_midnight < 1000:
            FRIDAY_MODE = False
    elif now.weekday() == 5:
        from_midnight = int(
            (
                now - now.replace(hour=0, minute=0, second=0, microsecond=0)
            ).total_seconds()
        )
        if from_midnight <= 70 and not FRIDAY_MODE:
            answer = (
                "Флудный день окончен \N{unamused face}. "
                "Всем спасибо, все свободны."
            )
            bot.send_message(settings.CHAT_ALERT, answer)
            FRIDAY_MODE = True
        elif 100 < from_midnight < 1000:
            FRIDAY_MODE = False


if __name__ == "__main__":
    db = DataBase()
    db.create_database()
    db.close()
    flask_thread.start()
    # monitoring_friday_talks()
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Error in Telegram bot: {e}")
        shutdown_event.set()
