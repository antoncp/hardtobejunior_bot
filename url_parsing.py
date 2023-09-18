import os
import re

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
YA_ID = os.environ.get("YA_ID")


def find_url(text):
    regex = r"(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-&?=%.]+"
    return re.findall(regex, text)


def read_url(target):
    endpoint = "https://300.ya.ru/api/sharing-url"
    response = requests.post(
        endpoint,
        json={"article_url": f"{target}"},
        headers={"Authorization": f"OAuth {YA_ID}"},
    )
    final_url = response.json().get("sharing_url")
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
