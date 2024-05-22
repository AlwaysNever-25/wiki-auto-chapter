import requests
import inflect
import arrow
import os
from dotenv import load_dotenv
import feedparser

load_dotenv()

bot_user = os.environ['WIKI_BOT_USER']
bot_pass = os.environ['WIKI_BOT_PASS']

p = inflect.engine()

d = feedparser.parse("https://mangasee123.com/rss/Zombie-100.xml")
chapter_num = len(d['items']) - 6

chapter_ord = p.number_to_words(p.ordinal(chapter_num))
date = arrow.utcnow().to('Asia/Tokyo').format('MM-DD')
chapter_date = arrow.utcnow().to('Asia/Tokyo').format('MMMM D, YYYY')
magazine_issue = arrow.utcnow().shift(months=+1).to('Asia/Tokyo').format('MMMM YYYY')

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
            "format": "json",
            "text": "{{stub}}{{Infobox Chapter \n|Color #1     = \n|name         = \n|imagepath    = Chapter %s.png\n|Volume       = \n|Chapter      = %s \n|Kana         = \n|Romaji       = \n|Release Date = %s\n|Previous     = [[Chapter %s]]\n|Next         = [[Chapter %s]]\n|Anime        = \n}}\n{{Nihongo|'''Chapter %s'''||}} is the %s chapter of ''[[Zom 100 (manga)|Zom 100]]'' manga series. It is written by [[Haro Aso]] and illustrated by [[Takata Koutarou]]. It was released in ''Monthly Sunday GX'' on %s, on its %s issue.<!--{{Ref|text=[https://www.amazon.co.jp/-/en/dp/B0D4443T71/ ''Monthly Sunday GX'' %s issue].  ''Amazon''}}-->\n==Summary==\n\n\n==Characters by Appearance==\n\n\n==Trivia==\n\n\n==References==\n{{References}}\n\n\n==Navigation==\n{{Chapter Navbox}}\n\n[[Category:Manga Chapters]]\n[[es:Capítulo %s]]" % (chapter_num, chapter_num, chapter_date, chapter_num-1, chapter_num+1, chapter_num, chapter_ord, chapter_date, magazine_issue, magazine_issue, chapter_num),
            "token": CSRF_TOKEN
        }
    R = S.post(URL, data=PARAMS_3)
    DATA = R.json()
    print(DATA)