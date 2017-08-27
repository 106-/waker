# -*- coding:utf-8 -*-

import threading

class musics:
    _instance = None
    _lock = threading.Lock()

    def __new__(self):
        if not self._instance:
            self._lock.acquire()
            self._instance = super().__new__(self)
            self._lock.release()
        return self._instance

    