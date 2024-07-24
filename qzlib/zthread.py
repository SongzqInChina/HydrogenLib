import threading as threading


def get_new_thread(function, args=(), kwargs={}):
    t = threading.Thread(target=function, args=args, kwargs=kwargs)
    return t


def start_new_thread(function, *args, **kwargs):
    t = get_new_thread(function, args, kwargs)
    t.start()
    return t


def start_demon_thread(function, *args, **kwargs):
    t = get_new_thread(function, args, kwargs)
    t.daemon = True
    t.start()
    return t


def exit_thread(thread: threading.Thread):
    thread._tstate_lock.release()


Lock = threading.Lock
