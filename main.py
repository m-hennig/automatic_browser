#!/usr/bin/env python3

import os, tornado, json, random, model, hashlib, time
from housepy import config, log, strings, process, server, util
from analyze import find_future

process.secure_pid(os.path.join(os.path.dirname(__file__), "run"))

class Home(server.Handler):

    def get(self, page=None):
        return self.render("home.html")

    def post(self, nop=None):
        action = self.get_argument("action", None)     
        self.set_header("Access-Control-Allow-Origin", "*")     
        if action is None:
            return self.error("Bad Action")
        if action == "new_user":
            return self.new_user()
        if action == "report":
            return self.report()

    def new_user(self):
        log.info("Home.new_user")
        user_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()        
        log.info("--> %s" % user_id)
        return self.text(user_id)

    def report(self):   
        log.info("Home.report")
        user_id = self.get_argument("user_id")
        host = self.get_argument("host")
        page = self.get_argument("page")
        auto = self.get_argument("auto") == "true"
        active = self.get_argument("active") == "true"
        model.insert_visit(user_id, host, page, auto)
        if not active:
            log.info("--> not active")
            return self.text("NOFUTURE")            
        future = find_future(user_id, host)
        if future is None:
            log.info("--> no future")
            return self.text("NOFUTURE")
        else:
            log.info("--> future: %s" % (future,))
        return self.text("%s %s %s" % future)


def main():
    handlers = [
        (r"/?([^/]*)", Home),
    ]
    server.start(handlers)      
                     
if __name__ == "__main__":
    main()

