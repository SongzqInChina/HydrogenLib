import json

from .Abc import Serializer
from ...DataStructure import Stack


class Json(Serializer):
    left_delimiter = b"{["
    right_delimiter = b"}"

    quotations = b"'\""

    mapping = {
        b'{': b'}',
        b'[': b']',
    }

    def __init__(self):
        self.stack = None
        self.s = None

    def dump(self, data):
        return json.dumps(data)

    def load(self, data):
        return json.loads(data)

    def _type_int(self, sock):
        while True:
            char = sock.recv(1)
            if not char.isdigit():
                return int(self.s)
            self.s += char

    def _type_string(self, sock):
        while True:
            char = sock.recv(1)
            self.s += char
            if char in self.quotations:
                return self.s

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
            if char in self.quotations and not escape:  # 未转义的引号内
                in_string = not in_string
            if in_string:  # 跳过引号内的字符
                continue
            if char in self.left_delimiter:
                self.stack.push(char)
            if char in self.right_delimiter:
                if self.stack.is_empty():
                    raise ValueError("Invalid json format(缺少左括号)")
                c = self.stack.pop()
                if char != self.mapping[c]:
                    raise ValueError("Invalid json format(括号不匹配)")

                if self.stack.is_empty():
                    return json.loads(self.s)

    def load_from_sock(self, sock):
        """
        动态解析JSON,当括号识别正确时认为数据接收完毕
        """
        self.s = b''
        char = sock.recv(1)
        print("Char", char)
        while char == b'':
            char = sock.recv(1)
        print("Char 2", char)
        self.s += char
        if not char.isdigit():
            if char == b'"':
                return self._type_string(sock)
            else:
                self.stack = Stack()
                if char in self.left_delimiter:
                    self.stack.push(char)
                return self._type_struct(sock)
        else:
            return self._type_int(sock)
