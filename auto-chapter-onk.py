#!/usr/bin/python3

"""
    auto-chapter-onk.py

    MediaWiki API script to automate chapter page creation
    Using `Edit` module: POST request to edit a page every time there is a new update
    MIT license
"""

from functools import partial
import sys
from mloader.loader import MangaLoader
from mloader.exporter import RawExporter
from itertools import chain
from dotenv import load_dotenv
import os
import logging
import requests
import inflect
import arrow
import pykakasi
import time
from bs4 import BeautifulSoup


response = requests.get("https://ynjn.jp/allEpisodeList/1156")
soup = BeautifulSoup(response.content, "html.parser")

load_dotenv()
bot_user = os.environ['WIKI_BOT_USER']
bot_pass = os.environ['WIKI_BOT_PASS']

"""
log = logging.getLogger()
# overkill but mloader expects it, wont log otherwise
def setup_logging():
    for logger in ("requests", "urllib3"):
        logging.getLogger(logger).setLevel(logging.WARNING)
    handlers = [logging.StreamHandler(sys.stdout)]
    logging.basicConfig(
        handlers=handlers,
        format=(
            "{asctime:^} | {levelname: ^8} | "
            "{filename: ^14} {lineno: <4} | {message}"
        ),
        style="{",
        datefmt="%d.%m.%Y %H:%M:%S",
        level=logging.INFO,
    )

setup_logging()

title_id = 100191
out_dir = "raws"

exporter = RawExporter
exporter = partial(
    exporter,
    add_chapter_title=True,
    add_chapter_subdir=True,
)
loader = MangaLoader(exporter, "super_high", False)

details = loader._get_title_details(title_id)

for x in chain(details.first_chapter_list, details.last_chapter_list):
    chapter_num = eval(x.name.replace("#", "").strip().lstrip("0"))
    parts = x.sub_title.split(": ")
    title = ": ".join(parts[1:])

chapter_title = title.lower().title()"""

chapter_numbers = soup.find_all("li", class_="title__listItem")
chapter_num = len(chapter_numbers)+6

chapter_titles = soup.find_all("div", class_="title__listItemText md:!text-[16px] !text-[16px]")
chapter_title_raw = chapter_titles[-1].contents
chapter_title_full = chapter_title_raw[0]
parts = chapter_title_full.split(" ")
chapter_title_jp = parts[1]

if chapter_title_jp == "今週は休載です":
    chapter_num = len(chapter_numbers)+5
else:
    kks = pykakasi.kakasi()
    result = kks.convert(chapter_title_jp)
    chapter_romaji_parts = []
    for item in result:
        x = "{}".format(item['hepburn'])
        chapter_romaji_parts.append(x.capitalize())

    chapter_romaji = " ".join(chapter_romaji_parts)

p = inflect.engine()

chapter_ord = p.number_to_words(p.ordinal(chapter_num+1))
date = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('MM-DD')
dayofweek = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('dddd')

if dayofweek == "Thursday":
    chapter_date = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('MMMM D, YYYY')
    magazine_number = int(arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('DDD')) / 7 + 5
else:
    chapter_date = 0
    magazine_number = 0

print(chapter_num)

S = requests.Session()

URL = os.environ['URL']

# Step 1: GET request to fetch login token
PARAMS_0 = {
    "action": "query",
    "meta": "tokens",
    "type": "login",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS_0)
DATA = R.json()

LOGIN_TOKEN = DATA['query']['tokens']['logintoken']

# Step 2: POST request to log in. Use of main account for login is not
# supported. Obtain credentials via Special:BotPasswords
# (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
PARAMS_1 = {
    "action": "login",
    "lgname": bot_user,
    "lgpassword": bot_pass,
    "lgtoken": LOGIN_TOKEN,
    "format": "json"
}

R = S.post(URL, data=PARAMS_1)

# Step 3: GET request to fetch CSRF token
PARAMS_2 = {
    "action": "query",
    "meta": "tokens",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS_2)
DATA = R.json()

CSRF_TOKEN = DATA['query']['tokens']['csrftoken']

# Step 4: GET request to search if page already exists
PARAMS_3 = {
    "action": "opensearch",
    "namespace": "Main",
    "search": "Chapter %s" % str(chapter_num+1),
    "limit": "5",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS_3)
SEARCH = R.json()
# if search came up empty
if not SEARCH[1]:
    # Step 5: POST request to edit a page
    PARAMS_4 = {
            "action": "edit",
            "title": "Chapter %s" % str(chapter_num+1),
            "bot": "yes",
            "format": "json",
            "text": "{{stub}}{{ChapterKai \n|name         = \n|Kana         = \n|Romaji       = \n|PAGENAME     = \n|imagepath    = Chapter %s cover.png\n|Color #1     = #FF9A00\n|Release Date = %s  (Weekly Young Jump 2024 #%d/ Mangaplus)\n|Previous     = [[Chapter %s]]\n|Next         = [[Chapter %s]]\n|Volume       = \n|Arc          = [[Toward the Stars and Dreams]]\n}}\n{{Nihongo|'''Chapter %s'''||}} is the %s chapter of ''[[Oshi no Ko]]'' manga series. It is written by [[Aka Akasaka]] and illustrated by [[Mengo Yokoyari]]. It will be released in ''Weekly Young Jump'' on %s.\n== Summary ==\n\n\n== Characters ==\n\n\n== Trivia ==\n\n\n== References ==\n{{References}}\n\n\n== Navigation ==\n{{MangaNavigation}}\n\n[[Category:Chapters]]\n[[Category:Toward the Stars and Dreams]]" % (chapter_num+1, chapter_date, magazine_number, chapter_num, chapter_num+2, chapter_num+1, chapter_ord, chapter_date),
            "token": CSRF_TOKEN
        }
    R = S.post(URL, data=PARAMS_4)
    DATA = R.json()
    print(DATA)

    PARAMS_5 = {
        "action": "edit",
        "title": "Template:Chapter_Countdown",
        "bot": "yes",
        "format": "json",
        "text": "{{Countdown/Chapter\n|chapter=%s\n|date=%s\n}}" % (chapter_num+1, chapter_date),
        "token": CSRF_TOKEN
    }

    R = S.post(URL, data=PARAMS_5)
    DATA = R.json()
    print(DATA)

    PARAMS_6 = {
        "action": "edit",
        "title": "Template:Latest_Chapter",
        "bot": "yes",
        "format": "json",
        "text": "{{#if:{{{1|}}}\n|{{#switch:{{{1|}}}\n|image = [[File:{{#ifexist:File:Chapter %s cover.png|Chapter %s cover.png|{{#ifexist:File:Chapter %s cover.jpg|Chapter 148 cover.jpg|None.png}}}}|center|200px|link=Chapter %s]]\n|chapter = Chapter %s: {{Nihongo|[[Chapter %s|'''Chapter %s''']]<br>|%s|%s}}\n|}}\n|This page is intentionally blank.}}" % (chapter_num, chapter_num, chapter_num, chapter_num, chapter_num, chapter_num, chapter_num, chapter_title_jp, chapter_romaji),
        "token": CSRF_TOKEN
    }

    R = S.post(URL, data=PARAMS_6)
    DATA = R.json()
    print(DATA)