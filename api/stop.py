# -*- coding:utf-8 -*-

from waker import waker
from tornado_json.requesthandlers import APIHandler
from tornado_json.exceptions import api_assert
from tornado_json import schema

class stop(APIHandler):
    __urls__ = ["/api/stop/?"]
    __url_names__ = []

    @schema.validate()
    def get(self):
        wkr = waker()
        if not wkr.alarm_stop():
            api_assert(False, log_message="alarm is not going off.")