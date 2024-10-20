from rich import print
import src.HydrogenLib
import src.HydrogenLib.HyConfigLanguage.Interpreter.Lexer
import src.HydrogenLib.HyConfigLanguage.Interpreter.Parser
import src.HydrogenLib.HyConfigLanguage.Interpreter.Interpreter
src.HydrogenLib.init(show_locals=True)

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
        c = subtable_2.two + "No"
        fill_var = {<name>}

import module1
import module2 as m2

from module3 import name1
from module4 import name2 as n2
'''

Inter = src.HydrogenLib.HyConfigLanguage
tokens = Inter.Lexer.lex(data)

for t in tokens:
    if t.type == 'WHITESPACE': continue
    print(t)
print("[bold green]Get [bold yellow]{}[bold green] tokens. [/]".format(len(tokens)))

ast = Inter.Parser.Parser(tokens)
ast.check()
for node in ast.parse():
    print(node)



