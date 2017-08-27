# -*- coding:utf-8 -*-

import iso8601
import datetime
from waker import waker
from tornado_json.requesthandlers import APIHandler
from tornado_json.exceptions import api_assert
from tornado_json import schema
from settings import ALARM_LEVELS,TIMEZONE

class schedules_handler(APIHandler):
    __urls__ = ["/api/schedules/?"]
    __url_names__ = []

    @schema.validate(
        output_schema = {
            "type":"array",
            "items": {
                "type": "object",
                "properties": {
                    "time":{"type": "string"},
                    "id": {"type": "string", "pattern":"[0-9a-f]{32}"},
                    "sound_id": {"type": "string", "pattern":"[0-9a-f]{32}"},
                    "level": {"enum":ALARM_LEVELS},
                    "repeat": {"type": "number"}
                }
            }
        },
        output_example = [
            {
                "time": "2017-08-26T00:00:00.000000+09:00",
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

        * `time`: ISO8601 formatted string. this value means when alarm go off. 
        * `id`: random 32byte hexadecimal string.
        * `sound_id`: random 32byte hexadecimal string.
        * `level`: type of alarm. (i.e. "alarm","notify","warning")
        * `repeat`: number of repeat sound. 0 means "repeats indefinitely".
        """
        jobs = waker().scheduler.get_jobs()
        jobs_lst = []
        for i in jobs:
            job = {
                "id": i.id,
                "time": i.next_run_time.isoformat(),
            }
            job.update(i.kwargs)
            jobs_lst.append(job)
        return jobs_lst

    @schema.validate(
        input_schema = {
            "type":"object",
            "required":["time","level","repeat"],
            "properties":{
                "time":{"type":"string"},
                "sound_id":{"type":"string", "pattern":"[0-9a-f]{32}"},
                "level":{"enum":ALARM_LEVELS},
                "repeat":{"type":"number"}
            }
        },
        input_example = {
            "time":"2017-08-26T00:00:00.000000+09:00",
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

        * `time`: ISO8601 formatted string. this value means when alarm go off.
        * `sound_id`: random 32byte hexadecimal string. you can get filename->sound_id correspondence from /api/musics/. 
                        if not set this value, waker may choose music randomly from same "level".
        * `level`: type of alarm. (i.e. "alarm","notify","warning")
        * `repeat`: number of repeat sound. 0 means "repeats indefinitely".
        """
        d = iso8601.parse_date(self.body["time"])
        if d < datetime.datetime.now(tz=TIMEZONE):
            api_assert(False, log_message="time must be later than present.")
            return

        sound_id = ""
        if("sound_id" in self.body):
            # TODO: ここに存在しないsound_idが来たときのエラー判定を挟む
            sound_id = self.body["sound_id"]

        level = self.body["level"]

        repeat = self.body["repeat"]
        if(repeat < 0):
            api_assert(False, log_message="repeat must be higer than zero.")
            return

        job = waker().scheduler.add_job(waker.alarm_go_off, "date", run_date=d, kwargs={"repeat":repeat, "level":level, "sound_id":sound_id})
        return job.id

class schedule_handler(schedules_handler):
    __urls__ = ["/api/schedules/(?P<id>[0-9a-f]{32})/?$"]

    @schema.validate(
        output_schema = {
            "type": "object",
            "properties": {
                "time":{"type": "string"},
                "id": {"type": "string", "pattern":"[0-9a-f]{32}"},
                "sound_id": {"type": "string", "pattern":"[0-9a-f]{32}"},
                "level": {"enum":ALARM_LEVELS},
                "repeat": {"type": "number"}
            }
        },
        output_example = {
            "time": "2017-08-26T00:00:00.000000+09:00",
            "id": "586bc7d3dc2a4696bef5ea71ae5a0413",
            "sound_id": "e0d2bb157aa4b43ce69ff3dccc2dd81d",
            "level": "alarm",
            "repeat": 0,
        }
    )
    def get(self, id):
        job = waker().scheduler.get_job(id)
        if(not job):
            api_assert(False, log_message="no such alarm.")
            return
        job_dict = {
            "id": job.id,
            "time": job.next_run_time.isoformat()
        }
        job_dict.update(job.kwargs)
        return job_dict

    @schema.validate(
        input_schema = {
            "type":"object",
            "properties":{
                "time":{"type":"string"},
                "sound_id":{"type":"string", "pattern":"[0-9a-f]{32}"},
                "level":{"enum":ALARM_LEVELS},
                "repeat":{"type":"number"}
            }
        },
        input_example = {
            "time":"2017-08-26T00:00:00.000000+09:00",
            "sound_id":"e0d2bb157aa4b43ce69ff3dccc2dd81d",
            "level":"alarm",
            "repeat":0
        }
    )
    def put(self, id):
        job = waker().scheduler.get_job(id)
        if(not job):
            api_assert(False, log_message="no such alarm.")
            return
        mod_args = {}
        for key in ["sound_id", "level", "repeat"]:
            if(key in self.body):
                mod_args[key] = self.body[key]
            else:
                mod_args[key] = job.kwargs[key]
        mod_time = job.next_run_time
        if("time" in self.body):
            mod_time = iso8601.parse_date(self.body["time"])
            if mod_time < datetime.datetime.now(tz=TIMEZONE):
                api_assert(False, log_message="time must be later than present.")
                return
        job.modify(next_run_time=mod_time, kwargs=mod_args)

    @schema.validate()   
    def delete(self, id):
        job = waker().scheduler.get_job(id)
        if(not job):
            api_assert(False, log_message="no such alarm.")
            return
        job.remove()