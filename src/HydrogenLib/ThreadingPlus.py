import threading as threading
from queue import Queue


def get_new_thread(function, args=(), kwargs={}):
    t = threading.Thread(target=function, args=args, kwargs=kwargs)
    return t


def start_new_thread(function, *args, **kwargs):
    t = get_new_thread(function, args, kwargs)
    t.start()
    return t


def start_daemon_thread(function, *args, **kwargs):
    t = get_new_thread(function, args, kwargs)
    t.daemon = True
    t.start()
    return t


def exit_thread(thread: threading.Thread):
    """
    This function is not safe. You should use thread.join() instead.
    """
    thread._tstate_lock.release()


def run_with_timeout(func, timeout, *args, **kwargs):
    queue = Queue()

    def target():
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            res = e

        queue.put(res)

    thread = start_new_thread(target)
    thread.join(timeout)

    if thread.is_alive():
        raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")

    result = queue.get()

    if isinstance(result, Exception):
        raise result
    return result


def run_in_thread(func, *args, **kwargs):
    queue = Queue()

    def target():
        try:
            res = func(*args, **kwargs)
        except Exception as e:
            res = e

        queue.put(res)

    return queue, start_new_thread(target)


def run_in_thread_with_timeout(func, timeout, *args, **kwargs):
    def target():
        return run_with_timeout(func, timeout, *args, **kwargs)

    return run_in_thread(target)


class ThreadPool:
    def __init__(self, max_length=8):
        self.max_length = max_length
        self.lock = threading.Lock()
        self._count = 0

    def submit(self, func, timeout=None, *args, **kwargs):
        def wait():
            with self.lock:
                self._count += 1
            q, t = run_in_thread(func, *args, **kwargs)
            result = q.get(timeout=timeout)
            with self.lock:
                self._count -= 1
            return result

        if self._count >= self.max_length:
            raise Exception("ThreadPool is full")

        return run_in_thread(wait)[0]

    @property
    def count(self):
        with self.lock:
            return self._count



