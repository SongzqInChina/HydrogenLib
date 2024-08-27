from threading import Lock


def to_thread_safety(classic):
    class Wrapper:
        OrignalClass = classic

        def __init__(self, *args, **kwargs):
            self.value = self.OrignalClass(*args, **kwargs)
            self._lock = Lock()

        def __getattr__(self, item):
            with self._lock:
                return getattr(self.value, item)

    return Wrapper
