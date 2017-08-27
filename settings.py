# -*- coding:utf-8 -*-

import datetime

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '7001'

ALARM_LEVELS = ["alarm", "notify", "warning"]
TIMEZONE = datetime.timezone( datetime.timedelta(hours=9) )