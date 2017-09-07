# -*- coding:utf-8 -*-

from settings import REDIS_HOST, REDIS_PORT
import threading
import redis
import random

string_src = "abcdef0123456789"
redis_music_key = "waker:music"
redis_music_hash_key = "waker:music:{}"

class music_controller:
    _instance = None
    _lock = threading.Lock()

    def __new__(self):
        if not self._instance:
            self._lock.acquire()
            self._instance = super().__new__(self)
            self._redis = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
            self._lock.release()
        return self._instance

    def add(self, data, sound_name, level="alarm"):
        id = "".join([random.choice(string_src) for x in range(32)])
        m = {
            "data":data,
            "sound_name":sound_name,
            "level":level
        }
        self._redis.sadd(redis_music_key, id)
        self._redis.hmset(redis_music_hash_key.format(id), m)
    
    def exist(self, id):
        return self._redis.sismember(redis_music_key, id)

    def delete(self, id):
        if self._redis.sismember(redis_music_key, id):
            self._redis.srem(redis_music_key, id)
            self._redis.delete(redis_music_hash_key.format(id))
            return True
        else:
            return False
    
    def get(self, id=None):
        if id is None:
            id = self._redis.srandmember(redis_music_key)

        if self._redis.sismember(redis_music_key, id):
            keys = ["data", "sound_name", "level"]
            m = self._get_music_dict(id, keys)
            return music(**m)
        else:
            return None
    
    def get_list(self):
        music_set = self._redis.smembers(redis_music_key)
        musics = []
        for i in music_set:
            keys = ["sound_name", "level"]
            musics.append(self._get_music_dict(i, keys))
        return musics

    def _get_music_dict(self, id, keys):
        music_dict = {"id": id}
        values = self._redis.hmget(redis_music_hash_key.format(id.decode("utf-8")), *keys)
        music_dict.update(dict(zip(keys, values)))
        return music_dict

class music:
    def __init__(self, id, sound_name, level, data):
        self.id = id
        self.sound_name = sound_name
        self.level = level
        self.data = data
    
    def play(self):
        pass