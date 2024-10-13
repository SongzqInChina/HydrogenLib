import builtins

import src.HydrogenLib
from src.HydrogenLib.REPlus.REConcatenater import *
src.HydrogenLib.init(show_locals=True)

Re("abc") + Re('bcd')

var_assign = (Re(r'[a-zA-Z_][a-zA-Z0-9_]*', name="name") + Re(r'\s*=\s*', ignore=True) +
              Re(r'.+', name="value"))
start = Re('^')

NEWLINE = Literal('\n')
WHITESPACE = Re(' +')
IDENT = Re(r'[a-zA-Z_][a-zA-Z0-9_.]*')
TABLE_DEF = Literal('[', ignore=True) + Re(IDENT, name="table_name") + Literal(']', ignore=True)
KEYWORD = Re("(from|import|as|pass)")
# ASSIGN = Literal('=')
ANY = Re('.+')
ASSIGN = Re(IDENT, name='var_name') + Re(r'\s*=\s*', ignore=True) + Re(ANY, name="value")
builtins.print(ASSIGN.pattern())
res = ASSIGN.match('a = 1')
# ('a', ' = ', '1')
print(res.group())
print(res.groups())
print(res.groupdict())
