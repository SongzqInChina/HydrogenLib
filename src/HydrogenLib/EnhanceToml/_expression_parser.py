import re
from types import NoneType

from ._literal_eval import literal_eval
from ._toml_types import *
from ..DataStructure import Stack

parentheses_map = {
    '(': ')',
    '[': ']',
    '{': '}',
    ')': '(',
    ']': '[',
    '}': '{'
}


def parentheses_match(text: str):
    """
    判断括号是否配对
    """
    parentheses_stack = Stack()
    for char in text:
        if char in '([{':
            parentheses_stack.push(char)
        if char in ')]}':
            x = parentheses_stack.get()
            if x is None:
                return False
            x = parentheses_map[x]
            if x != char:
                return False
            parentheses_stack.pop()
    return parentheses_stack.empty()


def get_parentheses_pair(text: str):
    if not parentheses_match(text):
        return None
    parentheses_stack = Stack()
    result = []
    for index, char in enumerate(text):
        if char in '([{':
            parentheses_stack.push((index, char))
        if char in ')]}':
            i, x = parentheses_stack.get()
            x = parentheses_map[x]
            if x != char:
                return None
            parentheses_stack.pop()
            result.append((i, index, char))
    return result


def split_parentheses(text: str):
    """
    将带括号的字符串分解成嵌套列表。
    """
    if not parentheses_match(text):
        raise ValueError("Invalid parentheses in the input string")

    def parse_expression(index):
        result = []
        while index < len(text):
            char = text[index]
            if char in '([{':
                sub_result, index = parse_expression(index + 1)
                result.append(sub_result)
            elif char in ')]}':
                return result, index
            elif char == ',' or char.isspace():
                index += 1
                continue
            else:
                start = index
                while index < len(text) and text[index] not in ',)]} \n\t':
                    index += 1
                result.append(text[start:index])
            index += 1
        return result, index

    parsed_result, _ = parse_expression(0)
    return parsed_result


def expression_eval(text: str):
    data = literal_eval(text)
    if isinstance(data, int):
        return Int(data)
    if isinstance(data, float):
        return Float(data)
    if isinstance(data, str):
        return String(data)
    if isinstance(data, list):
        return List([expression_eval(repr(i)) for i in data])
    if isinstance(data, dict):
        return Dict({expression_eval(repr(k)): expression_eval(repr(v)) for k, v in data.items()})
    if isinstance(data, NoneType):
        return Null()
    return data


TABLE_RE_EXPRESSION = r'\[\s*[\w.-]+\s*]'


def is_table(text: str):
    x = re.match(TABLE_RE_EXPRESSION, text)
    return x is not None


def find_tables(text: str):
    return re.findall(TABLE_RE_EXPRESSION, text)


def _to_dict(keys: list):
    if len(keys) == 1:
        return {keys[0]: None}
    return {keys[0]: _to_dict(keys[1:])}


def get_tables(text: str):
    return [_to_dict(i.strip('[]').split('.')) for i in find_tables(text)]


def split_tables(text: str):
    return re.split(TABLE_RE_EXPRESSION, text)


def check(text: str):
    lines = [i for i in text.split('\n') if not i.isspace() if i != '']
    return "# enhancetoml" in lines[0].lower()


def decode(text: str):
    if not check(text):
        raise ValueError("Not an enhanced TOML file")  # 增强TOML可能与原版TOML不兼容
    tables = find_tables(text)
    chunks = [i for i in split_tables(text) if not i.isspace() if i != '']
    res = {}
    for chunk, table in zip(chunks, tables):
        lines = [i for i in chunk.split('\n') if not i.isspace() if i != '']
        res[table] = {}
        index = 0
        while index < len(lines):
            # 合并行
            line = lines[index]
            if not parentheses_match(line):
                lines[index] += lines[index + 1]
                lines.pop(index + 1)
            else:
                index += 1
        for index, line in enumerate(lines):
            # 这时候的内容就是括号合并到一行的了
            line = line.rstrip().lstrip()
            eq_char_index = line.find('=')
            key, value = line[:eq_char_index].strip(), line[eq_char_index + 1:]
            if key == '':
                continue
            value = expression_eval(value)
            res[table][key] = value
    return res
