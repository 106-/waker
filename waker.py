# -*- coding:utf-8 -*-

import threading
import logging
import pygame
from music_controller import music_controller
from apscheduler.schedulers.tornado import TornadoScheduler
from settings import *

class waker:
    _instance = None
    _lock = threading.Lock()
    _isplayingmusic = False
    _music = None

    def __new__(self):
        if not self._instance:
            self._lock.acquire()
            self._instance = super().__new__(self)
            self.scheduler = TornadoScheduler()
            self.scheduler.add_jobstore('redis', host=REDIS_HOST, port=REDIS_PORT)
            self.scheduler.start()
            pygame.init()
            self._lock.release()
        return self._instance

    @classmethod
    def alarm_go_off(cls, repeat, level, sound_id):
        logging.info("sound_id: {}, repeat: {}, level: {}".format(sound_id, repeat, level))
        if not cls._isplayingmusic:
            mc = music_controller()
            m = mc.get(sound_id)
            m.play(repeat)
            cls._isplayingmusic = True
            cls._music = m
        else:
            logging.warn("waker is already playing music.")

    @classmethod
    def alarm_stop(cls):
        if cls._isplayingmusic:
            cls._music.stop()
            cls._isplayingmusic = False
        else:
            logging.warn("waker is not playing music.")
    
    @classmethod
    def schedule_update(cls):
        pass
    
    @classmethod
    def schedule_remove(cls):
        pass