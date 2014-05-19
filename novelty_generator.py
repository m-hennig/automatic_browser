#!/usr/bin/env python3

import json, model, random, time, math, re, pycurl
import numpy as np
from housepy import config, log, strings, net
from twitter import Twitter, OAuth

topics = "#google", "frankenstein"
lists = ("tegabrain", "weird-ecology"), ("fork_do", "artandtechnology"), ("MoizSyed", "artsec"), ("HerHealthySelf", "data")

t = Twitter(auth=OAuth(config['twitter']['access_token'], config['twitter']['access_token_secret'], config['twitter']['consumer_key'], config['twitter']['consumer_secret']))

def get_url():
    log.info("novelty_generator.get_url()")
    try:
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
        urls = []
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
            urls.append(ls.group("url"))
        # log.debug(json.dumps(urls, indent=4))

        url = random.choice(urls)
        url = unshorten(url)
        log.info(url)
        return url
    except Exception as e:
        log.error(log.exc(e))
        return "http://google.com"
    
def unshorten(url):
    log.info("--> unshortening %s" % url)
    if "/t.co/" not in url:
        return url
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.WRITEFUNCTION, lambda x: None)
    c.setopt(c.VERBOSE, False)    
    c.setopt(c.FOLLOWLOCATION, True)
    c.perform()    
    try:
        url = c.getinfo(pycurl.EFFECTIVE_URL)
    except Exception as e:
        log.error(log.exc(e))
        return "http://google.com"
    return url


if __name__ == "__main__":
    get_url()
