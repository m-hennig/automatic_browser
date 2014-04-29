#!/usr/bin/env python3

import sqlite3, json, time, sys, os
from urllib.parse import urlparse
from housepy import config, log, util

connection = sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), "data.db")))
connection.row_factory = sqlite3.Row
db = connection.cursor()

def init():
    try:
        db.execute("CREATE TABLE IF NOT EXISTS visits (user_id TEXT, t INTEGER, host TEXT, page TEXT)")
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
init()

def insert_visit(user_id, url):
    t = util.timestamp()
    parts = urlparse(url)
    host, page = parts.netloc, parts.path
    if not host:
        host = page
    try:
        db.execute("INSERT INTO visits (user_id, t, host, page) VALUES (?, ?, ?, ?)", (user_id, t, host, page))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
    log.info("Inserted visit (%s) %s %s" % (t, user_id, url))    
    return entry_id

def fetch_visits(user_id):
    db.execute("SELECT t, host, page FROM visits WHERE user_id=?", (user_id,))
    visits = [dict(visit) for visit in db.fetchall()]
    return visits



# def get_protect(kind):
#     db.execute("SELECT t FROM features WHERE kind=? ORDER BY t DESC LIMIT 1", (kind,))
#     result = db.fetchone()
#     if result is None:
#         return 0
#     return result['t']

