from typing import Callable

from c_interop.generator.codewriter import CodeWriter
from c_interop.generator.ctypes import CTypes
from c_interop.model.model import List, Array


class Attributes:
    def __init__(self, ctypes: CTypes):
        self._ctypes = ctypes

    def with_attribute(self, owner, attribute_name, action):
        return MacroCall(
            'with_attribute',
            owner,
            quote(attribute_name),
            'python_value',
            action)


    def with_int64_attribute(self, owner, attribute_name, action):
        return self.with_attribute(
            owner,
            attribute_name,
            self.with_int64(
                'python_value',
                attribute_name,
                action))


    def with_int64(self, python_name, value_name, action):
        return MacroCall(
            'with_pylong_as_int64',
            python_name,
            value_name,
            action)

    def with_float_attribute(self, owner, attribute_name, action):
        return self.with_attribute(
            owner,
            attribute_name,
            self.with_float(
                'python_value',
                attribute_name,
                action))


    def with_float(self, python_name, value_name, action):
        return MacroCall(
            'with_pyfloat_as_double',
            python_name,
            value_name,
            action)


    def with_list_attribute_elements(self, owner, attribute_name, list_type: List, action):
        return self.with_attribute(
            owner,
            attribute_name,
            self.with_list_elements(
                'python_value',
                list_type,
                action))


    def with_array_attribute_elements(self, owner, attribute_name, array_type: Array, action):
        return self.with_attribute(
            owner,
            attribute_name,
            self.with_array_elements(
                'python_value',
                array_type,
                action))


    def with_list_elements(self, value_name, list_type, action):
        return MacroCall(
            'with_list_elements',
            value_name,
            self._ctypes.for_type(list_type.element_type),
            list_type.maximum_length,
            action)


    def with_array_elements(self, value_name, array_type, action):
        return MacroCall(
            'with_array_elements',
            value_name,
            self._ctypes.for_type(array_type.element_type),
            array_type.length,
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
