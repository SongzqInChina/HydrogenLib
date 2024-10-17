from .Lexer import Token
from ...DataStructure import Stack


class SysntaxMatcher:
    def __init__(self, *expr):
        """
        通过指定语法，实现对语法的检测
        如：
            s = SysnatxMatcher('LP=[', 'IDENT', 'RP=]')
            s.match([Token('LP', '['), Token('IDENT', 'abc'), Token('RP', ']')])  # True
        """
        self.expr = expr
        self._rules = []

    def _split_expr(self):
        for i in self.expr:
            self._rules.append(i.split('='))


class Node:
    def __init__(self, _type, value=None, children=None):
        self.type = _type
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"{self.type}: {self.value} {self.children}"


class Table:
    def __init__(self):
        self.data = ''
        self.subtables = []


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens  # type: list[Token]
        self.pos = 0

    def check(self):
        self._check_parenthesis()

    def _get_type(self, pos):
        """
        分析当前标记和后续标记，判断类型（语句，表达式，赋值...）
        """

    def parse(self):
        def consume(type_):
            while self.tokens[self.pos].type != 'WHITESSPACE':
                self.pos += 1

            return self.tokens[self.pos]

    def _check_parenthesis(self):
        s = Stack()
        for token in self.tokens:
            if token.type == 'LP':
                s.push(token)
            if token.type == 'RP':
                if s.empty():
                    raise SyntaxError('Unexpected right parenthesis')
                t = s.pop()
                if t.value != token.value:
                    raise SyntaxError('Unexpected right parenthesis')

        if not s.empty():
            raise SyntaxError('Unexpected left parenthesis')
        return True
