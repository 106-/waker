# -*- coding:utf-8 -*-

from waker import waker
from music_controller import music_controller
from datetime import datetime
from tornado_json.requesthandlers import APIHandler
from tornado_json.exceptions import api_assert
from tornado_json import schema
from settings import ALARM_LEVELS
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.cron.fields import DayOfWeekField

day_of_weeks = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
TIME_FORMAT = "%H:%M:%S"
TIME_PATTERN = "[0-2]\d:[0-5]\d:[0-5]\d"
CRONJOB_POST_OBJECT = {
    "type": "object",
    "required": ["time", "day_of_week", "level", "repeat"],
    "properties": {
        "time":{"type": "string", "pattern":TIME_PATTERN},
        "day_of_week":{
            "type":"array",
            "items":{"enum":day_of_weeks}
        },
        "sound_id": {"type": ["string","null"], "pattern":"[0-9a-f]{32}"},
        "level": {"enum":ALARM_LEVELS},
        "repeat": {
            "type": "number",
            "minimum": 0
        }
    }
}
CRONJOB_POST_EXAMPLE = {
    "time": "09:30:00",
    "day_of_week":["sat", "sun", "mon"],
    "sound_id": "e0d2bb157aa4b43ce69ff3dccc2dd81d",
    "level": "alarm",
    "repeat": 0,
}
CRONJOB_OBJECT = CRONJOB_POST_OBJECT.copy()
CRONJOB_OBJECT["properties"]["id"] = {"type": "string", "pattern":"[0-9a-f]{32}"}
del CRONJOB_OBJECT["required"]
CRONJOB_EXAMPLE = CRONJOB_POST_EXAMPLE.copy()
CRONJOB_EXAMPLE["id"] = "586bc7d3dc2a4696bef5ea71ae5a0413"

def make_cronobj_from_job(job):
    t = job.next_run_time.time().strftime(TIME_FORMAT)
    day_of_week = get_dayofweek_list_from_job(job)
    job_dict = {
        "id": job.id,
        "time": t,
        "day_of_week": day_of_week
    }
    job_dict.update(job.kwargs)
    return job_dict

def get_dayofweek_list_from_job(job):
    day_of_week_obj = list(filter(lambda x:isinstance(x, DayOfWeekField), job.trigger.fields))[0]
    day_of_week = [str(x) for x in day_of_week_obj.expressions]
    return day_of_week

class rules_hendler(APIHandler):
    __urls__ = ["/api/rules/?"]
    __url_names__ = []

    @schema.validate(
        output_schema = {
            "type":"array",
            "items": CRONJOB_OBJECT
        },
        output_example = [
            CRONJOB_EXAMPLE
        ]
    )
    def get(self):
        """
        get list of scheduled alarms.

        ### output
        * `time`: colon(":") splitted time. (i.e. 09:30:00) this value means when alarm go off. 
        * `day_of_week`: list of "day of week".  
        * `id`: random 32byte hexadecimal string.
        * `sound_id`: random 32byte hexadecimal string.
        * `level`: type of alarm. (i.e. "alarm","notify","warning")
        * `repeat`: number of repeat sound. 0 means "repeats indefinitely".
        """
        jobs = filter(lambda x:isinstance(x.trigger, CronTrigger), waker().scheduler.get_jobs())
        jobs_lst = []
        for i in jobs:
            jobs_lst.append(make_cronobj_from_job(i))
        return jobs_lst

    @schema.validate(
        input_schema = CRONJOB_POST_OBJECT,
        input_example = CRONJOB_POST_EXAMPLE,
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
        * `day_of_week`: list of "day of week".  
        * `sound_id`: random 32byte hexadecimal string. you can get filename->sound_id correspondence from /api/musics/. if not set this value, waker may choose music randomly from same "level".
        * `level`: type of alarm. (i.e. "alarm","notify","warning")
        * `repeat`: number of repeat sound. 0 means "repeats indefinitely".
        ### output
        job id.
        """

        d = datetime.strptime(self.body["time"], TIME_FORMAT)

        day_of_week = ",".join(self.body["day_of_week"])

        sound_id = None
        if("sound_id" in self.body):
            sound_id = self.body["sound_id"]
            mc = music_controller()
            if not mc.exist(sound_id):
                api_assert(False, log_message="such sound_id is not exists.")
                return

        level = self.body["level"]
        repeat = self.body["repeat"]
        job = waker().scheduler.add_job(waker.alarm_go_off, "cron", hour=d.hour, minute=d.minute, second=d.second, day_of_week=day_of_week, kwargs={"repeat":repeat, "level":level, "sound_id":sound_id})
        return job.id

class rule_handler(rules_hendler):
    __urls__ = ["/api/rules/(?P<id>[0-9a-f]{32})/?$"]

    @schema.validate(
        output_schema = CRONJOB_OBJECT,
        output_example = CRONJOB_EXAMPLE
    )
    def get(self, id):
        job = waker().scheduler.get_job(id)
        if(not job):
            api_assert(False, log_message="no such rule.")
            return
        job_dict = make_cronobj_from_job(job)
        return job_dict

    @schema.validate(
        input_schema = CRONJOB_OBJECT,
        input_example = CRONJOB_EXAMPLE,
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
        mc = music_controller()
        if not mc.exist(mod_args["sound_id"]):
            api_assert(False, log_message="such sound_id is not exists.")
            return
        mod_day_of_week = get_dayofweek_list_from_job(job)
        if("day_of_week" in self.body):
            mod_day_of_week = self.body["day_of_week"]
        mod_day_of_week = ",".join(mod_day_of_week)

        d = job.next_run_time.time()
        if("time" in self.body):
            d = datetime.strptime(self.body["time"], TIME_FORMAT)
        
        mod_trigger = CronTrigger(hour=d.hour, minute=d.minute, second=d.second, day_of_week=mod_day_of_week)
        job.modify(kwargs=mod_args)
        job.reschedule(mod_trigger)
    
    @schema.validate()
    def delete(self, id):
        job = waker().scheduler.get_job(id)
        if(not job):
            api_assert(False, log_message="no such alarm.")
            return
        job.remove()
