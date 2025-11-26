from enum import Enum
from typing import Callable

_indentation_step = 4
_indentation = ' ' * _indentation_step


class CodeWriterMode(Enum):
    C = 1
    Python = 2


class CodeWriter:
    def __init__(self, mode: CodeWriterMode):
        self._buffer: list[str] = []
        self._indentation_level = 0
        self._at_line_start = True
        self._opening_bracket: str
        self._closing_bracket: str

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

    # noinspection PyTypeChecker
    def block(self, write_code: Callable[['CodeWriter'], None] | Callable[[], None], suffix=''):
        self.writeln(self._opening_bracket)
        self._indentation_level += 1
        self._call_with_self(write_code)
        self._indentation_level -= 1
        self.writeln(self._closing_bracket, suffix)

    def indent(self):
        self._indentation_level += 1

    def unindent(self):
        if self._indentation_level < 1:
            raise ValueError("Attempting to unindent below zero")
        self._indentation_level -= 1

    def result(self):
        if self._indentation_level != 0:
            raise ValueError("Attempting to retrieve result at indentation level " + str(self._indentation_level))
        return ''.join(self._buffer)

    def indentation(self):
        return self._indentation_level

    def set_indentation(self, value):
        if type(value) is int and value >= 0:
            self._indentation_level = value
        else:
            raise ValueError("Illegal indentation level value [" + str(value) + "] of type " + str(type(value)))

    def _call_with_self(self, function):
        if hasattr(function, '__code__') and function.__code__.co_argcount > 0:
            function(self)
        else:
            function()
