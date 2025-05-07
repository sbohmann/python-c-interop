import typing

from generator.CodeWriter import CodeWriter, CodeWriterMode
from model.model import Module, Type, PrimitiveType


class PythonModuleGenerator:
    out = CodeWriter(CodeWriterMode.Python)

    def __init__(self, module: Module):
        self.module = module

    def run(self):
        for enum in self.module.enums:
            self.write_enum(enum)
        for struct in self.module.structs:
            self.write_struct(struct)

    def write_enum(self, enum):
        self.out.write('class', enum.name, '(Enum):')
        def write_enum_body():
            ordinal = 1
            for value in enum.values:
                self.out.write(value, ' = ', str(ordinal))
                ordinal += 1
        self.out.block(write_enum_body)
        self.out.writeln()

    def write_struct(self, struct):
        self.out.write('class', struct.name)
        def write_struct_body():
            for field in struct.fields:
                self.out.write(field.name, ': ', pythonTypeForType(field.type))
        self.out.block(write_struct_body)
        self.out.writeln()

def pythonTypeForType(t: Type):
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
        # TODO quote as forward if outer type or written before
        return t.name
