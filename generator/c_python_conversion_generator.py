from generator.attributes import with_int64_attribute, MacroCall, quote
from generator.codewriter import CodeWriter, CodeWriterMode
from generator.ctypes import CTypes
from model.model import Module, Struct, Enumeration


class CPythonConversionGenerator:
    def __init__(self, module: Module):
        self.module = module
        self._header = CodeWriter(CodeWriterMode.C)
        self._code = CodeWriter(CodeWriterMode.C)
        self.ctypes = CTypes()

    def run(self):
        for enum in self.module.enums:
            self._write_enum_python_to_c_conversion(enum)
            self._write_enum_c_to_python_conversion(enum)
        for struct in self.module.structs:
            self._write_struct_python_to_c_conversion(struct)
            self._write_struct_c_to_python_conversion(struct)

    def result(self):
        return self._header.result(), self._code.result()

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
