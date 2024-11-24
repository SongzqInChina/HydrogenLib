# Namedpipe for windows

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
