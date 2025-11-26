from c_interop.generator.codewriter import CodeWriter, CodeWriterMode
from c_interop.generator.ctypes import CTypes, PascalToCCase
from c_interop.generator.style import Style
from c_interop.model.model import Module, Struct, Enumeration, PrimitiveType, Array


class CToStringGenerator:
    def __init__(self, module: Module, style=Style.Knr):
        self.module = module
        self._style = style
        self._header_out = CodeWriter(CodeWriterMode.C)
        self._module_out = CodeWriter(CodeWriterMode.C)
        self._ctypes = CTypes()

    def run(self):
        for enum in self.module.enums:
            self._write_enum_to_string(enum)
        for struct in self.module.structs:
            self._write_struct_to_string(struct)

    def result(self):
        return self._header_out.result(), self._module_out.result()

    def _write_enum_to_string(self, enum: Enumeration):
        enum_c_name = self._enum_c_name(enum)

        enum_c_signature = f'void {enum_c_name}_to_string({enum_c_name} value, struct OutputHandler *out)'

        self._header_out.writeln(enum_c_signature + ';')

        self._before_block(enum_c_signature)

        def write_to_string_body():
            def write_switch_block():
                for value in enum.values:
                    self._module_out.writeln(f'case {value}:')
                    self._module_out.indent()
                    self._module_out.writeln(f'OutputHandler_process(out, "%s", "{value}");')
                    self._module_out.writeln(f'break;')
                    self._module_out.unindent()
                self._module_out.writeln(f'default:')
                self._module_out.indent()
                self._module_out.writeln(f'OutputHandler_process(out, "Unknown %s value: %d", "{enum.name}", value);')
                self._module_out.unindent()

            self._before_block('switch (value)')
            self._module_out.block(write_switch_block)

        self._module_out.block(write_to_string_body)
        self._module_out.writeln()

    def _write_struct_to_string(self, struct: Struct):
        struct_c_name = self._struct_c_name(struct)

        struct_c_signature = f'void {struct_c_name}_to_string({struct_c_name} value, struct OutputHandler *out, size_t indentation)'

        self._header_out.writeln(struct_c_signature + ';')

        self._before_block(struct_c_signature)

        def write_to_string_body():
            self._module_out.writeln(f'OutputHandler_process(out, "{struct.name} {{\\n");')
            for field in struct.fields:
                write_field_to_string_call(field)
            self._module_out.writeln(f'OutputHandler_indent(out, indentation);')
            self._module_out.writeln('OutputHandler_process(out, "}");')

        def write_field_to_string_call(field):
            self._module_out.writeln(f'OutputHandler_indent(out, indentation + 1);')
            self._module_out.writeln(f'OutputHandler_process(out, "%s: ", "{field.name}");')
            if type(field.type) is Struct:
                self._module_out.writeln(f'{self._struct_c_name(field.type)}_to_string(value.{field.name}, out, indentation + 1);')
            elif type(field.type) is Enumeration:
                self._module_out.writeln(f'{self._enum_c_name(field.type)}_to_string(value.{field.name}, out);')
            elif type(field.type) is PrimitiveType:
                field_code = primitive_type_printf_code(field.type)
                self._module_out.writeln(f'OutputHandler_process(out, "{field_code}", value.{field.name});')
            elif type(field.type) is Array:
                def write_array_element_to_string():
                    self._module_out.writeln(f'OutputHandler_indent(out, indentation + 2);')
                    if type(field.type.element_type) is Struct:
                        self._module_out.writeln(f'{self._struct_c_name(field.type.element_type)}_to_string(value.{field.name}[index], out, indentation + 2);')
                    elif type(field.type) is Enumeration:
                        self._module_out.writeln(f'{self._enum_c_name(field.type.element_type)}_to_string(value.{field.name}[index], out);')
                    elif type(field.type) is PrimitiveType:
                        element_code = primitive_type_printf_code(field.type.element_type)
                        self._module_out.writeln(f'OutputHandler_process(out, "{element_code}", value.{field.name}[index]);')
                    self._module_out.writeln(f'OutputHandler_process(out, ",\\n");')

                self._module_out.writeln(f'OutputHandler_process(out, "[\\n");')
                self._before_block(f'for (size_t index = 0; index < {field.type.length}; ++index)')
                self._module_out.block(write_array_element_to_string)
                self._module_out.writeln(f'OutputHandler_indent(out, indentation + 1);')
                self._module_out.writeln(f'OutputHandler_process(out, "]");')

            else:
                raise ValueError(f"Unsupported type: {field.type}")
            self._module_out.writeln(f'OutputHandler_process(out, ",\\n");')

        self._module_out.block(write_to_string_body)
        self._module_out.writeln()

    def _enum_c_name(self, enum):
        prefix = '' if enum.typedef else 'enum '
        postfix = '_e' if enum.typedef else ''
        enum_c_name = prefix + PascalToCCase(enum.name).result + postfix
        return enum_c_name

    def _struct_c_name(self, struct):
        prefix = '' if struct.typedef else 'struct '
        postfix = '_t' if struct.typedef else ''
        struct_c_name = prefix + PascalToCCase(struct.name).result + postfix
        return struct_c_name

    def _before_block(self, *values):
        if self._style is Style.Knr:
            self._module_out.write(*values, ' ')
        elif self._style == Style.Bsd:
            self._module_out.writeln(*values)
        else:
            raise ValueError(f"Unknown style [{str(self._style)}]")


def primitive_type_printf_code(primitve_type):
    if primitve_type == PrimitiveType.Int64:
        return '%lld'
    elif primitve_type == PrimitiveType.UInt64:
        return '%llu'
    elif primitve_type == PrimitiveType.Int32:
        return '%ld'
    elif primitve_type == PrimitiveType.UInt32:
        return '%lu'
    elif primitve_type == PrimitiveType.Int16:
        return '%d'
    elif primitve_type == PrimitiveType.UInt16:
        return '%u'
    elif primitve_type == PrimitiveType.Int8:
        return '%d'
    elif primitve_type == PrimitiveType.UInt8:
        return '%u'
    elif primitve_type in (PrimitiveType.Double, PrimitiveType.Float):
        return '%f'
    else:
        raise ValueError(f"Unsupported primitive type: {primitve_type}")


def quote(text: str) -> str:
    return f'"{escape(text)}"'


def escape(text: str) -> str:
    escapes = {
        '"': '\\"',
        '\\': '\\\\',
        '\n': '\\n',
        '\r': '\\r',
        '\t': '\\t',
        '\f': '\\f',
        '\b': '\\b',
        '\a': '\\a',
        '\v': '\\v'
    }
    return ''.join(escapes.get(c, c) for c in text)
