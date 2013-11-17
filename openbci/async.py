from Queue import Queue
import random
import threading
import time

from openbci import OpenBCI

class OpenBCIAsync(threading.Thread):
    "Buffered OpenBCI reading suitable for use in a thread"

    def __init__(self, bufferlen=250, **kw):
        threading.Thread.__init__(self)
        self.bci = OpenBCI(**kw)
        self.queue = Queue(maxsize=bufferlen)

    def run(self):
        for val in self.bci:
            self.queue.put(val)

class DummyData(threading.Thread):
    def __init__(self, bufferlen=250, **_kw):
        threading.Thread.__init__(self)
        self.queue = Queue(maxsize=bufferlen)

    def run(self):
        while True:
            self.queue.put([random.random()*2 - 1 for _x in range(8)])
            time.sleep(1.0/250)
