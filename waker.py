# -*- coding:utf-8 -*-

import threading
import logging
import pygame
import json
from music_controller import music_controller
from apscheduler.schedulers.tornado import TornadoScheduler
from settings import *
from wsstream import wsstream

class waker:
    _instance = None
    _lock = threading.Lock()
    _isplayingmusic = False
    _music = None
    _alarm_data = None

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
            cls._alarm_data = {
                "level": level,
                "sound_id" : sound_id,
                "repeat": repeat,
                "sound_name": m.sound_name
            }
            wsdata = cls._alarm_data
            wsdata.update({"event":"ALARM_GO_OFF"})
            wsstream.broadcast(json.dumps(wsdata))
            m.play(repeat)
            cls._isplayingmusic = True
            cls._music = m
            return True
        else:
            logging.warn("waker is already playing music.")
            return False

    @classmethod
    def alarm_stop(cls):
        if cls._isplayingmusic:
            wsdata = cls._alarm_data
            wsdata.update({"event":"ALARM_STOPPED"})
            wsstream.broadcast(json.dumps(wsdata))
            cls._music.stop()
            cls._isplayingmusic = False
            wsstream.broadcast("alarm stopped.")
            return True
        else:
            logging.warn("waker is not playing music.")
            return False