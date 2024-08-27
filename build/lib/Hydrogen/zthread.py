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


Lock = threading.Lock
