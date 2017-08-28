# -*- coding:utf-8 -*-

from waker import waker
from datetime import datetime
from tornado_json.requesthandlers import APIHandler
from tornado_json.exceptions import api_assert
from tornado_json import schema
from settings import ALARM_LEVELS
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.cron.fields import DayOfWeekField

WEEKDAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
TIME_FORMAT = "%H:%M:%S"
TIME_PATTERN = "[0-2]\d:[0-5]\d:[0-5]\d"

class rules_hendler(APIHandler):
    __urls__ = ["/api/rules/?"]
    __url_names__ = []

    @schema.validate(
        output_schema = {
            "type":"array",
            "items": {
                "type": "object",
                "properties": {
                    "time":{"type": "string", "pattern":TIME_PATTERN},
                    "weekdays":{
                        "type":"array",
                        "items":{"enum":WEEKDAYS}
                    },
                    "id": {"type": ["string","null"], "pattern":"[0-9a-f]{32}"},
                    "sound_id": {"type": ["string","null"], "pattern":"[0-9a-f]{32}"},
                    "level": {"enum":ALARM_LEVELS},
                    "repeat": {"type": "number"}
                }
            }
        },
        output_example = [
            {
                "time": "09:30:00",
                "weekdays":["sat", "sun", "mon"],
                "id": "586bc7d3dc2a4696bef5ea71ae5a0413",
                "sound_id": "e0d2bb157aa4b43ce69ff3dccc2dd81d",
                "level": "alarm",
                "repeat": 0,
            }
        ]
    )
    def get(self):
        """
        get list of scheduled alarms.

        ### output
        * `time`: colon(":") splitted time. (i.e. 09:30:00) this value means when alarm go off. 
        * `weekdays`: list of "day of week".  
        * `id`: random 32byte hexadecimal string.
        * `sound_id`: random 32byte hexadecimal string.
        * `level`: type of alarm. (i.e. "alarm","notify","warning")
        * `repeat`: number of repeat sound. 0 means "repeats indefinitely".
        """
        jobs = filter(lambda x:isinstance(x.trigger, CronTrigger), waker().scheduler.get_jobs())
        jobs_lst = []
        for i in jobs:
            t = i.next_run_time.time().strftime(TIME_FORMAT)
            week_of_day_obj = list(filter(lambda x:isinstance(x, DayOfWeekField), i.trigger.fields))[0]
            week_of_day = [str(x) for x in week_of_day_obj.expressions]
            job = {
                "id": i.id,
                "time": t,
                "week_of_day": week_of_day
            }
            job.update(i.kwargs)
            jobs_lst.append(job)
        return jobs_lst

    @schema.validate(
        input_schema = {
            "type":"object",
            "required":["time","weekdays","level","repeat"],
            "properties":{
                "time":{"type": "string", "pattern":TIME_PATTERN},
                "weekdays":{
                    "type":"array",
                    "items":{"enum":WEEKDAYS}
                },
                "sound_id":{"type":"string", "pattern":"[0-9a-f]{32}"},
                "level":{"enum":ALARM_LEVELS},
                "repeat":{"type":"number"}
            }
        },
        input_example = {
            "time": "09:30:00",
            "weekdays":["sat", "sun", "mon"],
            "sound_id":"e0d2bb157aa4b43ce69ff3dccc2dd81d",
            "level":"alarm",
            "repeat":0
        },
        output_schema = {
            "type":"string"
        },
        output_example = "68d21c9612a34559b593e8001c2d0b87"
    )
    def post(self):
        """
        post new alarm schedule. returns job id.

        ### input
        * `time`: colon(":") splitted time. (i.e. 09:30:00) this value means when alarm go off. 
        * `weekdays`: list of "day of week".  
        * `sound_id`: random 32byte hexadecimal string. you can get filename->sound_id correspondence from /api/musics/. if not set this value, waker may choose music randomly from same "level".
        * `level`: type of alarm. (i.e. "alarm","notify","warning")
        * `repeat`: number of repeat sound. 0 means "repeats indefinitely".
        ### output
        job id.
        """

        d = datetime.strptime(self.body["time"], TIME_FORMAT)

        day_of_week = ",".join(self.body["weekdays"])

        sound_id = None
        if("sound_id" in self.body):
            # TODO: ここに存在しないsound_idが来たときのエラー判定を挟む
            sound_id = self.body["sound_id"]

        level = self.body["level"]

        repeat = self.body["repeat"]
        if(repeat < 0):
            api_assert(False, log_message="repeat must be higer than zero.")
            return
        
        job = waker().scheduler.add_job(waker.alarm_go_off, "cron", hour=d.hour, minute=d.minute, second=d.second, day_of_week=day_of_week, kwargs={"repeat":repeat, "level":level, "sound_id":sound_id})
        return job.id