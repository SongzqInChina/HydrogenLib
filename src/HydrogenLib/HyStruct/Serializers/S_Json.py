import json
import socket

from . import Abc
from ... import DataStructure


class Json(Abc.Serializer):
    left_delimiter = b"{["
    right_delimiter = b"}]"

    quotations = b"'\""

    mapping = {
        b'{': b'}',
        b'[': b']',
    }

    def __init__(self):
        self.stack = None
        self.s = None

    def dumps(self, data):
        return json.dumps(data)

    def loads(self, data):
        return json.loads(data)

    def _type_int(self, sock):
        while True:
            char = sock.recv(1, socket.MSG_PEEK)
            if not char.isdigit():
                return int(self.s)
            self.s += char
            sock.recv(1)

    def _type_string(self, sock):
        cnt = 0
        escape = False
        while True:
            char = sock.recv(1, socket.MSG_PEEK)
            self.s += char
            if char == b'\\':
                escape = not escape
            elif escape:
                escape = False
            if char in self.quotations and not escape:
                cnt += 1
                if cnt == 2:
                    return self.loads(self.s)
            sock.recv(1)

    def _type_struct(self, sock):
        in_string = False
        escape = False
        while True:
            char = sock.recv(1)
            self.s += char
            if char == b'\\':
                escape = not escape
            else:
                if escape:
                    escape = False
            if char in self.quotations and not escape:  # 未转义的引号
                in_string = not in_string
            if in_string:  # 跳过引号内的字符
                continue
            if char in self.left_delimiter:
                self.stack.push(char)
            if char in self.right_delimiter:
                if self.stack.is_empty():
                    raise ValueError("Invalid json format(缺少左括号)", self.stack)
                c = self.stack.pop()
                if char != self.mapping[c]:
                    raise ValueError("Invalid json format(括号不匹配)", self.stack, 'except:', c, 'get:', char)

                if self.stack.is_empty():
                    return self.loads(self.s)

    def load_from_sock(self, sock):
        """
        动态解析JSON,当括号识别正确时认为数据接收完毕
        """
        self.s = b''
        while True:
            char = sock.recv(1, socket.MSG_PEEK)
            if char != b'':
                break
            sock.recv(1)
        if not char.isdigit():
            if char == b'"':
                return self._type_string(sock)
            else:
                self.stack = DataStructure.Stack()
                return self._type_struct(sock)
        else:
            return self._type_int(sock)
