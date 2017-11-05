# -*- coding:utf-8 -*-

import datetime

REDIS_HOST = '127.0.0.1'
REDIS_PORT = '7001'

ALARM_LEVELS = ["alarm", "notify", "warning"]

# 時計針の回し方、私次第かも!
TIMEZONE = datetime.timezone( datetime.timedelta(hours=9) )

SOUND_MIMETYPES = ["audio/mp3", "audio/mpeg"]