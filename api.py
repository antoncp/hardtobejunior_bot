import base64
import json
import logging
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from groq import Groq

from config import logger, settings

client = Groq(api_key=settings.GROQ_API_KEY)


def find_url(text):
    regex = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+"
    return re.findall(regex, text)


def send_yandex_api(link):
    endpoint = "https://300.ya.ru/api/sharing-url"
    response = requests.post(
        endpoint,
        json={"article_url": f"{link}"},
        headers={"Authorization": f"OAuth {settings.YA_ID}"},
    )
    return response.json().get("sharing_url")


def read_url(target):
    final_url = send_yandex_api(target)
    if final_url:
        logger.info(f"Получен ответ от YandexGPT: {final_url}")
        response = requests.get(final_url)
        soup = BeautifulSoup(response.content, "html.parser")
        og_title_tag = soup.find("meta", attrs={"property": "og:title"})
        if og_title_tag:
            title = og_title_tag["content"]
        og_description_tag = soup.find(
            "meta", attrs={"property": "og:description"}
        )
        if og_description_tag:
            description = og_description_tag["content"]
        return title + "\n\n" + description
    else:
        logger.warning("Ошибка в ответе от YandexGPT")
        return None


def send_conversation(content):
    dt = datetime.now()
    time_name = str(datetime.timestamp(dt)).replace(".", "")
    url = f"https://blog.antoncp.nl/create_page/{time_name}"
    username = settings.API_LOGIN
    password = settings.API_PAS
    credentials = base64.b64encode(
        f"{username}:{password}".encode("utf-8")
    ).decode("utf-8")
    headers = {"Authorization": f"Basic {credentials}"}
    response = requests.post(
        url, data=content.encode("utf-8"), headers=headers
    )
    if response.json().get("status") == "created":
        link = response.json().get("link")
        final_url = send_yandex_api(link)
        requests.delete(url, headers=headers)
        if final_url:
            response = requests.get(final_url)
            soup = BeautifulSoup(response.content, "html.parser")
            og_description_tag = soup.find(
                "meta", attrs={"property": "og:description"}
            )
            if og_description_tag:
                description = og_description_tag["content"]
            return description


def writing_message(message):
    data = {
        "timestamp": message.date,
        "chat_id": message.chat.id,
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "user_first_name": message.from_user.first_name,
        "user_last_name": message.from_user.last_name,
        "text": message.text,
    }
    url = "http://localhost/save_message/"
    username = settings.API_LOGIN
    password = settings.API_PAS
    credentials = base64.b64encode(
        f"{username}:{password}".encode("utf-8")
    ).decode("utf-8")
    headers = {"Authorization": f"Basic {credentials}"}
    try:
        requests.post(
            url, data=json.dumps(data), headers=headers, timeout=(1, None)
        )
    except Exception:
        logging.info(f"ОШИБКА ЗАПИСИ: {message.text[:45]}...")


def summ_with_groq(messages):
    message = [{"role": "user", "content": f"{settings.PROMPT}{messages}"}]
    response = client.chat.completions.create(
        model="llama3-8b-8192", messages=message, temperature=0
    )
    return response
