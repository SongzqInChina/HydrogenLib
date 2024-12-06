import builtins
import socket
import time
import warnings
from typing import Callable

from src.hydrolib import type_func, threading_methods
from src.hydrolib.socket_structure.SocketPost import SocketPost


class RPCServer:
    def __init__(self, sp_socket: SocketPost):
        self.lock_event = None
        self.thread = None
        self.socket = sp_socket
        self.functions = {}  # type: dict[str, Callable]

    def server(self, port):
        self.socket.server_at(port)

    def link(self, func):
        if not type_func.Func.is_function(func):
            raise Exception("Func param must be callable")
        func_name = func.__name__
        if func is builtins.eval or func_name == "eval":
            warnings.warn("Registering 'eval' function is potentially dangerou. Exercise extreme caution!",
                          category=UserWarning)
        self.functions[func_name] = func

    def unlink(self, func):
        type_ = type(func)
        if type_ == str:
            return self.functions.pop(type_)
        if type_func.Func.is_function(func):
            return self.functions.pop(func.__name__)
        raise Exception("Func param must be str or a func")

    def _post_loop(self, StopEvent):
        while not StopEvent.is_set():
            post = self.socket.get()
            if post is None:
                continue
            if "fc_name" not in post or "fc_args" not in post or "fc_kwargs" not in post:
                continue  # error call_request
            fc_name, fc_args, fc_kwargs = post.gets(["fc_name", "fc_args", "fc_kwargs"])
            if fc_name not in self.functions:  # function not found
                self.socket.send(
                    fc_name=fc_name,
                    time=time.time(),
                    result=("server_error", RuntimeError("Function not found"))
                )  # send error
            func = self.functions[fc_name]  # get function
            try:
                result = func(*fc_args, **fc_kwargs)  # call function
                self.socket.send(fc_name=fc_name, time=time.time(), result=("ok", result))  # send result
            except Exception as e:
                self.socket.send(fc_name=fc_name, time=time.time(), result=("error", e))  # send error

    def server_start(self):
        self.lock_event = threading_methods.threading.Event()
        self.thread = threading_methods.start_new_thread(self._post_loop, self.lock_event)

    def server_stop(self):
        if self.thread:
            self.lock_event.set()

    def close(self):
        self.server_stop()
        self.socket.close()


class RPCClient:
    def __init__(self, remote_host, remote_port, timeout=None):
        self.socket = SocketPost(SyncSocket())
        try:
            self.socket.connect(remote_host, remote_port, timeout)
        except socket.timeout:
            raise Exception("Connect timeout")

    def _request(self, fc_name, fc_args, fc_kwargs):
        self.socket.send(fc_name=fc_name, fc_args=fc_args, fc_kwargs=fc_kwargs)
        answer = self.socket.get()
        if answer is None:
            raise Exception("No answer")
        result = answer.top("result")
        return dict(
            time=answer.top("time"),
            ok=result[0] == "ok",
            return_value=result[1],
            result=result
        )

    def request(self, fc_name, *fc_args, **fc_kwargs):
        return self._request(fc_name, fc_args, fc_kwargs)

    def close(self):
        self.socket.close()
