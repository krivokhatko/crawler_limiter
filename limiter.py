import time
    
class FuzzyLimiter:
    def __init__(self, config, storage, ptime=time):
        self._cfg = config
        self._storage = storage
        self._time = ptime

    async def rate_limit(self, domain, crawl_time):
        delay_time = 0
        cur_time = self._time.time()
        cur_time_ms = int(round(cur_time * 1000))
        rate_req, rate_time = self._cfg.get(domain, (None, None,))
        if rate_req is None:
            return 0
        bucket_index = cur_time // rate_time
        while True:
            bucket_key = '%s:%i'%(domain, bucket_index)
            planned_req = self._storage.incr(bucket_key)
            self._storage.expire(bucket_key, rate_time)
            if planned_req >= rate_req:
                bucket_index += 1
            else:
                break
        delay_time = bucket_index * rate_time - cur_time

        return (delay_time if delay_time > 0 else 0)*1000