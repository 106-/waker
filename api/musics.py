# -*- coding:utf-8 -*-

from music_controller import music_controller
from tornado_json.requesthandlers import APIHandler
from tornado_json.exceptions import api_assert
from tornado_json import schema
from settings import ALARM_LEVELS,SOUND_MIMETYPES

class musics_handler(APIHandler):
    __urls__ = ["/api/musics/?"]
    __url_names__ = []

    @schema.validate(
        output_schema = {
            "type":"array",
            "items":{
                "type":"object",
                "properties":{
                    "id": {"type": "string", "pattern":"[0-9a-f]{32}"},
                    "sound_name": {"type": "string"},
                    "level": {"enum": ALARM_LEVELS}
                }
            }
        },
        output_example = [
            {
                "id":"349d3d3eda958f2d0d004394043e9af1",
                "sound_name": "the fine everyday.mp3",
                "level": "alarm"
            }
        ]
    )
    def get(self):
        mc = music_controller()
        m = mc.get_list()
        return m

    @schema.validate()
    def post(self):
        level = self.get_argument("level", default=None)
        if not level in ALARM_LEVELS:
            api_assert(False, log_message="no such alarm level.")
            return

        files = self.request.files
        if not "data" in files:
            api_assert(False, log_message="sound data(mp3) is required.")
            return
        file = files["data"][0]
        if not file["content_type"] in SOUND_MIMETYPES:
            api_assert(False, log_message="This file is not supported.({})".format(file["content_type"]))
        
        sound_name = self.get_argument("sound_name", default=None)
        if not sound_name:
            sound_name = file["filename"]
        data = file["body"]

        mc = music_controller()
        mc.add(data, sound_name, level)

class music_handler(musics_handler):
    __urls__ = ["/api/musics/(?P<id>[0-9a-f]{32})/?$"]

    def _check_valid_id(func):
        def wrap(self, id):
            mc = music_controller()
            if not mc.exist(id):
                api_assert(False, status_code=404, log_message="no such sound_id.")
            return func(self, id)
        return wrap

    @schema.validate(
        output_schema = {
            "type":"object",
            "properties":{
                "id": {"type": "string", "pattern":"[0-9a-f]{32}"},
                "sound_name": {"type": "string"},
                "level": {"enum": ALARM_LEVELS}
            }
        },
        output_example = {
            "id":"349d3d3eda958f2d0d004394043e9af1",
            "sound_name": "the fine everyday.mp3",
            "level": "alarm"
        }
    )
    @_check_valid_id
    def get(self, id):
        mc = music_controller()
        m = mc.get(id)
        music_dict = {
            "id":m.id,
            "name":m.sound_name,
            "level":m.level
        }
        return music_dict
    
    @schema.validate(
        input_schema = {
            "type":"object",
            "properties":{
                "sound_name": {"type": "string"},
                "level": {"enum": ALARM_LEVELS}
            }
        },
        input_example = {
            "sound_name": "the fine everyday.mp3",
            "level": "alarm"
        }
    )
    @_check_valid_id
    def put(self, id):
        mc = music_controller()
        mc.modify(id, self.body)

    @schema.validate()
    @_check_valid_id
    def delete(self, id):
        mc = music_controller()
        mc.delete(id)