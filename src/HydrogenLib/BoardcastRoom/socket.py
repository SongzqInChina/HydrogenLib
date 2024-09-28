from ..Class.MemberManager import Manager
from ..SocketPlus import *


class BoardcastServer:
    def __init__(self, port):
        self.port = port
        self.sock = SyncSocket()
        self.member_manager = Manager()
