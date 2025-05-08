from enum import Enum
from typing import Callable

_indentation_step = 4
_indentation = ' ' * _indentation_step


class CodeWriterMode(Enum):
    C = 1
    Python = 2


class CodeWriter:
    _buffer: list[str] = []
    _indentation_level = 0
    _at_line_start = True
    _opening_bracket: str
    _closing_bracket: str

    def __init__(self, mode: CodeWriterMode):
        if mode is CodeWriterMode.C:
            self._opening_bracket = '{'
            self._closing_bracket = '}'
        elif mode is CodeWriterMode.Python:
            self._opening_bracket = ''
            self._closing_bracket = ''

    def write(self, *values):
        if self._at_line_start:
            self._buffer.append(_indentation * self._indentation_level)
            self._at_line_start = False
        for value in values:
            self._buffer.append(str(value))

    def writeln(self, *values):
        self.write(*values)
        self.write('\n')
        self._at_line_start = True

    def block(self, write_code):
        self.writeln(self._opening_bracket)
        self._indentation_level += 1
        write_code()
        self._indentation_level -= 1
        self.writeln(self._closing_bracket)

    def result(self):
        return ''.join(self._buffer)
