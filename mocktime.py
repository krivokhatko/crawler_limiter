class MockTime:
    def __init__(self, start_time=0.0):
        self._time = float(start_time)
        
    def time(self):
        return self._time
    
    def sleep(self, delay):
        self._time += delay