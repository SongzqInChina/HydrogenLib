import multiprocessing
import pathlib
import queue
import threading

from ._ConfigLoader import *
from ..TypeFunc import get_attr_by_path
from ..ThreadingPlus import start_daemon_thread


class TestManager:
    def __init__(self):
        self.configs = []  # type: list[Config]
        self.queue = multiprocessing.Queue()

    def load(self, cfg_file):
        self.configs.append(
            Config.load_cls(cfg_file)
        )

    def loads(self, path: str, pattern: str):
        path = pathlib.Path(path)
        files = path.glob(pattern)
        for file in files:
            self.load(file)

    def run_test(self, config: Config, queue: queue.Queue):
        res = config.run()
        queue.put(res)

    def run(self, main_class):
        ps_list = []  # type: list[threading.Thread]
        for config in self.configs:
            config.func = get_attr_by_path(main_class, config.name).top()

        for config in self.configs:
            ps = start_daemon_thread(self.run_test, config, self.queue)
            ps_list.append(ps)

        for ps in ps_list:
            ps.join()

        results = {}
        i = 0
        while self.queue.qsize() and i < len(self.configs):
            results[self.configs[i].name] = self.queue.get()
        return results
