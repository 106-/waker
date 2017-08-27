#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import logging
from datetime import datetime, timedelta
from waker import waker
from tornado.ioloop import IOLoop
from tornado_json.routes import get_routes
from tornado_json.application import Application

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s", level=logging.DEBUG)

def tick(type, repeat, sound_id):
    logging.info(("%s %d %s") % (type, repeat, sound_id))

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    wkr = waker()
    wkr.scheduler.add_job(waker.alarm_go_off, 'date', run_date=datetime.now()+timedelta(seconds=10), kwargs={"repeat":1, "level":"notify", "sound_id":"0"*32})
    #wkr.scheduler.add_job(waker.alarm_go_off, kwargs={"repeat":1, "level":"notify", "sound_id":"0"*32})

    import api
    routes = get_routes(api)
    print("Routes\n======\n\n" + json.dumps(
        [(url, repr(rh)) for url, rh in routes],
        indent=2)
    )

    app = Application(routes=routes, settings={})
    app.listen(8080)

    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Interrupted.")

if __name__=='__main__':
    main()