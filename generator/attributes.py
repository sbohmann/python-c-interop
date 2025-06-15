from typing import Callable

from generator.codewriter import CodeWriter


def with_attribute(owner, attribute_name, action):
    return MacroCall(
        'with_attribute',
        owner,
        quote(attribute_name),
        'python_value',
        action)


def with_int64_attribute(owner, attribute_name, action):
    return with_attribute(
        owner,
        attribute_name,
        with_int64(
            'python_value',
            attribute_name,
            action))


def with_int64(python_name, value_name, action):
    return MacroCall(
        'with_pylong_as_int64',
        python_name,
        value_name,
        action)

def with_float_attribute(owner, attribute_name, action):
    return with_attribute(
        owner,
        attribute_name,
        with_float(
            'python_value',
            action))


def with_float(value_name, action):
    return MacroCall(
        'with_pyfloat_as_double',
        value_name,
        action)


def with_list_attribute(owner, attribute_name, action):
    return with_attribute(
        owner,
        attribute_name,
        with_list(
            'python_value',
            action))


def with_list(value_name, action):
    return MacroCall(
        'with_list_elements',
        value_name,
        action)


class MacroCall:
    def __init__(self, name: str, *arguments: type(str) | type('MacroCall') | Callable[[CodeWriter], None]):
        self.name = name
        self.arguments = list(arguments)

    def write(self, out: CodeWriter):
        original_indentation = out.indentation()
        out.writeln(self.name, '(')
        out.indent()
        first = True
        for arg in self.arguments:
            if not first:
                out.writeln(',')
            if type(arg) is MacroCall:
                arg.write(out)
            else:
                out.write(arg)
            first = False
        out.write(')')
        out.set_indentation(original_indentation)

    def writeln(self, out: CodeWriter):
        self.write(out)
        out.writeln(';')


def quote(text: str):
    return '"' + text.replace('"', '\"') + '"'
