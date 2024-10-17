from typing import Any

from ...DataStructure import Stack
from ...REPlus import *


class Token:
    def __init__(self, type_: str, value: re.Match | Any):
        self.type = type_
        if isinstance(value, re.Match):
            self.match = value
            self.value = value.group()
        else:
            self.value = value

    def __str__(self):
        return f"{self.type}( {self.value} )"

    def __len__(self):
        return len(str(self.value))

    def __repr__(self):
        return f"Token{(self.type, self.value)}"


NEWLINE = Literal('\n')

IDENT = Re('[a-zA-Z_][a-zA-Z0-9_-]*')

WHITESPACE = Re(' +')

IMPORT = Literal('import')
AS = Literal('as')
FROM = Literal('from')
PASS = Literal('pass')

LP = Re(r'[(\[{]')
RP = Re(r'[)\]}]')

SPLIT_CHAR = Re(r'[,.]')

ASSIGN = Literal('=')

INT = Re('-?[0-9]+')
eINT = Re(r'-?\d+e\d+')

STR = Re(r'"([^"\\]*(\\.[^"\\]*)*)"')
sSTR = Re("'([^'\\\\]*(\\\\.[^'\\\\]*)*)'")

# 定义记号规则
TOKEN_PATTERNS = [
    ("INDENT", Re(r'\n[\t ]+')),
    ("NEWLINE", NEWLINE),
    ("IMPORT", IMPORT),
    ("FROM", FROM),
    ("PASS", PASS),
    ("IDENT", IDENT),
    ("ASSIGN", ASSIGN),
    ("INT", INT),
    ("INT", eINT),
    ("STR", STR),
    ("STR", sSTR),
    ("LP", LP),
    ("RP", RP),
    ("SPLIT_CHAR", SPLIT_CHAR),
    ("SPACE", WHITESPACE),
    # ("UNKNOWN", ANY),
]  # type: list[tuple[str, BaseRe]]


# "\""

def _lex(code):
    longer_match = None
    longer_token = None
    for token_type, pattern in TOKEN_PATTERNS:
        match = pattern.match(code)
        if match is None:
            # print(f"{token_type} not match")
            continue
        token = Token(token_type, match)
        if longer_match is None or len(match.group()) > len(longer_match.group()):
            longer_match = match
            longer_token = token
    # print(f"Longer Token: {longer_token}")
    return longer_token


def _calc_indent_length(indent):
    s = 0
    for c in indent:
        if c == '\t':
            s += 4
        elif c == ' ':
            s += 1
    return s


def _process_tokens(tokens):
    i = 0
    while i < len(tokens):
        if tokens[i].type == 'INDENT':
            indent_token = tokens[i]
            # tokens[i] = Token('NEWLINE', '\n')
            # tokens.insert(i + 1, Token('INDENT', _calc_indent_length(indent_token.value)))
            tokens[i] = Token('INDENT', _calc_indent_length(indent_token.value))
            i += 1
        if tokens[i].type == 'NEWLINE':
            tokens.pop(i)
            continue

        i += 1


def _process_indent(tokens: list[Token]):
    # 将绝对缩进转成相对缩进
    i = 0
    s = Stack([0])
    while i < len(tokens):
        if tokens[i].type == 'INDENT':
            indent_length = tokens[i].value
            s.push(indent_length)
            indent_length -= s[-2]
            if indent_length != 0:  # 当缩进有变化时，才生成新的记号
                if indent_length > 0:
                    tokens[i] = Token('INDENT', indent_length)
                else:
                    tokens[i] = Token('DEDENT', -indent_length)
        i += 1


def _delete_whitespace(tokens: list[Token]):
    i = 0
    while i < len(tokens):
        if tokens[i].type == 'SPACE':
            tokens.pop(i)
        else:
            i += 1


# 词法分析器
def lex(source_code):
    tokens = []
    while source_code:
        token = _lex(source_code)
        if token is None:
            raise SyntaxError(f"Invalid syntax: {source_code.split('\n')[0]}")
        tokens.append(token)
        source_code = source_code[len(token):]

    _process_tokens(tokens)
    _process_indent(tokens)
    # _delete_whitespace(tokens)

    return tokens
