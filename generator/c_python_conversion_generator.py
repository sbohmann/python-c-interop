from generator.attributes import Attributes, MacroCall, quote
from generator.codewriter import CodeWriter, CodeWriterMode
from generator.ctypes import CTypes
from model.model import Module, Struct, Enumeration, PrimitiveType, List, Array


class CPythonConversionGenerator:
    def __init__(self, module: Module, module_prefix=''):
        self._ctypes = CTypes()
        self._module = module
        self._module_prefix = module_prefix
        self._protocol_name = 'python_' + module.name + '_protocol'
        self._header = CodeWriter(CodeWriterMode.C)
        self._code = CodeWriter(CodeWriterMode.C)
        self._attributes = Attributes(self._ctypes)

    def run(self):
        for enum in self._module.enums:
            self._write_enum_python_to_c_conversion(enum)
            self._write_enum_c_to_python_conversion(enum)
        for struct in self._module.structs:
            self._write_struct_python_to_c_conversion(struct)
            self._write_struct_c_to_python_conversion(struct)

    def result(self):
        return self._header.result(), self._code.result()

    def _write_enum_python_to_c_conversion(self, enum):
        signature = self._ctypes.for_type(enum) + ' ' + enum.name + '_to_c(PyObject *python_enum)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('int ordinal;')
            (self._attributes.with_int64_attribute(
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
            out.block(lambda: out.writeln('enum_class = load_class("', self._module_prefix + self._protocol_name, '", "', enum.name, '");'))
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
                (assignment(f'result.{field.name}', field.name, field.type)
                 .writeln(out))
            out.writeln('return result;')

        def assignment(target, field_name, value_type):
            if type(value_type) is Struct or type(value_type) is Enumeration:
                return self._attributes.with_attribute(
                    'python_struct',
                    field_name,
                    target + ' = ' + value_type.name + '_to_c(python_value)')
            elif type(value_type) is PrimitiveType and value_type.is_integer:
                # TODO check value range! So easy to breach them from the python side ^^
                return self._attributes.with_int64_attribute(
                    'python_struct',
                    field_name,
                    target + ' = ' + field_name)
            elif type(value_type) is PrimitiveType and value_type in [PrimitiveType.Float, PrimitiveType.Double]:
                return self._attributes.with_float_attribute(
                    'python_struct',
                    field_name,
                    target + ' = ' + field_name)
            elif type(value_type) is List:
                return self._attributes.with_list_attribute_elements(
                    'python_struct',
                    field_name,
                    value_type,
                    assignment(f'{target}[item_index]', field_name + '_item', value_type.type_arguments[0]))
            elif type(value_type) is Array:
                return self._attributes.with_array_attribute_elements(
                    'python_struct',
                    field_name,
                    value_type,
                    assignment(f'{target}[item_index]', field_name + '_item', value_type.type_arguments[0]))
            else:
                # TODO implement the missing types
                raise ValueError(f'Unsupported type [{value_type.name}] of field [{struct.name}.{field_name}]')

        self._code.block(write_body)
        self._code.writeln()

    def _write_struct_c_to_python_conversion(self, struct):
        signature = 'PyObject * ' + struct.name + '_to_python(' + self._ctypes.for_type(struct) + ' c_struct)'
        self._header.writeln(signature, ';')
        self._code.write(signature, ' ')

        def write_body(out):
            out.writeln('static PyObject *struct_class = nullptr;')
            out.write('if (struct_class == nullptr) ')
            out.block(lambda: out.writeln('struct_class = load_class("', self._module_prefix + self._protocol_name, '", "', struct.name, '");'))
            out.writeln('PyObject *result = PyObject_CallFunction(struct_class, "");')
            out.write('if (result == NULL) ')
            out.block(lambda: out.writeln(
                'fail_with_message("Unable to instantiate struct ', struct.name, '");'))
            for field in struct.fields:
                if type(field.type) is Struct or type(field.type) is Enumeration:
                    (MacroCall(
                        'set_python_attribute_and_decref',
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
                            'set_python_attribute_and_decref',
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
                            'set_python_attribute_and_decref',
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
                            'set_python_attribute_and_decref',
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
                            'set_python_attribute_and_decref',
                            'result',
                            quote(field.name),
                            'value'))
                     .writeln(out))
                elif type(field.type) in (List, Array):
                    (MacroCall(
                        'with_array_as_pylist',
                        'c_struct.' + field.name,
                        field.type.element_type.name + '_to_python',
                        MacroCall(
                            'set_python_attribute_and_decref',
                            'result',
                            quote(field.name),
                            'pylist'))
                     .writeln(out))
                else:
                    # TODO implement the missing types
                    raise ValueError(f'Unsupported type [{field.type.name}] of field [{struct.name}.{field.name}]')
            out.writeln('return result;')

        self._code.block(write_body)
        self._code.writeln()
