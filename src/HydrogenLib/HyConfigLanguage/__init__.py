from .Interpreter import Lexer, Parser, Interpreter


def get_lexer(source_code):
    return Lexer.lex(source_code)


def get_parser(tokens):
    return Parser.parser(tokens)


def get_interpreter(ast):
    it = Interpreter.Interpreter(ast)
    return it


def get(source_code):
    lex = get_lexer(source_code)
    ast = get_parser(lex)
    return get_interpreter(ast)

