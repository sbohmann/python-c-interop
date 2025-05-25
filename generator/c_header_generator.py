from generator.codewriter import CodeWriter, CodeWriterMode
from generator.ctypes import CTypes
from model.model import Module


class CHeaderGenerator:
    def __init__(self, module: Module):
        self.module = module
        self._out = CodeWriter(CodeWriterMode.C)
        self._ctypes = CTypes()

    def run(self):
        for enum in self.module.enums:
            self._write_enum(enum)
        for struct in self.module.structs:
            self._write_struct(struct)

    def result(self):
        return self._out.result()

    def _write_enum(self, enum):
        if enum.typedef:
            self._out.write('typedef enum ')
        else:
            self._out.write('enum ', enum.name, ' ')
        def write_enum_body():
            ordinal = enum.first_ordinal
            first = True
            for value in enum.values:
                if not first:
                    self._out.writeln(',')
                self._out.write(value, ' = ', str(ordinal))
                ordinal += 1
                first = False
            self._out.writeln()
        if enum.typedef:
            self._out.block(write_enum_body, ' ' + enum.name + ';')
        else:
            self._out.block(write_enum_body, ';')
        self._out.writeln()

    def _write_struct(self, struct):
        if struct.typedef:
            self._out.write('typedef struct ')
        else:
            self._out.write('struct ', struct.name, ' ')
        def write_struct_body():
            for field in struct.fields:
                self._out.writeln(self._ctypes.for_type(field.type), ' ', field.name, ';')
        if struct.typedef:
            self._out.block(write_struct_body, ' ' + struct.name + ';')
        else:
            self._out.block(write_struct_body, ';')
        self._out.writeln()
