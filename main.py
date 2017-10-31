#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import json
import logging
import wsstream
from datetime import datetime, timedelta
from waker import waker
from music_controller import music_controller
from tornado.ioloop import IOLoop
from tornado_json.routes import get_routes
from tornado_json.application import Application

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(message)s", level=logging.DEBUG)

def tick(type, repeat, sound_id):
    logging.info(("%s %d %s") % (type, repeat, sound_id))

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    wkr = waker()

    import api
    routes = get_routes(api)
    routes.append(("/ws", wsstream.wsstream))
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