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

    def add(self, data, sound_name, type="alarm"):
        id = "".join([random.choice(string_src) for x in xrange(16)])
        m = {
            "data":data,
            "sound_name":sound_name,
            "type":type
        }
        self._redis.sadd(redis_music_key, id)
        self._redis.hmset(redis_music_hash_key.format(id), m)
    
    def exist(self, id):
        if self._redis.sismember(redis_music_key, id):
            return True
        else:
            return False

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

        if id in self._redis.sismember(redis_music_key, id):
            m = self._redis.hgetall(redis_music_hash_key.format(id))
            return music(**m)
        else:
            return None
    
    def get_list(self):
        music_set = self._redis.smembers(redis_music_key)
        get_music_list = lambda x: self._redis.hmget(redis_music_hash_key.format(x), "sound_name", "type" )
        musics = map(get_music_list, music_set)
        return musics

class music:
    def __init__(self, id, sound_name, type, data):
        self.id = id
        self.sound_name = sound_name
        self.type = type
        self.data = data
    
    def play(self):
        pass