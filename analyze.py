#!/usr/bin/env python3

import json, model
import numpy as np

visits = model.fetch_visits('abaa56f20901eeca813cb72bb8544009')

print(json.dumps(visits, indent=4))


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
        self.pages = []
        self.durations = []        

    @property
    def duration(self):
        return np.mean(self.durations), np.std(self.durations)

    def __str__(self):
        return "%s\t\t\t%s\t%s" % (self.host, self.duration, self.pages)

v = n = 0
while v < len(visits):
    site = Site.get(visits[v]['host'])
    while n < len(visits) and visits[v]['host'] == visits[n]['host']:
        site.pages.append(visits[n]['page'])
        n += 1     
    duration = (visits[n]['t'] if n < len(visits) else visits[n - 1]['t']) - visits[v]['t']
    site.durations.append(duration)
    v = n

for host, site in Site.sites.items():
    site.pages = list(set(site.pages))
    print(site)
