import signal
from contextlib import contextmanager

class Timeout(Exception):
    pass

@contextmanager
def time_limit(seconds: int):
    def signal_handler(signum, frame):
        raise Timeout("Time limit exceeded")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
