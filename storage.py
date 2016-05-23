import time

class Storage:
    #TODO: add periodic cleanup of expired keys
    def __init__(self, custom_dict=None, ptime=time):
        if custom_dict is None:
            self._d = {}
        else:
            self._d = custom_dict
        self._exp = {}
        self._time = ptime
    
    def set(self, key, value):
        self._d[key] = value
    
    def incr(self, key):
        if key not in self._d:
            self._d[key] = 0
        self._d[key] += 1
        return self._d[key]

    def get(self, key):
        cur_time = self._time.time()
        if cur_time > self._exp.get(key, cur_time):
            del self._d[key]
            del self._exp[key]
        return self._d.get(key, None)
        
    def expire(self, key, time_delta):
        if key in self._d:
            cur_time = self._time.time()
            self._exp[key] = cur_time + time_delta
            
    def expireat(self, key, time_at):
        if key in self._d:
            self._exp[key] = time_at