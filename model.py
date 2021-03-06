#!/usr/bin/env python3

import sqlite3, json, time, sys, os
from housepy import config, log, util

def db_call(f):
    def wrapper(*args):
        connection = sqlite3.connect(os.path.abspath(os.path.join(os.path.dirname(__file__), "data.db")))
        connection.row_factory = sqlite3.Row
        db = connection.cursor()
        results = f(db, *args)
        connection.commit()
        connection.close()
        return results
    return wrapper

@db_call
def init(db):
    try:
        db.execute("CREATE TABLE IF NOT EXISTS visits (user_id TEXT, t INTEGER, host TEXT, page TEXT, auto BOOLEAN)")
        db.execute("CREATE INDEX IF NOT EXISTS t_key ON visits(t)")
    except Exception as e:
        log.error(log.exc(e))
        return
init()

@db_call
def insert_visit(db, user_id, host, page, auto):
    t = util.timestamp()
    try:
        db.execute("INSERT INTO visits (user_id, t, host, page, auto) VALUES (?, ?, ?, ?, ?)", (user_id, t, host, page, auto))
        entry_id = db.lastrowid
    except Exception as e:
        log.error(log.exc(e))
        return
    log.info("Inserted visit (%s) %s [%s] [%s] %s" % (t, user_id, host, page, auto))    
    return entry_id

@db_call
def fetch_visits(db, user_id):
    # min_t = util.timestamp() - (7 * 24 * 60 * 60)
    # db.execute("SELECT t, host, page, auto FROM visits WHERE user_id=? AND t > ? ORDER BY t", (user_id, min_t)) # entries from the last week
    db.execute("SELECT t, host, page, auto FROM visits WHERE user_id=? ORDER BY t LIMIT 500", (user_id,))   # last 1000 entries
    visits = [dict(visit) for visit in db.fetchall()]
    return visits