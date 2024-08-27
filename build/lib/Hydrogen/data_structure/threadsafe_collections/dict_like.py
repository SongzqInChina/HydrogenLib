from threading import Lock


class SafeDict:
    def __init__(self, value):
        self._lock = Lock()
        self._dict = dict(value)

    def __getattr__(self, item):
        with self._lock:
            return self._dict[item]
