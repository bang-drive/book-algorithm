from datetime import datetime
import time


class RecurringTimer(object):
    def __init__(self, interval):
        self.interval = interval
        self.last_time = datetime.fromtimestamp(0)

    def remain(self):
        now = datetime.now()
        result = self.interval - (now - self.last_time).total_seconds()
        if result <= 0:
            self.last_time = now
        return result

    def check(self):
        return self.remain() <= 0

    def wait(self):
        if (seconds := self.remain()) > 0:
            time.sleep(seconds)
            self.last_time = datetime.now()
        return True
