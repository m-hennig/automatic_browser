#!/usr/bin/env python3

import os, tornado, json, random, model, hashlib, time
from housepy import config, log, strings, process, server, util

process.secure_pid(os.path.join(os.path.dirname(__file__), "run"))

class Home(server.Handler):

    def get(self, page=None):
        return self.render("blank.html")

    def post(self, nop=None):
        action = self.get_argument("action", None)     
        self.set_header("Access-Control-Allow-Origin", "*")     
        if action is None:
            return self.error("Bad Action")
        if action == "new_user":
            return self.new_user()
        if action == "report":
            return self.receive_report()
        if action == "get_model":
            pass

    def new_user(self):
        log.info("Home.new_user")
        user_id = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()        
        return self.text(user_id)

    def receive_report(self):   
        log.info("Home.receive_report")
        user_id = self.get_argument("user_id")
        url = self.get_argument("url")
        model.insert_visit(user_id, url)
        return self.text("OK")


def main():
    handlers = [
        (r"/?([^/]*)", Home),
    ]
    server.start(handlers)      
                     
if __name__ == "__main__":
    main()

