#!/usr/bin/env python3

import json, model, random, time, math, novelty_generator
import numpy as np
from housepy import config, log

MIN_DURATION = .17 * 60  # let's not make it too flippy, minimum on a site
MAX_DURATION =  10 * 60  # you're not really spending more than this on a site ;)
MIN_MODEL_SIZE = 8       # don't do anything until we have a decent model
NOV_MODEL_SIZE = 20      # don't work in novelty util a significant model has been established
JUMP_PROB = .15          # any node in the chain includes JUMP_PROB of transitioning to a random node

class Model(object):

    sites = {}

    @classmethod
    def build(cls, user_id, host):
        if host == "NONE":
            return None
        visits = model.fetch_visits(user_id)
        if len(visits) < 2:
            return None
        visits = visits[:-1] if visits[-1]['host'] == host else visits     # dont include current site in analysis
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
        if 'NONE' in Model.sites:
            del Model.sites['NONE']
        log.info("Model size: %s" % len(Model.sites))
        return True

    @classmethod
    def get(cls, host):
        if not host in cls.sites:
            cls.sites[host] = Model(host)
        return cls.sites[host]

    @classmethod
    def calc_novelty(cls):
        total_visits = sum([len(site.durations) for site in cls.sites.values()])
        novelty = len(cls.sites) / total_visits
        log.info("Novelty: %s" % novelty)
        return novelty

    @classmethod
    def sites_exclude(cls, current):
        return [site for site in cls.sites.values() if site != current]

    def __init__(self, host):
        self.host = host
        self.durations = []        
        self.nexts = []
        self.pages = []        
        
    def find_next(self):
        if len(self.durations):
            std_dev = np.std(self.durations)
            seconds = np.mean(self.durations) + ((random.random() * std_dev) - std_dev/2)
        else:
            seconds = 0.0
        seconds = (random.random() * (MAX_DURATION - MIN_DURATION)) + MIN_DURATION if seconds == 0.0 else seconds # if we dont have time info, make it up            

        if len(Model.sites) >= max(2, NOV_MODEL_SIZE) and random.random() <= Model.calc_novelty():
            url = novelty_generator.get_url()
            return "CLEAR", url, int(seconds * 1000)    # kinda hacky

        else:
            if random.random() > JUMP_PROB:             # follow the chain
                if not len(self.nexts):                 # new site, not enough info, choose most common site            
                    site = max(Model.sites_exclude(self), key=lambda site: len(site.durations))
                else:
                    site = random.choice(self.nexts)    # duplicate entries mean prob distribution is correct, abusing memory space a bit, how's that gonna scale...
            else:                                       
                site = random.choice(Model.sites_exclude(self))              # jump the chain to a random site in the model
            page = random.choice(site.pages) if len(site.pages) else '/'     # keep with deep paths if possible
            return site.host, page, int(seconds * 1000)


    def __str__(self):
        return "%s\n\t%f, %f\n\t%s\n" % (self.host, np.mean(self.durations) if len(self.durations) else 0.0, np.std(self.durations) if len(self.durations) else 0.0, self.pages)


def find_future(user_id, host):
    if Model.build(user_id, host) is None:
        return None
    if __name__ == "__main__":
        for host, site in Model.sites.items():
            log.debug(site)
        log.debug("Novelty: %f" % Model.calc_novelty())
    if len(Model.sites) < max(2, MIN_MODEL_SIZE):                                # the model is too small
        return None
    future = Model.get(host).find_next()
    return future        


if __name__ == "__main__":
    user_id = "e29d909b34d7ced11f67440a74f95f1e"
    t = time.clock()
    future = find_future(user_id, "twitter.com")
    log.debug(future)
    log.info("%fms" % ((time.clock() - t) * 1000))
