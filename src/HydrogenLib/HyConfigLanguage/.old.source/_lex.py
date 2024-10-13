from pyparsing import (
    Word, alphas, alphanums, oneOf, ZeroOrMore, Group, LineEnd, LineStart,
    Optional, Literal, restOfLine
)

# 定义基础元素
identifier = Word(alphas, alphanums + "_")
integer = Word("0123456789")
keyword = oneOf("import from as name")
newline = LineEnd().suppress()
indent = LineStart() + (" " * 4)
dedent = LineStart() - (" " * 4)

# 定义表
table_def = Group(
    Literal("[") + identifier + Literal("]") + newline
)

# 定义变量赋值
assignment = Group(
    identifier + Literal("=") + restOfLine + newline
)

# 定义模块导入
import_statement = Group(
    keyword("import") + identifier("module") + Optional(keyword("as") + identifier("alias")) + newline
)

# 定义从模块导入
from_import_statement = Group(
    keyword("from") + identifier("module") + keyword("import") + identifier("name") +
    Optional(
        keyword("as") + identifier("alias")) + newline
)

# 定义整个代码块
code_block = ZeroOrMore(
    table_def
    | assignment
    | import_statement
    | from_import_statement
)


def parse(code):
    return code_block.parseString(code)
