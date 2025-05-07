import typing

from generator.CodeWriter import CodeWriter, CodeWriterMode
from model.model import Module, Type, PrimitiveType


class PythonModuleGenerator:
    _out = CodeWriter(CodeWriterMode.Python)
    _complexTypesWritten = set()

    def __init__(self, module: Module):
        self.module = module

    def run(self):
        for enum in self.module.enums:
            self.write_enum(enum)
            self._complexTypesWritten.add(enum.name)
        for struct in self.module.structs:
            self.write_struct(struct)
            self._complexTypesWritten.add(struct.name)

    def write_enum(self, enum):
        self._out.write('class', enum.name, '(Enum):')
        def write_enum_body():
            ordinal = 1
            for value in enum.values:
                self._out.write(value, ' = ', str(ordinal))
                ordinal += 1
        self._out.block(write_enum_body)
        self._out.writeln()

    def write_struct(self, struct):
        self._out.write('class', struct.name)
        def write_struct_body():
            for field in struct.fields:
                self._out.write(field.name, ': ', pythonTypeForType(field.type))
        self._out.block(write_struct_body)
        self._out.writeln()

    def pythonTypeForType(self, t: Type):
        if type(t) is PrimitiveType:
            primitive = typing.cast(PrimitiveType, t)
            if primitive.name == 'Boolean':
                return 'bool'
            elif primitive.is_integer:
                return 'int'
            elif primitive.name == 'Float' or primitive.name == 'Double':
                return 'float'
            elif primitive.name == 'String':
                return 'str'
            else:
                raise ValueError("Unsupported type [" + t.name + "]")
        else:
            # TODO import if necessary
            if t.name in self._complexTypesWritten:
                return t.name
            else:
                return "'" + t.name + "'"
