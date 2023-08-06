import time


class StopWatch:
    def __init__(self):
        self._start = 0
        self._stop = 0

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self.display_elapsed(self._start, self._stop)

    def start(self):
        self._start = time.time()

    def stop(self):
        self._stop = time.time()

    def reset(self):
        self._start = 0
        self._stop = 0

    @staticmethod
    def display_elapsed(start, stop):
        seconds = stop - start  # get total elapsed seconds
        minutes = (seconds // 60) % 60  # to get correct minutes first divide total seconds by 60 then modulo by 60
        hours = seconds // 3600  # hours is total seconds divided by 3600 (seconds in an hour)
        seconds %= 60  # finally, modulo seconds now that you're done using the total
        print(f'Start-{start} : Stop-{stop} : '
              f'Difference-{int(hours):0>2}:{int(minutes):0>2}:{round(seconds, 3):0>6}')
