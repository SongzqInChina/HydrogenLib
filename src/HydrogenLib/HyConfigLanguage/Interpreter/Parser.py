from idlelib.macosx import isXQuartz

from ...DataStructure import Stack


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
        self.tokens = tokens
        self.pos = 0

    def check(self):
        self._check_indent()
        self._check_keyword()

    def _check_indent(self):
        for idx, tk in enumerate(self.tokens.copy()):
            if tk.type == 'TABLE_DEF':
                if self.tokens[idx+1].type != 'INDENT':
                    raise Exception('Indent error')

    def _check_keyword(self):
        table = False
        for idx, tk in enumerate(self.tokens):
            if tk.type == 'TABLE_DEF':
                table = True
            elif tk.type in ['ASSIGN', 'ANY'] and table is False:
                raise Exception('Keyword error')




