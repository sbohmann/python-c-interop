from generator.codewriter import CodeWriter, CodeWriterMode
from generator.ctypes import CTypes
from model.model import Module


class CHeaderGenerator:
    def __init__(self, module: Module):
        self.module = module
        self._out = CodeWriter(CodeWriterMode.C)
        self._ctypes = CTypes()

    def run(self):
        for constant in self.module.constants:
            self._out.writeln(f'#define {constant.name} {self._literal_for_value(constant.value)}')
            self._out.writeln()
        for enum in self.module.enums:
            self._write_enum(enum)
        for struct in self.module.structs:
            self._write_struct(struct)

    def _literal_for_value(self, value):
        if type(value) is str:
            return quote(value)
        else:
            return value

    def result(self):
        return self._out.result()

    def _write_enum(self, enum):
        if enum.typedef:
            self._out.write('typedef enum ')
        else:
            self._out.write('enum ', PascalToCCase(enum.name).result, ' ')

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
            self._out.block(write_enum_body, ' ' + PascalToCCase(enum.name).result + postfix(enum) + ';')
        else:
            self._out.block(write_enum_body, ';')
        self._out.writeln()

    def _write_struct(self, struct):
        if struct.typedef:
            self._out.write('typedef struct ')
        else:
            self._out.write('struct ', PascalToCCase(struct.name), ' ')

        def write_struct_body():
            for field in struct.fields:
                c_type = self._ctypes.for_type(field.type)
                if type(c_type) is tuple:
                    self._out.write(c_type[0], ' ', field.name, c_type[1], ';')
                else:
                    self._out.write(c_type, ' ', field.name, ';')
                if field.comment:
                    lines = [stripped for line in field.comment.split('\n') if len(stripped := line.strip()) > 0]
                    if len(lines) == 0:
                        raise ValueError(f"Field {field.name} of struct {struct.name} has an empty comment")
                    for line in lines:
                        self._out.writeln(f" /* {line} */")
                else:
                    self._out.writeln()

        if struct.typedef:
            self._out.block(write_struct_body, ' ' + PascalToCCase(struct.name).result + postfix(struct) + ';')
        else:
            self._out.block(write_struct_body, ';')
        self._out.writeln()


def postfix(type):
    return f'_{type.typedef_postfix}' if type.typedef_postfix else ''


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


class PascalToCCase:
    def __init__(self, text: str):
        self.text = text
        self.result = ''
        self.inside_uppercase_group = False
        self.previousCharacter = None

        for c in self.text:
            self.handle_character(c)
        self.handle_character(None)

        # TODO beter algorithm
        self.result = self.result.replace('__', '_')
        if self.result[0] == '_':
            self.result = self.result[1:]

    def handle_character(self, c: str | None):
        if c is None:
            self.result += self.previousCharacter.lower()
        elif self.previousCharacter is not None:
            if c.isupper():
                if self.previousCharacter.isupper():
                    self.result += self.previousCharacter.lower()
                else:
                    self.result += self.previousCharacter + '_'
            else:
                if self.previousCharacter.isupper():
                    self.result += '_' + self.previousCharacter.lower()
                else:
                    self.result += self.previousCharacter.lower()
        self.previousCharacter = c


# class PascalToCCase:
#     def __init__(self, text: str):
#         self.text = text
#         self.words = []
#         self.current_word = []
#
#         for i, c in enumerate(text):
#             if c == '_':
#                 if self.current_word:
#                     self.words.append(''.join(self.current_word))
#                     self.current_word = []
#             elif c.isupper():
#                 # Look ahead to check if this is part of an acronym
#                 next_is_lower = (i + 1 < len(text) and text[i + 1].islower())
#                 prev_is_lower = (self.current_word and self.current_word[-1].islower())
#
#                 if prev_is_lower or next_is_lower:
#                     # Start of new word
#                     if self.current_word:
#                         self.words.append(''.join(self.current_word))
#                     self.current_word = [c]
#                 else:
#                     # Part of an acronym
#                     self.current_word.append(c)
#             else:
#                 self.current_word.append(c)
#
#         if self.current_word:
#             self.words.append(''.join(self.current_word))
#
#         self.result = '_'.join(word.lower() for word in self.words if word)

# class PascalToCCase:
#     def __init__(self, text: str):
#         self.text = text
#         self.words = []
#         self.current_word = []
#
#         for i, c in enumerate(text):
#             if c == '_':
#                 if self.current_word:
#                     self.words.append(''.join(self.current_word))
#                 self.current_word = []
#                 self.words.append('_')
#             elif c.isdigit():
#                 # Handle numbers as separate words
#                 if self.current_word:
#                     self.words.append(''.join(self.current_word))
#                     self.current_word = []
#                 self.words.append(c)
#             elif c.isupper():
#                 # Look ahead to check if this is part of an acronym
#                 next_is_lower = (i + 1 < len(text) and text[i + 1].islower())
#                 prev_is_lower = (self.current_word and self.current_word[-1].islower())
#
#                 if prev_is_lower or next_is_lower:
#                     # Start of new word
#                     if self.current_word:
#                         self.words.append(''.join(self.current_word))
#                     self.current_word = [c]
#                 else:
#                     # Part of an acronym
#                     self.current_word.append(c)
#             else:
#                 self.current_word.append(c)
#
#         if self.current_word:
#             self.words.append(''.join(self.current_word))
#
#         # Convert to lowercase and join, preserving explicit underscores
#         self.result = ''
#         for i, word in enumerate(self.words):
#             if word == '_':
#                 self.result += '_'
#             else:
#                 if i > 0 and self.words[i - 1] != '_' and word != '_':
#                     self.result += '_'
#                 self.result += word.lower()

def show(before, after):
    print(before)
    print('    ' + after)


show("XMLTutorial", PascalToCCase("XMLTutorial").result)
show("this_is_AnXMLTutorial", PascalToCCase("this_is_AnXMLTutorial").result)
show("This_isAnXMLTutorial", PascalToCCase("This_isAnXMLTutorial").result)
show("this_isAn_XMLTutorial", PascalToCCase("this_isAn_XMLTutorial").result)
show("this_isAnXML_Tutorial", PascalToCCase("this_isAnXML_Tutorial").result)
show("this_isAn_XML_tutorial", PascalToCCase("this_isAn_XML_tutorial").result)
show("this_isAnXMLT9.17tutorial_", PascalToCCase("this_isAnXMLT9.17tutorial_").result)
show("XMLTutorial", PascalToCCase("XMLTutorial").result)         # xml_tutorial
show("this_isAnXMLTutorial", PascalToCCase("this_isAnXMLTutorial").result)  # this_is_an_xml_tutorial
show("getXMLParser", PascalToCCase("getXMLParser").result)        # get_xml_parser
show("SimpleXML_", PascalToCCase("SimpleXML_").result)          # simple_xml_
show("Parse2XML", PascalToCCase("Parse2XML").result)           # parse_2_xml
show("Class_", PascalToCCase("Class_").result)              # class_
show("Class__Name", PascalToCCase("Class__Name").result)         # class__name