import unittest
from storage import Storage
from mocktime import MockTime
from limiter import FuzzyLimiter

class TestLimiter(unittest.TestCase):

    def test_limiter(self):
        time = MockTime(100000)
        config = {'rozetka.ua':(10, 15), 'f.ua':(10, 20), 'repka.ua':(20, 12)}
        storage = Storage(ptime=time)

        crawlers = []
        crawlers.append({'next_start':int(round(time.time() * 1000)), 'domain':'f.ua', 'page_gen':50})
        crawlers.append({'next_start':int(round(time.time() * 1000)), 'domain':'f.ua', 'page_gen':50})
        crawlers.append({'next_start':int(round(time.time() * 1000)), 'domain':'rozetka.ua', 'page_gen':80})
        crawlers.append({'next_start':int(round(time.time() * 1000)), 'domain':'rozetka.ua', 'page_gen':80})
        crawlers.append({'next_start':int(round(time.time() * 1000)), 'domain':'repka.ua', 'page_gen':70})
        crawlers.append({'next_start':int(round(time.time() * 1000)), 'domain':'repka.ua', 'page_gen':70})

        domain_req_count = {}
        limiter = FuzzyLimiter(config, storage, ptime=time)

        delta_time = 0
        start_time = time.time()
        while delta_time < 120:
            cur_time = int(round(time.time() * 1000))
            for crawler in crawlers:
                if crawler['next_start'] <= cur_time:
                    if crawler['domain'] not in domain_req_count:
                        domain_req_count[crawler['domain']] = 0
                    domain_req_count[crawler['domain']] += 1
                    dt = limiter.rate_limit(crawler['domain'], crawler['page_gen'])
                    crawler['next_start'] = cur_time + dt
            time.sleep(0.0001)
            delta_time = time.time() - start_time

        for key, val in domain_req_count.items():
            self.assertTrue(abs(val/delta_time - config[key][0]/config[key][1]) < 0.1)

if __name__ == '__main__':
    unittest.main()