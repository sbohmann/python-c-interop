import typing

from generator.codewriter import CodeWriter, CodeWriterMode
from model.model import Module, Type, PrimitiveType, List, Set, Map


class PythonModuleGenerator:
    def __init__(self, module: Module):
        self.module = module
        self._out = CodeWriter(CodeWriterMode.Python)
        self._complexTypesWritten = set()

    def run(self):
        for enum in self.module.enums:
            self._write_enum(enum)
            self._complexTypesWritten.add(enum.name)
        for struct in self.module.structs:
            self._write_struct(struct)
            self._complexTypesWritten.add(struct.name)

    def result(self):
        return self._out.result()

    def _write_enum(self, enum):
        self._out.write('class ', enum.name, '(Enum):')
        def write_enum_body():
            ordinal = enum.first_ordinal
            for value in enum.values:
                self._out.writeln(value, ' = ', str(ordinal))
                ordinal += 1
        self._out.block(write_enum_body)
        self._out.writeln()

    def _write_struct(self, struct):
        self._out.writeln('@dataclass')
        self._out.write('class ', struct.name, ':')
        def write_struct_body():
            for field in struct.fields:
                self._out.writeln(field.name, ': ', self._python_type_for_type(field.type), ' = ',
                                  default_value_for_type(field.type))
        self._out.block(write_struct_body)
        self._out.writeln()

    def _python_type_for_type(self, t: Type):
        if type(t) is PrimitiveType:
            primitive = typing.cast(PrimitiveType, t)
            if primitive is PrimitiveType.Boolean:
                return 'bool'
            elif primitive.is_integer:
                return 'int'
            elif primitive is PrimitiveType.Float or primitive is PrimitiveType.Double:
                return 'float'
            elif primitive is PrimitiveType.String:
                return 'str'
            else:
                raise ValueError("Unsupported type [" + t.name + "]")
        elif type(t) is List:
            return f'list[{self._python_type_for_type(t.type_arguments[0])}]'
        elif type(t) is Set:
            return f'set[{self._python_type_for_type(t.type_arguments[1])}]'
        elif type(t) is Map:
            return f'dict[{self._python_type_for_type(t.type_arguments[0])}, {self._python_type_for_type(t.type_arguments[1])}]'
        else:
            # TODO import if necessary
            if t.name in self._complexTypesWritten:
                return t.name
            else:
                return "'" + t.name + "'"


def default_value_for_type(t):
    if type(t) is PrimitiveType:
        if t is PrimitiveType.Boolean:
            return 'False'
        elif t.is_integer:
            return 0
        elif t in [PrimitiveType.Float, PrimitiveType.Double]:
            return 0.0
    return None
