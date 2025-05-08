import typing

from generator.codewriter import CodeWriter, CodeWriterMode
from model.model import Module, Type, PrimitiveType, Struct, Enumeration


class CHeaderGenerator:
    _out = CodeWriter(CodeWriterMode.C)

    def __init__(self, module: Module):
        self.module = module

    def run(self):
        for enum in self.module.enums:
            self._write_enum(enum)
        for struct in self.module.structs:
            self._write_struct(struct)

    def result(self):
        return self._out.result()

    def _write_enum(self, enum):
        self._out.write('enum ', enum.name, ' ')
        def write_enum_body():
            ordinal = 1
            first = True
            for value in enum.values:
                if not first:
                    self._out.writeln(',')
                self._out.write(value, ' = ', str(ordinal))
                ordinal += 1
                first = False
            self._out.writeln()
        self._out.block(write_enum_body, ';')
        self._out.writeln()

    def _write_struct(self, struct):
        self._out.write('struct ', struct.name)
        def write_struct_body():
            for field in struct.fields:
                self._out.writeln(self._c_type_for_type(field.type), ' ', field.name, ';')
        self._out.block(write_struct_body, ';')
        self._out.writeln()

    def _c_type_for_type(self, t: Type):
        if type(t) is PrimitiveType:
            primitive = typing.cast(PrimitiveType, t)
            if primitive is PrimitiveType.Boolean:
                return 'bool'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int64:
                return 'int64_t'
            elif primitive is PrimitiveType.UInt64:
                return 'unt64_t'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int32:
                return 'int32_t'
            elif primitive is PrimitiveType.UInt32:
                return 'unt32_t'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int16:
                return 'int16_t'
            elif primitive is PrimitiveType.UInt16:
                return 'unt16_t'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int8:
                return 'int8_t'
            elif primitive is PrimitiveType.UInt8:
                return 'unt8_t'
            elif primitive is PrimitiveType.Float:
                return 'float'
            elif primitive is PrimitiveType.Double:
                return 'double'
            elif primitive is PrimitiveType.String:
                return 'const char *'
            else:
                raise ValueError("Unsupported type [" + t.name + "]")
        else:
            # TODO import if necessary
            if type(t) is Struct:
                return 'struct ' + t.name
            elif type(t) is Enumeration:
                return 'enum ' + t.name
            else:
                raise ValueError("Unsupported type " + str(type(t)))
