import re
import typing

from model.model import Type, PrimitiveType, Struct, Enumeration, List, Array


class CTypes:
    def __init__(self):
        self.includes = set()

    def for_type(self, t: Type):
        if type(t) is PrimitiveType:
            primitive = typing.cast(PrimitiveType, t)
            if primitive is PrimitiveType.Boolean:
                return 'bool'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int64:
                return 'int64_t'
            elif primitive is PrimitiveType.UInt64:
                return 'uint64_t'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int32:
                return 'int32_t'
            elif primitive is PrimitiveType.UInt32:
                return 'uint32_t'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int16:
                return 'int16_t'
            elif primitive is PrimitiveType.UInt16:
                return 'uint16_t'
            elif primitive is PrimitiveType.Integer or primitive is PrimitiveType.Int8:
                return 'int8_t'
            elif primitive is PrimitiveType.UInt8:
                return 'uint8_t'
            elif primitive is PrimitiveType.Float:
                return 'float'
            elif primitive is PrimitiveType.Double:
                return 'double'
            elif primitive is PrimitiveType.String:
                return 'const char *'
        else:
            # TODO import if necessary
            if type(t) is Struct:
                if typing.cast(Struct, t).typedef:
                    return PascalToCCase(t.name).result + '_t'
                else:
                    return 'struct ' + PascalToCCase(t.name).result
            elif type(t) is Enumeration:
                if typing.cast(Enumeration, t).typedef:
                    return PascalToCCase(t.name).result + '_e'
                else:
                    return 'enum ' + PascalToCCase(t.name).result
            elif type(t) is List:
                array_type = typing.cast(List, t)
                if array_type.maximum_length is not None:
                    return f'{self.for_type(array_type.element_type)}', f'[{array_type.maximum_length}]'
                else:
                    raise ValueError('Arbitrary length C lists not yet implemented')
            elif type(t) is Array:
                array_type = typing.cast(Array, t)
                return f'{self.for_type(array_type.element_type)}', f'[{array_type.length}]'
        raise ValueError("Unsupported type " + t.name)


class PascalToCCase:
    _multiple_underscores = re.compile(r'_+')

    def __init__(self, text: str):
        self.text = text
        self.result = ''
        self.inside_uppercase_group = False
        self.previousCharacter = None

        for c in self.text:
            self.handle_character(c)
        self.handle_character(None)

        self.result: str  = self._multiple_underscores.sub('_', self.result)
        if self.result[0] == '_':
            self.result = self.result[1:]

    def handle_character(self, c: str | None):
        if c is None:
            self.result += self.previousCharacter.lower()
        elif self.previousCharacter is not None:
            if c.isupper():
                if self.previousCharacter.isupper():
                    self.result += self.previousCharacter.lower()
                elif self.previousCharacter.islower():
                    self.result += self.previousCharacter + '_'
                else:
                    self.result += self.previousCharacter
            elif c.islower():
                if self.previousCharacter.isupper():
                    if len(self.result) > 0:
                        self.result += '_' + self.previousCharacter.lower()
                    else:
                        self.result += self.previousCharacter.lower()
                elif self.previousCharacter.islower():
                    self.result += self.previousCharacter
                else:
                    self.result += self.previousCharacter.lower()
            else:
                self.result += self.previousCharacter.lower()
        self.previousCharacter = c
