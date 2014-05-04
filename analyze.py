#!/usr/bin/env python3

import json, model, random, time
import numpy as np
from housepy import config, log

MAX_DURATION = 15 * 60  # you're not really spending more than 15 minutes on a site ;)

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
                site.durations.append(min(duration, MAX_DURATION))
            site = next_site
            v = n
        if 'NONE' in Site.sites:
            del Site.sites['NONE']

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
        log.debug("nexts %s" % list(set([next.host for next in self.nexts])))
        if not len(self.nexts):                 # new site, not enough info, choose most common site            
            site = max([site for site in Site.sites.values() if site != self], key=lambda site: len(site.durations))            
            log.debug("UIQUE SITE %s" % [site.host for site in Site.sites.values() if site != self])
        else:
            site = random.choice(self.nexts)    # duplicate entries mean distribution is correct, abusing memory space a bit, how's that gonna scale...
        log.debug("SITE PAGES: %s" % site.pages)
        page = random.choice(site.pages) if len(site.pages) else '/'
        std_dev = np.std(self.durations)
        seconds = np.mean(self.durations) + ((random.random() * std_dev) - std_dev/2)
        seconds = (random.random() * (MAX_DURATION/2)) + (MAX_DURATION/2) if seconds == 0.0 else seconds # if we dont have time info, make it up
        # return "%s%s" % (site.host, page), int(seconds * 1000)
        return "http://%s%s" % (site.host, page), 10000

    def __str__(self):
        return "%s\n\t%s, %s\n\t%s\n" % (self.host, np.mean(self.durations), np.std(self.durations), self.pages)


def find_future(user_id, host):
    Site.build_model(user_id, host)
    if __name__ == "__main__":
        for host, site in Site.sites.items():
            log.debug(site)
    if len(Site.sites) < 2:                                    # the model is too small
        return None
    future = Site.get(host).find_next()
    log.info("--> future: %s" % (future,))
    return future        


if __name__ == "__main__":
    user_id = "e39b180fde96525298a0ff09ad229a2e"
    t = time.clock()
    future = find_future(user_id, "twitter.com")
    log.debug(future)
    log.info("%fms" % ((time.clock() - t) * 1000))
