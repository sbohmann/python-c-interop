import typing

from model.model import Type, PrimitiveType, Struct, Enumeration


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
            # TODO import if necessary
            if type(t) is Struct:
                if typing.cast(Struct, t).typedef:
                    return t.name
                else:
                    return 'struct ' + t.name
            elif type(t) is Enumeration:
                if typing.cast(Enumeration, t).typedef:
                    return t.name
                else:
                    return 'enum ' + t.name
        raise ValueError("Unsupported type " + t.name)
