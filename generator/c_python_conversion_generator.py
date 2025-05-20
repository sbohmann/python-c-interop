import typing

from generator.attributes import with_attribute, with_int64, with_int64_attribute, MacroCall, quote
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
            self._write_enum_c_to_python_conversion(enum)
        for struct in self.module.structs:
            self._write_struct_python_to_c_conversion(struct)
            self._write_struct_c_to_python_conversion(struct)

    def result(self):
        return (self._header.result(), self._code.result())

    def _write_enum_python_to_c_conversion(self, enum):
        signature = 'struct ' + enum.name + '_to_c(const PyObject *python_enum)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('int ordinal = -1;')
            (with_int64_attribute(
                'python_enum',
                'value',
                'ordinal = value')
             .writeln(self._code))
            out.writeln('switch (ordinal) {')
            ordinal = 1
            for value in enum.values:
                out.writeln('    case ', value, ':')
                out.writeln('        return ', value, ';')
                ordinal += 1
            out.writeln('    default', ':')
            out.writeln('        fail_with_message("Illegal ordinal value for enum ', enum.name, ' [%d]", ordinal);')
            out.writeln('}')

        self._code.block(write_body, ';')
        self._code.writeln()

    def _write_enum_c_to_python_conversion(self, enum):
        signature = 'PyObject * ' + enum.name + '_to_python(enum ' + enum.name + ' value)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('static PyObject *enum_class = load_class("', self.module.name, '", "', enum.name, '")')
            out.writeln('result = return PyObject_CallMethod(enum_class, "i", (int) value);')
            out.write('if (result == NULL) ')
            out.block(lambda: out.writeln(
                'fail_with_message("Unable to convert ordinal value [%d] to enum ', enum.name, ', value);'))
            out.writeln('return result;')

        self._code.block(write_body, ';')
        self._code.writeln()

    def _write_struct_python_to_c_conversion(self, struct):
        signature = 'struct ' + struct.name + ' ' + struct.name + '_to_c(PyObject *python_struct)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('struct ', struct.name, ' result = {};')
            for field in struct.fields:
                if type(field.type) is Struct or type(field.type) is Enumeration:
                    out.writeln('result.', field.name, ' = ', field.type.name, '_to_c(python_struct.', field.name, ')')
                else:
                    (with_int64_attribute(
                        'python_struct',
                        field.name,
                        'result.' + field.name + ' = value')
                     .writeln(out))
            out.writeln('return result;')

        self._code.block(write_body, ';')
        self._code.writeln()

    def _write_struct_c_to_python_conversion(self, struct):
        signature = 'PyObject * ' + struct.name + '_to_python(struct ' + struct.name + ' c_struct)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('static PyObject *struct_class = load_class("', self.module.name, '", "', struct.name, '")')
            out.writeln('PyObject *result = PyObject_CallMethod(struct_class, "");')
            out.write('if (result == NULL) ')
            out.block(lambda: out.writeln(
                'fail_with_message("Unable to instantiate struct ', struct.name, ');'))
            for field in struct.fields:
                if type(field.type) is Struct or type(field.type) is Enumeration:
                    (MacroCall(
                        'set_python_attribute',
                        'result',
                        quote(field.name),
                        field.type.name + '_to_c(c_struct.' + field.name + ')')
                     .writeln(out))
                else:
                    (MacroCall(
                        'with_int64_as_pylong',
                        'c_struct.' + field.name,
                        'value',
                        MacroCall(
                            'set_python_attribute',
                            'result',
                            quote(field.name),
                            'value'))
                     .writeln(out))
            out.writeln('return result;')

        self._code.block(write_body, ';')
        self._code.writeln()

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
