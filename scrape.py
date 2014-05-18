#!/usr/bin/env python3

import json, model, random, time, math, re
import numpy as np
from housepy import config, log, strings
from twitter import Twitter, OAuth

topics = "#google", "frankenstein"
lists = ("tegabrain", "weird-ecology"), ("fork_do", "artandtechnology"), ("MoizSyed", "artsec"), ("HerHealthySelf", "data")

t = Twitter(auth=OAuth(config['twitter']['access_token'], config['twitter']['access_token_secret'], config['twitter']['consumer_key'], config['twitter']['consumer_secret']))
if random.random() < 0.3:
    topic = random.choice(topics)
    log.info("--> chose %s..." % topic)
    statuses = t.search.tweets(q=topic)['statuses']    
else:
    owner_screen_name, slug = random.choice(lists)
    log.info("--> chose %s..." % slug)
    statuses = t.lists.statuses(owner_screen_name=owner_screen_name, slug=slug)

statuses = [status['text'] for status in statuses]
# log.debug(json.dumps(statuses, indent=4))
links = []
for status in statuses:
    ascy = True
    for letter in status:
        if ord(letter) > 128:
            ascy = False
            break
    if ascy is False:
        continue
    ls = re.search("(?P<url>https?://[^\s]+)", status)
    if ls is None:
        continue
    links.append(ls.group("url"))
# log.debug(json.dumps(links, indent=4))

link = random.choice(links)
log.info(link)