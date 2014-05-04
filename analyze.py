#!/usr/bin/env python3

import json, model, random, time
import numpy as np
from housepy import config, log

MAX_DURATION = 15 * 60  # you're not really spending more than 15 minutes on a site

class Site(object):

    sites = {}

    @classmethod
    def get(cls, host):
        host = host.replace("www.", "")
        if not host in cls.sites:
            cls.sites[host] = Site(host)
        return cls.sites[host]

    def __init__(self, host):
        self.host = host
        self.durations = []        
        self.nexts = []
        self.pages = []
        
    def find_next(self):
        log.debug("Site.find_next")
        print("nexts %s" % self.nexts)
        if not len(self.nexts):
            # new site, not enough info, choose most common site
            site = max(Site.sites.values(), key=lambda site: len(site.durations))            
        else:
            site = random.choice(self.nexts)    # duplicate entries mean distribution is correct, abusing memory space a bit, how's that gonna scale...
        log.debug(site)
        page = random.choice(site.pages) if len(site.pages) else '/'
        std_dev = np.std(self.durations)
        print("mean %s" % np.mean(self.durations))
        print("std_dev %s" % std_dev)
        seconds = np.mean(self.durations) + ((random.random() * std_dev) - std_dev/2)
        print("seconds %s" % seconds)
        seconds = (random.random() * (MAX_DURATION/2)) + (MAX_DURATION/2) if seconds == 0.0 else seconds # if we dont have time info, make it up
        return "%s%s" % (site.host, page), int(seconds * 1000)

    def __str__(self):
        return "%s\n\t%s, %s\n\t%s\n" % (self.host, np.mean(self.durations), np.std(self.durations), self.pages)


def find_future(user_id):
    visits = model.fetch_visits(user_id)
    current = visits[-1]
    visits = visits[:-1]    # dont include current site in analysis
    v = n = 0
    site = Site.get(visits[0]['host'])
    while v < len(visits):
        while n < len(visits) and visits[v]['host'] == visits[n]['host']:
            if visits[n]['page'] != '/':    # more interesting to go to deeper paths
                site.pages.append(visits[n]['page'])
            n += 1     
        if n != len(visits):
            duration = visits[n]['t'] - visits[v]['t']
            next_site = Site.get(visits[n]['host'])
            if next_site.host != "NONE":
                site.nexts.append(next_site)
        else:
            duration = visits[n - 1]['t'] - visits[v]['t']
        site.durations.append(min(duration, MAX_DURATION))
        site = next_site
        v = n
    del Site.sites['NONE']
    # for host, site in Site.sites.items():
    #     log.debug(site)
    future = Site.get(current['host']).find_next()
    log.info("FUTURE: %s" % (future,))
    return future


if __name__ == "__main__":
    # user_id = "abaa56f20901eeca813cb72bb8544009"
    user_id = "44df95d0fb745dac15367fe7c2296706"
    t = time.clock()
    find_future(user_id)
    log.info("%fms" % ((time.clock() - t) * 1000))
