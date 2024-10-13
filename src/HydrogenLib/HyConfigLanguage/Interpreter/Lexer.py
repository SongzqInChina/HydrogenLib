from typing import Any

from ...DataStructure import Stack
from ...REPlus.REConcatenater import *


class Token:
    def __init__(self, type_: str, value: re.Match | Any):
        self.type = type_
        if isinstance(value, re.Match):
            self.match = value
            self.value = value.group()
        else:
            self.value = value

    def __str__(self):
        return f"Token{(self.type, self.value)}"

    def __len__(self):
        return len(str(self.value))

    __repr__ = __str__


NEWLINE = Literal('\n')
WHITESPACE = Re(' +')
IDENT = Re(r'[a-zA-Z_][a-zA-Z0-9_.]*')
TABLE_DEF = Literal('[', ignore=True) + Re(IDENT, name="table_name") + Literal(']', ignore=True)
# ASSIGN = Literal('=')
ANY = Re('.+')
ASSIGN = Re(IDENT, name='var_name') + Re(r'\s*=\s*', ignore=True) + Re(ANY, name="value")
IMPORT = Re(r'import\s+') + Re(IDENT)
IMPORT_AS = Re(r'import\s+') + Re(IDENT) + Re(r'\s+as\s+') + Re(IDENT)
FROM_IMPORT = Re(r'from\s+') + Re(IDENT) + Re(r'\s+import\s+') + Re(IDENT)
FROM_IMPORT_AS = Re(r'from\s+') + Re(IDENT) + Re(r'\s+import\s+') + Re(IDENT) + Re(r'\s+as\s+') + Re(IDENT)
PASS = Literal('pass')

# 定义记号规则
TOKEN_PATTERNS = [
    ("INDENT", Re(r'\n[\t ]+')),
    ("NEWLINE", NEWLINE),
    ("IMPORT", IMPORT),
    ("IMPORT", IMPORT_AS),
    ("IMPORT", FROM_IMPORT),
    ("IMPORT", FROM_IMPORT_AS),
    ("PASS", PASS),
    ("ASSIGN", ASSIGN),
    ("TABLE_DEF", TABLE_DEF),
    ("IDENT", IDENT),
    ("WHITESPACE", WHITESPACE),
    # ("UNKNOWN", ANY),
]  # type: list[tuple[str, REConcateratable]]


def _lex(code):
    longer_match = None
    longer_token = None
    for token_type, pattern in TOKEN_PATTERNS:
        match = pattern.match(code)
        if match is None:
            continue
        token = Token(token_type, match)
        if longer_match is None or len(match.group()) > len(longer_match.group()):
            longer_match = match
            longer_token = token

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


# 词法分析器
def lex(source_code):
    tokens = []
    while source_code:
        token = _lex(source_code)
        if not token:
            raise SyntaxError(f"Invalid syntax: {source_code.split('\n')[0]}")
        tokens.append(token)
        source_code = source_code[len(token):]

    _process_tokens(tokens)
    _process_indent(tokens)

    return tokens
