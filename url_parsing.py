import os
import re
from datetime import datetime

import requests
import base64
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
YA_ID = os.environ.get("YA_ID")
API_LOGIN = os.environ.get("API_LOGIN")
API_PAS = os.environ.get("API_PAS")


def find_url(text):
    regex = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+"
    return re.findall(regex, text)


def send_yandex_api(link):
    endpoint = "https://300.ya.ru/api/sharing-url"
    response = requests.post(
        endpoint,
        json={"article_url": f"{link}"},
        headers={"Authorization": f"OAuth {YA_ID}"},
    )
    return response.json().get("sharing_url")


def read_url(target):
    final_url = send_yandex_api(target)
    if final_url:
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
        return None


def send_conversation(content):
    dt = datetime.now()
    time_name = str(datetime.timestamp(dt)).replace(".", "")
    url = f"https://blog.antoncp.nl/create_page/{time_name}"
    username = API_LOGIN
    password = API_PAS
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
        else:
            return None
