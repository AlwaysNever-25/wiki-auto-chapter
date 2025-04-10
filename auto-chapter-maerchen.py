#!/usr/bin/python3

"""
    auto-chapter-maerchen.py

    MediaWiki API script to automate chapter page creation and relevant updates
    Using `Edit` module: POST request to edit a page every time there is a new update
    MIT license
"""

# mloader for English Title
from functools import partial
import sys
from mloader.loader import MangaLoader
from mloader.exporter import RawExporter
from itertools import chain
import logging

import requests
import inflect
import arrow

# dotenv
from dotenv import load_dotenv
import os

# Start of loading env section
load_dotenv()
bot_user = os.environ['WIKI_BOT_USER']
bot_pass = os.environ['WIKI_BOT_PASS']

# Start of getting English title and chapter number through Mangaplus API section
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

title_id = 100468
out_dir = "raws"

exporter = RawExporter
exporter = partial(
    exporter,
    add_chapter_title=True,
    add_chapter_subdir=True,
)
loader = MangaLoader(exporter, "super_high", False)

details = loader._get_title_details(title_id)

for x in chain(details.chapter_list_group):
    for y in (x.first_chapter_list):
        chapter_num = eval(y.name.replace("#", "").replace(",", "").strip().lstrip("0"))
        parts = y.sub_title.split(": ")
        title = ": ".join(parts[1:])

chapter_title = title.lower().title()

"""
print(chapter_title)
print(chapter_num)
"""

# Start of getting Japanese title through the raw website (ynjn.jp)
# requires Selenium, running this locally instead of through gh action

# Start of MediaWiki API section
S = requests.Session()
URL = os.environ['URL2']

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

# alternative method if mloader doesn't work
# this requires updating the specific page to have the current chapter number, which can be done through API as well
"""
PARAMS_3 = {
        "action": "parse",
        "page": "User:AlwaysNever25/Current",
        "prop": "wikitext",
        "format": "json"
    }
res = S.get(URL, params=PARAMS_3)
DATA = res.json()
chapter_num = int(DATA['parse']['wikitext']['*'])
print(chapter_num)
"""

p = inflect.engine()

chapter_ord = p.number_to_words(p.ordinal(chapter_num+1))
date = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('MM-DD')
dayofweek = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('dddd')

if dayofweek == "Thursday":
    chapter_date_cur = arrow.utcnow().to('Asia/Tokyo').format('MMMM D, YYYY')
    chapter_date = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('MMMM D, YYYY')
    magazine_number = int(arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('DDD')) / 7 + 5
else:
    chapter_date = 0
    magazine_number = 0

"""
print(chapter_ord)
print(DATA['parse']['wikitext']['*'])
"""

# Step 4: GET request to search if page already exists
PARAMS_4 = {
    "action": "opensearch",
    "namespace": "Main",
    "search": "Chapter %s" % str(chapter_num+1),
    "limit": "5",
    "format": "json"
}
R = S.get(url=URL, params=PARAMS_4)
SEARCH = R.json()

# if search came up empty
if not SEARCH[1]:
    # Step 5: POST request to edit a page
    PARAMS_5 = {
            "action": "edit",
            "title": "Chapter %s" % str(chapter_num+1),
            "bot": "yes",
            "format": "json",
            "text": "{{Stub}}{{Infobox/Chapter \n| image          = Chapter %s.png\n| volume         = \n| pages          = \n| arc            = \n| release        = %s  (Weekly Young Jump 2024 #%d/ Mangaplus)\n| episode        = \n}}\n{{Nihongo|{{CH|%s}}|{{CHNAME|%s}}|{{CHNAME/JP|%s}}}} is the %s chapter of [[Maerchen Crown|''Maerchen Crown'']] manga series. It will be released on %s in ''Weekly Young Jump'' issue #%d 2025.\n== Summary ==\n\n== Plot ==\n\n== Characters ==\n''In order of appearance''\n\n== Trivia ==\n\n== Links ==\n\n<!--\n== References ==\n{{References}}\n-->\n\n== Navigation ==\n{{Navbox/Chapter}}" % (chapter_num+1, chapter_date, magazine_number, chapter_num+1, chapter_num+1, chapter_num+1, chapter_ord, chapter_date, magazine_number),
            "token": CSRF_TOKEN
        }
    R = S.post(URL, data=PARAMS_5)
    DATA = R.json()
    print(DATA)

    PARAMS_6 = {
        "action": "edit",
        "title": "Template:Chapter_Countdown",
        "bot": "yes",
        "format": "json",
        "text": "{{Countdown/Chapter\n|chapter=%s\n|date=%s\n}}" % (chapter_num+1, chapter_date),
        "token": CSRF_TOKEN
    }

    R = S.post(URL, data=PARAMS_6)
    DATA = R.json()
    print(DATA)

    PARAMS_7 = {
        "action": "edit",
        "title": "Template:Latest_Chapter",
        "bot": "yes",
        "format": "json",
        "text": "{{#if:{{{1|}}}\n|{{#switch:{{{1|}}}\n|image = [[File:{{#ifexist:File:Chapter %s.png|Chapter %s.png|{{#ifexist:File:Chapter %s.jpg|Chapter 2.png|None.png}}}}|center|200px|link=Chapter %s]]\n|chapter = Chapter %s: {{Nihongo|'''{{CH|%s}}'''|{{CHNAME/JP|%s}}|{{CHNAME/JP|%sR}}}}\n|date = %s\n|}}\n|This page is intentionally blank.}}" % (chapter_num, chapter_num, chapter_num, chapter_num, chapter_num, chapter_num, chapter_num, chapter_num, chapter_date_cur),
        "token": CSRF_TOKEN
    }

    R = S.post(URL, data=PARAMS_7)
    DATA = R.json()
    print(DATA)

    # alternative method if mloader doesn't work
    """
    PARAMS_8 = {
        "action": "edit",
        "title": "User:AlwaysNever25/Current",
        "bot": "yes",
        "format": "json",
        "text": "%s" % chapter_num+1,
        "token": CSRF_TOKEN
    }
    R = S.post(URL, data=PARAMS_8)
    DATA = R.json()
    print(DATA)
    """

    PARAMS_9 = {
            "action": "parse",
            "page": "Template:CHNAME",
            "prop": "wikitext",
            "format": "json"
        }
    R = S.post(URL, data=PARAMS_9)
    DATA = R.json()
    chname_old = str(DATA['parse']['wikitext']['*'])
    appended = "| %d = %s\n}}" % (chapter_num, chapter_title)
    chname_new = appended.join(chname_old.rsplit("}}", 1))


    PARAMS_10 = {
        "action": "edit",
        "title": "Template:CHNAME",
        "bot": "yes",
        "format": "json",
        "text": chname_new,
        "token": CSRF_TOKEN
    }
    R = S.post(URL, data=PARAMS_10)
    DATA = R.json()
    print(DATA)