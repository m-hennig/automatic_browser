#!/usr/bin/env python3

import json, model, random, time, math
import numpy as np
from housepy import config, log

MIN_DURATION = .25 * 60  # let's not make it too flippy, stan, 15s minimum
MAX_DURATION =  15 * 60  # you're not really spending more than 15 minutes on a site ;)
MIN_MODEL_SIZE = 5

class Site(object):

    sites = {}

    @classmethod
    def build_model(cls, user_id, host):
        if host == "NONE":
            return None
        visits = model.fetch_visits(user_id)
        visits = visits[:-1] if visits[-1]['host'] == host else visits     # dont include current site in analysis
        if not len(visits):
            return None
        cls.sites = {}
        v = n = 0
        site = cls.get(visits[v]['host'])
        while v < len(visits):
            while n < len(visits) and visits[v]['host'] == visits[n]['host']:
                if not visits[n]['auto']:                                  # don't include auto-browsed sites in model
                    if visits[n]['page'] != '/':                           # more interesting to stick with deeper paths
                        site.pages.append(visits[n]['page'])
                n += 1     
            if n == len(visits):
                break            
            duration = visits[n]['t'] - visits[v]['t']
            next_site = cls.get(visits[n]['host'])
            if not visits[n]['auto']:                                      # don't include auto-browsed sites in model
                if next_site.host != "NONE": 
                    site.nexts.append(next_site)
                site.durations.append(max(min(duration, MAX_DURATION), MIN_DURATION))
            site = next_site
            v = n
        if 'NONE' in Site.sites:
            del Site.sites['NONE']
        return True

    @classmethod
    def get(cls, host):
        if not host in cls.sites:
            cls.sites[host] = Site(host)
        return cls.sites[host]

    def __init__(self, host):
        self.host = host
        self.durations = []        
        self.nexts = []
        self.pages = []
        
    def find_next(self):
        if not len(self.nexts):                 # new site, not enough info, choose most common site            
            site = max([site for site in Site.sites.values() if site != self], key=lambda site: len(site.durations))            
        else:
            site = random.choice(self.nexts)    # duplicate entries mean distribution is correct, abusing memory space a bit, how's that gonna scale...
        page = random.choice(site.pages) if len(site.pages) else '/'
        if len(self.durations):
            std_dev = np.std(self.durations)
            seconds = np.mean(self.durations) + ((random.random() * std_dev) - std_dev/2)
            seconds = (random.random() * (MAX_DURATION - MIN_DURATION)) + MIN_DURATION if seconds == 0.0 else seconds # if we dont have time info, make it up
        else:
            seconds = 0.0
        return site.host, page, int(seconds * 1000)

    def __str__(self):
        return "%s\n\t%s, %s\n\t%s\n" % (self.host, np.mean(self.durations) if len(self.durations) else 0.0, np.std(self.durations) if len(self.durations) else 0.0, self.pages)


def find_future(user_id, host):
    if Site.build_model(user_id, host) is None:
        return None
    if __name__ == "__main__":
        for host, site in Site.sites.items():
            log.debug(site)
    if len(Site.sites) < max(2, MIN_MODEL_SIZE):                                # the model is too small
        return None
    future = Site.get(host).find_next()
    return future        


if __name__ == "__main__":
    user_id = "78c682d735ba528f91470076769f3e21"
    t = time.clock()
    future = find_future(user_id, "twitter.com")
    log.debug(future)
    log.info("%fms" % ((time.clock() - t) * 1000))
