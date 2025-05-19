from typing import Callable

from generator.codewriter import CodeWriter


def with_attribute(out: CodeWriter, owner, attribute_name, action):
    (MacroCall('with_attribute',
              owner,
              quote(attribute_name),
              'python_value',
              action)
     .writeln(out))


class MacroCall:
    def __init__(self, name: str, *arguments: str | type('MacroCall') | Callable[[CodeWriter], None]):
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
        out.writeln()


def quote(text: str):
    return '"' + text.replace('"', '\"') + '"'
