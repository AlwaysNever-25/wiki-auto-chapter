#!/usr/bin/python3

"""
    auto-chapter-onk-anime.py

    MediaWiki API script to automate episode page creation
    Using `Edit` module: POST request to edit a page every time there is a new update
    Differentiated from automated chapter page creation because of one hour time difference between release
    MIT license
"""

from dotenv import load_dotenv
import os
import requests
import inflect
import arrow

load_dotenv()
bot_user = os.environ['WIKI_BOT_USER']
bot_pass = os.environ['WIKI_BOT_PASS']

episode_date = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('MMMM D, YYYY')
episode_time = arrow.utcnow().shift(weeks=+1).to('Asia/Tokyo').format('HH')

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
    "search": "Episode",
    "limit": "25",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS_3)
SEARCH2 = R.json()
print(SEARCH2)
episode_num = len(SEARCH2[1])
p = inflect.engine()
episode_ord = p.number_to_words(p.ordinal(episode_num+1))

# Step 4: GET request to search if page already exists
PARAMS_4 = {
    "action": "opensearch",
    "namespace": "Main",
    "search": "Episode %s" % str(episode_num+1),
    "limit": "5",
    "format": "json"
}

R = S.get(url=URL, params=PARAMS_4)
SEARCH = R.json()

# if search came up empty
if not SEARCH[1]:
    PARAMS_5 = {
        "action": "edit",
        "title": "Episode %s" % str(episode_num+1),
        "bot": "yes",
        "format": "json",
        "text": "{{stub}}{{Infobox Episode \n|title         = Episode %s \n|image         = \n|japanese       = \n|romaji     = \n|season    = [[Season 2|2]]\n|episode     = %s \n|airdate = %s \n|runtime      = \n|adapted       = \n|screenwriter =     \n|storyboard       = \n|episode_director        = \n|animation_director         = \n|previous     = [[Episode %s]]\n|next         = [[Episode %s]]\n}}\n{{Nihongo|'''Episode %s'''||}} is the %s episode of ''[[Oshi no Ko]]'' anime adaptation.\n== Synopsis==\n\n== Summary ==\n\n== Characters ==\n\n==Gallery==\n\n==Anime Notes==\n\n== Trivia ==\n\n== References ==\n{{References}}\n\n\n== Navigation ==\n{{AnimeNavigation}}\n\n[[Category:Episodes]]\n[[Category:Season 2]]" % (episode_num+1, episode_num+1, episode_date, episode_num, episode_num+2, episode_num+1, episode_ord),
        "token": CSRF_TOKEN
    }

    R = S.post(URL, data=PARAMS_5)
    DATA = R.json()
    print(DATA)

    PARAMS_6 = {
        "action": "edit",
        "title": "Template:Episode_Countdown",
        "bot": "yes",
        "format": "json",
        "text": "{{Countdown/Episode\n|episode=%s\n|date=%s\n|time=%s:00:00\n}}" % (episode_num+1, episode_date, episode_time),
        "token": CSRF_TOKEN
    }

    R = S.post(URL, data=PARAMS_6)
    DATA = R.json()
    print(DATA)