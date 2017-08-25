#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging
from settings import *
from tornado.ioloop import IOLoop
from apscheduler.schedulers.tornado import TornadoScheduler

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    scheduler = TornadoScheduler()
    scheduler.add_jobstore('redis', REDIS_HOST, REDIS_PORT)
    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Interrupted.")

if __name__=='__main__':
    main()