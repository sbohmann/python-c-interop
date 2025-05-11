import typing

from generator.codewriter import CodeWriter, CodeWriterMode
from model.model import Module, Type, PrimitiveType, Struct, Enumeration


class CPythonConversionGenerator:
    _header = CodeWriter(CodeWriterMode.C)
    _code = CodeWriter(CodeWriterMode.C)

    def __init__(self, module: Module):
        self.module = module

    def run(self):
        for enum in self.module.enums:
            self._write_enum_python_to_c_conversion(enum)
            # self._write_enum_c_to_python_conversion(enum)
        # for struct in self.module.structs:
            # self._write_struct(struct)

    def result(self):
        return (self._header.result(), self._code.result())

    def _write_enum_python_to_c_conversion(self, enum):
        signature = 'struct ' + enum.name + '(const PyObject *python_enum)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')
        def write_body():
            self._code.writeln(
'''int ordinal = -1;
    with_attribute(
        python_control_algorithm,
        "value",
        python_value,
        with_pylong_as_int64(
            python_value,
            value,
            ordinal = value));''')
            self._code.writeln('switch (ordinal) {')
            ordinal = 1
            for value in enum.values:
                self._code.writeln('    case ', value, ':')
                self._code.writeln('        return ', value, ';')
                ordinal += 1
            self._code.writeln('    default', ':')
            self._code.writeln('        fail_with_message("Illegal ordinal value for enum ', enum.name, ' [%d]", ordinal);')
            self._code.writeln('}')
        self._code.block(write_body, ';')
        self._code.writeln()

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
