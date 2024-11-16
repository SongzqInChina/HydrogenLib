from rich import print
import src.HydrogenLib
import src.HydrogenLib.HyConfigLanguage.Interpreter.Lexer
import src.HydrogenLib.HyConfigLanguage.Interpreter.Parser
import src.HydrogenLib.HyConfigLanguage.Interpreter.Interpreter
# src.HydrogenLib.init(show_locals=True)

# 测试代码
data = '''
[table_name]
    x = 1
    y = "hello"

[table_1]
    var = 0
    abc = 999
[table_2]
    var = 0
    abc = 12
    [subtable_1]
        description = "I'm a subtable!"
        [subsubTable]
            value = "End of sub tables"
        vars = [a, b, c]
    name = "Table"
    [subtable_2]
        two = ''
    [subtable_3]
        lst = [
            a, b, c,
            1,2, 3,
            'a', 'b', 'c'
        ]
        c = Config.table_2.subtable_1.description + "No"
        fill_var = {<name>}
    [subtable_4]
        add_elems = a + b + c + d + e + f + g + h + i
        multi = a * b - c + d // e / f | 1 << 10 >> 10 & 101001 ^ 2

import module1
import module2 as m2

from module3 import name1
from module4 import name2 as n2
'''

Inter = src.HydrogenLib.HyConfigLanguage.Interpreter
tokens = Inter.Lexer.lex(data)

for t in tokens:
    if t.type == 'WHITESPACE': continue
    print(t)
print("[bold green]Get [bold yellow]{}[bold green] tokens. [/]".format(len(tokens)))

first_parser = Inter.Parser.Parser(tokens)
first_parser.check()
first_results = first_parser.parse()
print(len(first_results))
for node in first_results:
    print(node)




