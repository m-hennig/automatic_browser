#!/usr/bin/env python3

import json, model
import numpy as np

visits = model.fetch_visits('abaa56f20901eeca813cb72bb8544009')

print(json.dumps(visits, indent=4))


class Site(object):

    sites = {}

    @classmethod
    def get(cls, host):
        if not host in cls.sites:
            cls.sites[host] = Site(host)
        return cls.sites[host]

    def __init__(self, host):
        self.host = host
        self.pages = []
        self.durations = []        

    def add(self, page, duration):
        self.pages.append(page)
        self.durations.append(duration)

    @property
    def duration(self):
        return np.mean(self.durations), np.std(self.durations)

    def __ref__(self):
        return "%s" % self.host

sites = []
for v in range(len(visits) - 1):
    duration = visits[v + 1]['t'] - visits[v]['t']
    site = Site.get(visits[v]['host'])
    site.add(visits[v]['page'], duration)
    if site not in sites:
        sites.append(site)

for site in sites:
    print(site.duration)