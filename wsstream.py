# -*- coding:utf-8 -*-

import threading
from tornado.websocket import WebSocketHandler

class wsstream(WebSocketHandler):
    _connections = set()

    def open(self):
        self._connections.add(self)
    
    def on_close(self):
        self._connections.remove(self)
    
    @classmethod
    def broadcast(self, msg):
        for i in self._connections:
            i.write_message(msg)