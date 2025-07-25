from enum import Enum

from generator.codewriter import CodeWriter, CodeWriterMode
from generator.ctypes import CTypes, PascalToCCase
from model.model import Module, List


class Style(Enum):
    Knr = 1
    Bsd = 2


class CHeaderGenerator:
    def __init__(self, module: Module, style=Style.Knr):
        self.module = module
        self._style = style
        self._out = CodeWriter(CodeWriterMode.C)
        self._ctypes = CTypes()

    def run(self):
        for constant in self.module.constants:
            self._out.writeln(f'#define {constant.name} {self._literal_for_value(constant.value)}')
            self._out.writeln()
        for enum in self.module.enums:
            self._write_enum(enum)
        for struct in self.module.structs:
            self._write_struct(struct)

    def _literal_for_value(self, value):
        if type(value) is str:
            return quote(value)
        else:
            return value

    def result(self):
        return self._out.result()

    def _write_enum(self, enum):
        if enum.typedef:
            self._before_block('typedef enum')
        else:
            self._before_block('enum ', PascalToCCase(enum.name).result)

        def write_enum_body():
            ordinal = enum.first_ordinal
            first = True
            for value in enum.values:
                if not first:
                    self._out.writeln(',')
                self._out.write(value, ' = ', str(ordinal))
                ordinal += 1
                first = False
            self._out.writeln()

        if enum.typedef:
            self._out.block(write_enum_body, ' ' + PascalToCCase(enum.name).result + postfix(enum) + ';')
        else:
            self._out.block(write_enum_body, ';')
        self._out.writeln()

    def _write_struct(self, struct):
        if struct.typedef:
            self._before_block('typedef struct')
        else:
            self._before_block('struct ', PascalToCCase(struct.name).result)

        def write_struct_body():
            for field in struct.fields:
                c_type = self._ctypes.for_type(field.type)
                if type(c_type) is tuple:
                    self._out.write(c_type[0], ' ', field.name, c_type[1], ';')
                else:
                    self._out.write(c_type, ' ', field.name, ';')
                if field.comment:
                    lines = [stripped for line in field.comment.split('\n') if len(stripped := line.strip()) > 0]
                    if len(lines) == 0:
                        raise ValueError(f"Field {field.name} of struct {struct.name} has an empty comment")
                    for line in lines:
                        self._out.writeln(f" /* {line} */")
                else:
                    self._out.writeln()
                if type(field.type) is List:
                    self._out.writeln('size_t ', field.name, '_length;')

        if struct.typedef:
            self._out.block(write_struct_body, ' ' + PascalToCCase(struct.name).result + postfix(struct) + ';')
        else:
            self._out.block(write_struct_body, ';')
        self._out.writeln()

    def _before_block(self, *values):
        if self._style is Style.Knr:
            self._out.write(*values, ' ')
        elif self._style == Style.Bsd:
            self._out.writeln(*values)
        else:
            raise ValueError(f"Unknown style [{str(self._style)}]")


def postfix(type):
    return f'_{type.typedef_postfix}' if type.typedef_postfix else ''


def quote(text: str) -> str:
    return f'"{escape(text)}"'


def escape(text: str) -> str:
    escapes = {
        '"': '\\"',
        '\\': '\\\\',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\f': '\\f',
        '\b': '\\b',
        '\a': '\\a',
        '\v': '\\v'
    }
    return ''.join(escapes.get(c, c) for c in text)
