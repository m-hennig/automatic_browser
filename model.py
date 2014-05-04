#!/usr/bin/env python3

import sqlite3, json, time, sys, os
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

def insert_visit(user_id, host, page):
    t = util.timestamp()
    try:
        db.execute("INSERT INTO visits (user_id, t, host, page) VALUES (?, ?, ?, ?)", (user_id, t, host, page))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    connection.commit()
    log.info("Inserted visit (%s) %s %s %s" % (t, user_id, host, page))    
    return entry_id

def fetch_visits(user_id):
    db.execute("SELECT t, host, page FROM visits WHERE user_id=? ORDER BY t", (user_id,))
    visits = [dict(visit) for visit in db.fetchall()]
    return visits
