from collections import deque
from threading import Lock
from typing import Iterable


class SafeList:
    def __init__(self, lst: list | Iterable | None = None):
        if lst is None:
            lst = []
        self.list = lst

        self.lock = Lock()

    def __getattr__(self, item):
        with self.lock:
            return getattr(self.list, item)


class SafeDeque:
    def __init__(self, __list: Iterable | deque | None = None):
        if __list is None:
            __list = deque([])
        self.list = deque(__list)
        self.lock = Lock()

    def __getattr__(self, item):
        with self.lock:
            return getattr(self.list, item)
