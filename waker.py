# -*- coding:utf-8 -*-

import threading
import logging
from apscheduler.schedulers.tornado import TornadoScheduler
from settings import *

class waker:
    _instance = None
    _lock = threading.Lock()

    def __new__(self):
        if not self._instance:
            self._lock.acquire()
            self._instance = super().__new__(self)
            self.scheduler = TornadoScheduler()
            self.scheduler.add_jobstore('redis', host=REDIS_HOST, port=REDIS_PORT)
            self.scheduler.start()
            self._lock.release()
        return self._instance

    @classmethod
    def alarm_go_off(cls, repeat, level, sound_id):
        logging.info("sound_id: {}, repeat: {}, level: {}".format(sound_id, repeat, level))
    
    def alarm_stop(self):
        pass
    
    def schedule_update(self):
        pass
    
    def schedule_remove(self):
        pass