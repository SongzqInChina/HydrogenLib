# Namedpipe for windows
import win32pipe
from win32file import WriteFile, ReadFile

from ..Json import Pickle


# module end
# module start at Aug 31st 2024 20:31
# module not end
# TODO: 完成命名管道的重构


# self.handle = win32pipe.CreateNamedPipe(  Server
#     self.format_name(),
#     win32pipe.PIPE_ACCESS_INBOUND,
#     win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
#     1, 65535, 65535,
#     0, None
# )
# self.handle = win32file.CreateFileW(  Client
#     self.format_name(),
#     win32file.GENERIC_WRITE,
#     0,
#     None,
#     win32file.OPEN_EXISTING,
#     0,
#     None
# )

# Server: Create namedpipe
# Client: Create file
# Server: Connect namedpipe
# Client: Write to file
def format_pipe_name(name):
    return fr"\\.\pipe\{name}"


class Server:
    def __init__(self, name):
        self.filename = format_pipe_name(name)
        self.namedpipe = None
        self.connects = 0

    def _wait_for_connect(self):
        return win32pipe.ConnectNamedPipe(self.namedpipe, None)

    def listen(self):
        self.namedpipe = win32pipe.CreateNamedPipe(
            self.filename,
            win32pipe.PIPE_ACCESS_DUPLEX,
            win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_WAIT,
            1, 65535, 65535,
            0, None
        )

    def accept(self):
        self._wait_for_connect()

    def write(self, data):
        WriteFile(self.namedpipe, data)

    def read(self):
        return ReadFile(self.namedpipe, 65535)

    def close(self):
        win32pipe.DisconnectNamedPipe(self.namedpipe)
