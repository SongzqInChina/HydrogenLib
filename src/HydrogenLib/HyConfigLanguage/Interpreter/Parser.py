import re

from .Lexer import Token
from ...DataStructure import Stack


class Phrase(Token):
    ...


class SyntaxMatcher:
    class Rule:
        def __init__(self, type_, value=None):
            self.type = type_ if type_ != '' else None
            self.value = value

        def match(self, token: Token):
            if self.value is None:
                if self.type is None:
                    return True
                return self.type == token.type
            return self.type == token.type and self.value == token.value

        def __str__(self):
            return f"Rule({self.type},{self.value})"

    def __init__(self, *expr):
        """
        通过指定语法，实现对语法的检测
        如：
            s = SysnatxMatcher('LP=[', 'IDENT', 'RP=]')
            s.match([Token('LP', '['), Token('IDENT', 'abc'), Token('RP', ']')])  # True
        """
        Rule = self.Rule
        self.expr = expr
        self.skips = ['WHITESPACE']
        self._rules: list[Rule] = []

        self._split_expr()

    def __len__(self):
        return len(self._rules)

    def _split_expr(self):
        expr_re = re.compile(r'^(?P<TYPE>[A-Za-z0-9_]+)(=?)(?P<VALUE>.+)?$')
        for i in self.expr:
            if i == '':
                self._rules.append(self.Rule(i))
                continue
            match = expr_re.match(i)
            if not match:
                raise ValueError(f'Invalid expr: {i}')
            else:
                type_, value = match.groupdict()['TYPE'], match.groupdict()['VALUE']
                self._rules.append(
                    self.Rule(type_, value)
                )

    def _find(self, tokens, type_, value=None):
        rule = self.Rule(type_, value)
        for idx, tk in enumerate(tokens):
            if rule.match(tk):
                yield idx, tk

    def _match(self, idx, tokens):
        for rule in self._rules:
            if idx >= len(tokens):
                return False
            while idx < len(tokens) and tokens[idx].type in self.skips:
                idx += 1
            if not rule.match(tokens[idx]):
                return False
            idx += 1

        return True

    def find(self, tokens):
        head_token_matches = list(self._find(tokens, self._rules[0].type, self._rules[0].value))
        if not head_token_matches:
            return False
        for idx, tk in head_token_matches:
            if self._match(idx, tokens):
                yield idx

    def match(self, tokens):
        return self._match(0, tokens)


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
    types = [
        ('indent', SyntaxMatcher('INDENT')),
        ('dedent', SyntaxMatcher('DEDENT')),

        ('table_def', SyntaxMatcher('LP=[', 'IDENT', 'RP=]')),

        ('import', SyntaxMatcher('FROM', 'IDENT', 'IMPORT', 'IDENT', 'AS', 'IDENT')),
        ('import', SyntaxMatcher('FROM', 'IDENT', 'IMPORT', 'IDENT')),
        ('import', SyntaxMatcher('IMPORT', 'IDENT', 'AS', 'IDENT')),
        ('import', SyntaxMatcher('IMPORT', 'IDENT')),

        ('fill_item', SyntaxMatcher('LFILL', 'IDENT', 'RFILL')),

        ('plus', SyntaxMatcher('PLUS', '')),
        ('minus', SyntaxMatcher('MINUS', '')),
        ('multiply', SyntaxMatcher('MULTIPLY', '')),
        ('div', SyntaxMatcher('DIV', '')),
        ('floordiv', SyntaxMatcher('FLOORDIV', '')),

        ('_assign', SyntaxMatcher('IDENT', 'ASSIGN')),
        ('assign', SyntaxMatcher('_assign', 'expr')),

        ('start_seq', SyntaxMatcher('LP', '', 'SPLIT_CHAR=,')),
        ('elem', SyntaxMatcher('', 'SPLIT_CHAR=,')),
        ('end_seq', SyntaxMatcher('', 'RP')),
        ('end_seq', SyntaxMatcher('', 'SPLIT_CHAR=,', 'RP')),

        ('get_attr', SyntaxMatcher('SPLIT_CHAR=.', 'IDENT')),

        ('constant', SyntaxMatcher('STR')),
        ('constant', SyntaxMatcher('INT')),

        ('lp', SyntaxMatcher('LP')),
        ('rp', SyntaxMatcher('RP')),

        ('expr', SyntaxMatcher('ident', 'get_attr')),
        ('expr', SyntaxMatcher('get_attr', 'get_attr')),
        ('expr', SyntaxMatcher('start_seq', '', 'end_seq')),

        ('expr', SyntaxMatcher('IDENT')),
    ]

    def __init__(self, tokens):
        self._tokens = tokens  # type: list[Token]
        self.tokens = tokens  # type: list[Token]
        self.phrases = []
        self.pos = 0

    def check(self):
        self._check_parenthesis()

    def _get_type(self, pos, tokens):
        """
        分析当前标记和后续标记，判断语法类型（语句，表达式，赋值...）
        """
        for type_, matcher in self.types:
            if matcher.match(tokens[pos:]):
                return type_, len(matcher)
        return None, 0

    def _first_parse(self):
        tokens = self.tokens
        self.pos = 0

        def consume(count):
            for i in range(count):
                self.pos += 1
                move_no_whitespace()

        def move_no_whitespace():
            while self.pos < len(self.tokens) and tokens[self.pos].type == 'WHITESPACE':
                self.pos += 1

        while self.pos < len(tokens):
            move_no_whitespace()
            type_, length = self._get_type(self.pos, tokens)
            if type_ is None:  # Error
                error_msg = '\n'
                for idx in range(max(0, self.pos - 5), min(len(tokens), self.pos + 5)):
                    tk = tokens[idx]
                    if idx == self.pos:
                        error_msg += '=>'
                    error_msg += '\t'
                    error_msg += str(tk)
                    error_msg += '\n'
                raise SyntaxError(
                    error_msg
                )
            matches = []
            for i in range(length):
                move_no_whitespace()
                matches.append(tokens[self.pos])
                consume(1)
            p = Phrase(type_, matches)
            self.phrases.append(p)

    def _mid_parse(self):
        self.tokens = self.phrases

    def parse(self):
        self._first_parse()
        return self.phrases

    def _check_parenthesis(self):
        s = Stack()
        parenthesis_map = {
            '{': '}',
            '[': ']',
            '(': ')',
            ']': '[',
            '}': '{',
            ')': '(',
        }
        for token in self.tokens:
            if token.type == 'LP':
                s.push(token)
            if token.type == 'RP':
                if s.empty():
                    raise SyntaxError('Unexpected right parenthesis(except {}, but get {})'.format(
                        None, token.value
                    ))
                t = s.pop()
                if parenthesis_map[t.value] != token.value:
                    raise SyntaxError('Unexpected right parenthesis(except {}, but get {})'.format(
                        t.value, token.value
                    ))

        if not s.empty():
            raise SyntaxError('Unexpected left parenthesis')
        return True

    def __repr__(self):
        return f'{self.pos}'
