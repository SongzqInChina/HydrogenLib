import re
from collections import deque
from fnmatch import fnmatch
from typing import Optional

import rich.table

from .Lexer import Token
from ...data_structures import Stack


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


class Phrase(Token):
    ...


TPANY = '*'
MODE_GREEDY = 'GREEDY'
MODE_CONDITIONAL_GREEDY = 'CONGREEDY'
MODE_EXACT = 'EXACT'


class MatchRule:
    re = re.compile(
        r'([*+-])?(\d+)?\s*:?\s*(\?)?([^\s=:]+)\s*=?\s*(.+)?'
    )
    _mapping = {
        '*': MODE_GREEDY,
        '-': MODE_CONDITIONAL_GREEDY,
        '+': MODE_EXACT,
        None: MODE_EXACT,
    }

    skips = ['WHITESPACE']

    def __init__(self, rule_str, skips=None):
        if rule_str.strip() == '':
            self.mode, self.t_p__name_pat, self.value, self.cnt, self.include = MODE_EXACT, TPANY, TPANY, 1, False
        else:
            self.mode, self.t_p__name_pat, self.value, self.cnt, self.include = self.__split_rule(rule_str)

        if skips is not None:
            self.skips = skips  # type: list[str]

    def __error(self, rule, *args):
        raise ValueError(f"Invalid match rule: {rule}", *args)

    def __split_rule(self, rule_str):
        match = self.re.match(rule_str)
        if not match:
            self.__error(rule_str)
        print(match.groups())
        (
            mode, cnt, include, ident,
            value,
            *args
        ) = match.groups()

        assert len(args) == 0

        cnt = int(cnt) if cnt else 1

        if mode not in self._mapping:
            self.__error(rule_str, f'Mode={mode} not found')

        mode = self._mapping.get(mode, None)
        return mode, ident, value, cnt, (include is None)

    def __check_type(self, tk):
        return fnmatch(tk.type, self.t_p__name_pat)

    def __eq(self, tk):
        """
        检查Token和Rule是否匹配
        """
        res = self.__check_type(tk)
        if not res:
            return False
        if self.value != TPANY:  # 检查是否为精确匹配
            res &= tk.value == self.value  # 值匹配

        return res  # 返回结果

    def __move_no_skip(self, tokens):
        tk_length = len(tokens)
        while self.pos < tk_length and tokens[self.pos] in self.skips:
            self.pos += 1
        return self.pos

    def __greedy_match(self, tokens, results: deque):  # 尽可能多匹配
        consumption = 0
        self.pos = 0
        while True:
            self.__move_no_skip(tokens)
            tk = tokens[self.pos]

            if self.__eq(tk):
                results.append(tk)
                consumption += 1
            else:
                break

            self.pos += 1

    def __exact_match(self, tokens, results: deque):  # 要么匹配成功，要么不匹配
        self.pos = 0
        n = 0
        while True:
            self.__move_no_skip(tokens)
            tk = tokens[self.pos]

            if self.__eq(tk):
                results.append(tk)
                n += 1
            else:
                results.clear()
                break

            if n >= self.cnt:
                break

        if n < self.cnt:
            results.clear()
            return
        return

    def __congreedy_match(self, tokens, results: deque):  # 至少匹配cnt个
        self.__greedy_match(tokens, results)
        if len(results) < self.cnt:  # 匹配失败
            results.clear()
        return

    def match(self, tokens):
        results = deque()
        func = None
        if self.mode == MODE_GREEDY:
            func = self.__greedy_match
        elif self.mode == MODE_EXACT:
            func = self.__exact_match
        elif self.mode == MODE_CONDITIONAL_GREEDY:
            func = self.__congreedy_match

        func(tokens, results)

        return list(results)

    def __repr__(self):
        return \
            (
                f'{self.__class__.__name__}'
                f'<name={repr(self.t_p__name_pat)}, value={repr(self.value)}, cnt={self.cnt}, mode={self.mode}>'
            )


class SyntaxMatcher:
    def __init__(self, *rules: str):
        self.rules = []  # type: list[MatchRule]
        self.__process_rules(rules)

    def __process_rules(self, rules):
        for rule in rules:
            self.rules.append(MatchRule(rule))

    def match(self, tokens) -> tuple[Optional[list[Token]], int]:
        consumption = 0
        results = deque()
        for rule in self.rules:
            result = rule.match(tokens[consumption:])
            if result is None:
                return None, 0
            consumption += len(result)
            if rule.include:
                results.append(result)
        return list(results), consumption


class Parser:
    """
    对原始标记列表的第一次处理
    """
    types = [
        ('indent', SyntaxMatcher('INDENT')),
        ('dedent', SyntaxMatcher('DEDENT')),

        ('table_def', SyntaxMatcher('LP=[', 'IDENT', 'RP=]')),

        ('import', SyntaxMatcher('?FROM', 'IDENT', '?IMPORT', 'IDENT', '?AS', 'IDENT')),
        ('import', SyntaxMatcher('?FROM', 'IDENT', '?IMPORT', 'IDENT')),
        ('import', SyntaxMatcher('?IMPORT', 'IDENT', '?AS', 'IDENT')),
        ('import', SyntaxMatcher('?IMPORT', 'IDENT')),

        ('fill_item', SyntaxMatcher('?LFILL', 'IDENT', '?RFILL')),

        ('oper', SyntaxMatcher('OPER', '*')),

        ('assign', SyntaxMatcher('IDENT', '?ASSIGN')),
        ('oper_assign', SyntaxMatcher('IDENT', 'OPER', '?ASSIGN')),

        ('start_seq', SyntaxMatcher('?LP', '*', '?SPLIT_CHAR=,')),
        ('elem', SyntaxMatcher('*', '?SPLIT_CHAR=,')),
        ('end_seq', SyntaxMatcher('*', '?RP')),
        ('end_seq', SyntaxMatcher('*', '?SPLIT_CHAR=,', '?RP')),

        ('get_attr', SyntaxMatcher('?SPLIT_CHAR=.', 'IDENT')),

        ('one_expr', SyntaxMatcher('STR')),
        ('one_expr', SyntaxMatcher('INT')),
        ('one_expr', SyntaxMatcher('IDENT')),

        ('lp', SyntaxMatcher('LP')),
        ('rp', SyntaxMatcher('RP')),
    ]  # type: list[tuple[SyntaxMatcher, ...]]

    phrase_matchers = [
        ('expr', SyntaxMatcher('oper', 'expr')),
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
        trys = deque()
        for type_, matcher in self.types:
            x, length = matcher.match(tokens[pos:])
            if length:
                return type_, length, trys
            trys.append((type_, length > 0))
        return None, 0, trys

    def _error(self, tokens=None, trys=None):
        token_msg = rich.table.Table('*', 'Token', title='Token')
        for idx in range(max(0, self.pos - 5), min(len(tokens), self.pos + 5)):
            tk = tokens[idx]
            if idx == self.pos:
                token_msg.add_row('=>', str(tk))
            else:
                token_msg.add_row('', str(tk))
        try_msg = rich.table.Table('Type', 'Matched', title='Try')
        for try_res in trys:
            type_, matched = try_res
            try_msg.add_row(type_, 'Yes' if matched else 'No')
        phrase_msg = rich.table.Table('Phrase', title='Phrases')
        for phrase in self.phrases:
            phrase_msg.add_row(phrase)
        console = rich.get_console()
        console.print(token_msg, try_msg, phrase_msg)
        raise SyntaxError()

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
            type_, length, trys = self._get_type(self.pos, tokens)
            if type_ is None:  # Error
                self._error(tokens, trys)
            matches = []
            for i in range(length):
                move_no_whitespace()
                matches.append(tokens[self.pos])
                consume(1)
            p = Phrase(type_, matches)
            self.phrases.append(p)

    def _second_parse(self):
        self.pos = 0
        while self.pos < len(self.phrases):
            p = self.phrases[self.pos]

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
                if s.is_empty():
                    raise SyntaxError('Unexpected right parenthesis(except {}, but get {})'.format(
                        None, token.value
                    ))
                t = s.pop()
                if parenthesis_map[t.value] != token.value:
                    raise SyntaxError('Unexpected right parenthesis(except {}, but get {})'.format(
                        t.value, token.value
                    ))

        if not s.is_empty():
            raise SyntaxError('Unexpected left parenthesis')
        return True

    def __repr__(self):
        return f'{self.pos}'
