# -*- coding:utf-8 -*-

from waker import waker
from tornado_json.requesthandlers import APIHandler
from tornado_json import schema

sche = [
    {
        "name":"sa",
        "time":"sometime"
    }
]

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
                    "id": {"type": "string"},
                    "sound_id": {"type": "string"},
                    "class": {"type": "string"},
                    "repeat": {"type": "number"}
                }
            }
        },
        output_example = [
            {
                "time": "2017-08-26T00:00:00.000000+09:00",
                "id": "586bc7d3dc2a4696bef5ea71ae5a0413",
                "sound_id": "e0d2bb157aa4b43ce69ff3dccc2dd81d",
                "class": "alarm",
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
        * `class`: type of alarm. (i.e. "alarm","notify","warning")
        * `repeat`: number of repeat sound. 0 means "repeats indefinitely".
        """
        jobs = waker.scheduler.get_jobs()
        jobs_lst = []
        for i in jobs:
            job = {
                "id": i.id,
                "time": i.next_run_time.isoformat(),
            }
            datas = dict(tuple([(k, v) for (k, v) in zip(["class", "repeat", "sound_id"], i.args)]))
            job.update(datas)
            jobs_lst.append(job)
        return jobs_lst

class schedule_handler(schedules_handler):
    __urls__ = ["/api/schedules/(?P<num>[0-9]+)/?$"]

    def get(self, num):
        try:
            self.success(sche[int(num)])
        except:
            self.fail("No such data.")