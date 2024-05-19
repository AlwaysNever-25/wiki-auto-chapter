import requests
import inflect
import arrow
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

bot_user = os.environ['WIKI_BOT_USER']
bot_pass = os.environ['WIKI_BOT_PASS']

p = inflect.engine()

response = requests.get("https://ynjn.jp/allEpisodeList/9862")
soup = BeautifulSoup(response.content, "html.parser")

chapter_numbers = soup.find_all("li", class_="title__listItem")

chapter_num = len(chapter_numbers)

chapter_ord = p.number_to_words(p.ordinal(chapter_num))
date = arrow.utcnow().to('Asia/Tokyo').format('MM-DD')
dayofweek = arrow.utcnow().to('Asia/Tokyo').format('dddd')

if dayofweek == "Thursday":
    chapter_date = arrow.utcnow().to('Asia/Tokyo').format('MMMM D, YYYY')
    chapter_date_cd = arrow.utcnow().to('Asia/Tokyo').format('MMMM D YYYY')
    magazine_number = int(arrow.utcnow().to('Asia/Tokyo').format('DDD')) / 7 + 5
else:
    chapter_date = arrow.utcnow().to('Asia/Tokyo').format('MMMM D, YYYY')
    magazine_number = 0

S = requests.Session()

URL = os.environ['URL1']

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
PARAMS = {
    "action": "opensearch",
    "namespace": "Main",
    "search": "Chapter %s" % str(chapter_num),
    "limit": "5",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS)
SEARCH = R.json()
# if search came up empty
if not SEARCH[1]:
    # Step 5: POST request to edit a page
    PARAMS_3 = {
            "action": "edit",
            "title": "Chapter %s" % str(chapter_num),
            "bot": "yes",
            "token": CSRF_TOKEN,
            "format": "json",
            "text": "{{stub}}{{Chapter \n|title         = \n|image    = Chapter %s.png\n|kanji         = \n|romaji       = \n|volume       = \n|pages = 18\n|arc = \n|issue = Weekly Young Jump #%d 2024 \n|release_date = %s\n|prev     = [[Chapter %s]]\n|next         = [[Chapter %s]]\n}}\n{{Nihongo|'''Chapter %s'''||}} is the %s chapter of ''[[Renai Daikou]]'' manga series, written by [[Aka Akasaka]] and illustrated by [[Nishizawa 5mm]]. It will be released in issue #%d, 2024 of ''[[Weekly Young Jump]]'' on %s.<!--<ref>[https://ynjn.jp/viewer/9862/ 第%s話 ] (in Japanese). ''Young Jump''. Retrieved %s</ref>-->\n== Summary ==\n\n\n== Characters ==\n\n\n== Trivia ==\n\n\n== References ==\n{{References}}\n\n\n== Navigation ==\n{{MangaNavigation}}\n\n[[Category:Chapters]]" % (chapter_num, magazine_number, chapter_date, chapter_num-1, chapter_num+1, chapter_num, chapter_ord, magazine_number, chapter_date, chapter_num, chapter_date)
        }
    R = S.post(URL, data=PARAMS_3)
    DATA = R.json()
    print(DATA)

    PARAMS_4 = {
            "action": "edit",
            "title": "Chapter %s" % str(chapter_num),
            "bot": "yes",
            "token": CSRF_TOKEN,
            "format": "json",
            "text": "{{Countdown/Chapter\n|chapter=%s\n|date=%s\n}}" % (chapter_num, chapter_date_cd)
    }
    R = S.post(URL, data=PARAMS_4)
    DATA = R.json()
    print(DATA)