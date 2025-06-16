from generator.attributes import with_int64_attribute, MacroCall, quote, with_list_attribute, with_float_attribute, \
    with_attribute
from generator.codewriter import CodeWriter, CodeWriterMode
from generator.ctypes import CTypes
from model.model import Module, Struct, Enumeration, PrimitiveType, List


class CPythonConversionGenerator:
    def __init__(self, module: Module):
        self._ctypes = CTypes()
        self.module = module
        self._header = CodeWriter(CodeWriterMode.C)
        self._code = CodeWriter(CodeWriterMode.C)

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
        signature = self._ctypes.for_type(enum) + ' ' + enum.name + '_to_c(const PyObject *python_enum)'
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

        self._code.block(write_body)
        self._code.writeln()

    def _write_enum_c_to_python_conversion(self, enum):
        signature = 'PyObject * ' + enum.name + '_to_python(' + self._ctypes.for_type(enum) + ' value)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('static PyObject *enum_class = nullptr;')
            out.write('if (enum_class == nullptr) ')
            out.block(lambda: out.writeln('load_class("', self.module.name, '", "', enum.name, '");'))
            out.writeln('PyObject *result = PyObject_CallFunction(enum_class, "i", value);')
            out.write('if (result == NULL) ')
            out.block(lambda: out.writeln(
                'fail_with_message("Unable to convert ordinal value [%d] to enum ', enum.name, ', value");'))
            out.writeln('return result;')

        self._code.block(write_body)
        self._code.writeln()

    def _write_struct_python_to_c_conversion(self, struct):
        signature = self._ctypes.for_type(struct) + ' ' + struct.name + '_to_c(PyObject *python_struct)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln(self._ctypes.for_type(struct), ' result = {};')
            for field in struct.fields:
                if type(field.type) is Struct or type(field.type) is Enumeration:
                    (with_attribute(
                        'python_struct',
                        field.name,
                        'result.' + field.name + ' = ' + field.type.name + '_to_c(python_value)')
                     .writeln(out))
                elif type(field.type) is PrimitiveType and field.type.is_integer:
                    # TODO check value range! So easy to breach them from the python side ^^
                    (with_int64_attribute(
                        'python_struct',
                        field.name,
                        'result.' + field.name + ' = ' + field.name)
                     .writeln(out))
                elif type(field.type) is PrimitiveType and field.type in [PrimitiveType.Float, PrimitiveType.Double]:
                    (with_float_attribute(
                        'python_struct',
                        field.name,
                        'result.' + field.name + ' = ' + field.name)
                     .writeln(out))
                elif type(field.type) is List:
                    (with_list_attribute(
                        'python_struct',
                        field.name,
                        f'result.{field.name}[item.index] = item.value')
                     .writeln(out))
                else:
                    # TODO implement the missing types
                    raise ValueError(f'Unsupported type [{field.type.name}] of field [{struct.name}.{field.name}]')
            out.writeln('return result;')

        self._code.block(write_body)
        self._code.writeln()

    def _write_struct_c_to_python_conversion(self, struct):
        signature = 'PyObject * ' + struct.name + '_to_python(' + self._ctypes.for_type(struct) + ' c_struct)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('static PyObject *struct_class = nullptr;')
            out.write('if (struct_class == nullptr) ')
            out.block(lambda: out.writeln('load_class("', self.module.name, '", "', struct.name, '");'))
            out.writeln('PyObject *result = PyObject_CallFunction(struct_class, "");')
            out.write('if (result == NULL) ')
            out.block(lambda: out.writeln(
                'fail_with_message("Unable to instantiate struct ', struct.name, '");'))
            for field in struct.fields:
                if type(field.type) is Struct or type(field.type) is Enumeration:
                    (MacroCall(
                        'set_python_attribute',
                        'result',
                        quote(field.name),
                        field.type.name + '_to_python(c_struct.' + field.name + ')')
                     .writeln(out))
                elif type(field.type) is PrimitiveType and field.type.is_integer:
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
                elif field.type is PrimitiveType.Boolean:
                    (MacroCall(
                        'with_pybool',
                        'c_struct.' + field.name,
                        'value',
                        MacroCall(
                            'set_python_attribute',
                            'result',
                            quote(field.name),
                            'value'))
                     .writeln(out))
                elif field.type in [PrimitiveType.Float, PrimitiveType.Double]:
                    (MacroCall(
                        'with_double_as_pyfloat',
                        'c_struct.' + field.name,
                        'value',
                        MacroCall(
                            'set_python_attribute',
                            'result',
                            quote(field.name),
                            'value'))
                     .writeln(out))
                elif field.type is PrimitiveType.String:
                    (MacroCall(
                        'with_string_as_pystring',
                        'c_struct.' + field.name,
                        'value',
                        MacroCall(
                            'set_python_attribute',
                            'result',
                            quote(field.name),
                            'value'))
                     .writeln(out))
                elif type(field.type) is List:
                    # TODO create python list
                    out.writeln(f'for (size_t index = 0; index < {field.type.maximum_length} && index < {field.name + '_length'}; ++index) ')

                    def write_block():
                        out.writeln(
                            f'{self._ctypes.for_type(field.type.type_arguments[0])} item = c_struct.{field.name}[index];')
                        # TODO add to python list

                    # TODO set python attribute
                    out.block(write_block)
                else:
                    # TODO implement the missing types
                    raise ValueError(f'Unsupported type [{field.type.name}] of field [{struct.name}.{field.name}]')
            out.writeln('return result;')

        self._code.block(write_body)
        self._code.writeln()
