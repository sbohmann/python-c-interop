import typing
from abc import abstractmethod


class Type:
    name: str
    type_arguments: list['Type']

    @abstractmethod
    def __init__(self, name: str, *type_arguments: 'Type'):
        self.name: str = name
        self.type_arguments: list['Type'] = list(type_arguments)


class PrimitiveType(Type):
    Boolean: 'PrimitiveType'
    Integer: 'PrimitiveType'
    Int8: 'PrimitiveType'
    UInt8: 'PrimitiveType'
    Int16: 'PrimitiveType'
    UInt16: 'PrimitiveType'
    Int32: 'PrimitiveType'
    UInt32: 'PrimitiveType'
    Int64: 'PrimitiveType'
    UInt64: 'PrimitiveType'
    Float: 'PrimitiveType'
    Float: 'PrimitiveType'
    String: 'PrimitiveType'

    def __init__(self, name: str, **keywords):
        self.name = name
        self.type_arguments = []
        self.is_integer = keywords.get('is_integer') is True


PrimitiveType.Boolean = PrimitiveType('Boolean')
PrimitiveType.Integer = PrimitiveType('Integer', is_integer=True)
PrimitiveType.Int8 = PrimitiveType('Int8', is_integer=True)
PrimitiveType.UInt8 = PrimitiveType('UInt8', is_integer=True)
PrimitiveType.Int16 = PrimitiveType('Int16', is_integer=True)
PrimitiveType.UInt16 = PrimitiveType('UInt16', is_integer=True)
PrimitiveType.Int32 = PrimitiveType('Int32', is_integer=True)
PrimitiveType.UInt32 = PrimitiveType('UInt32', is_integer=True)
PrimitiveType.Int64 = PrimitiveType('Int64', is_integer=True)
PrimitiveType.UInt64 = PrimitiveType('UInt64', is_integer=True)
PrimitiveType.Float = PrimitiveType('Float')
PrimitiveType.Float = PrimitiveType('Double')
PrimitiveType.String = PrimitiveType('String')


class Field:
    def __init__(self, name: str, type_: Type):
        self.name: str = name
        self.type: Type = type_


class Struct(Type):
    fields: list[Field]

    def __init__(self, name: str, *fields: Field):
        super().__init__(name)
        self.fields = list(fields)


class Enumeration(Type):
    def __init__(self, name: str, *values: str):
        super().__init__(name)
        self.values: list[str] = list(values)


class List(Type):
    def __init__(self, name: str, element_type: Type):
        self.name = name
        self.type_arguments = [element_type]


class Set(Type):
    def __init__(self, name: str, element_type: Type):
        self.name = name
        self.type_arguments = [element_type]


class Map(Type):
    def __init__(self, name: str, key_type: Type, value_type: Type):
        self.name = name
        self.type_arguments = [key_type, value_type]


class Module:
    def __init__(self, name: str, *types: Type):
        self.name: str = name
        self.structs: list[Struct] = []
        self.structForName: dict[str, Struct] = dict()
        self.enums: list[Enumeration] = []
        self.enumForName: dict[str, Enumeration] = dict()

        for t in types:
            if type(t) is Struct:
                self.structs.append(typing.cast(Struct, t))
            elif type(t) is Enumeration:
                self.enums.append(typing.cast(Enumeration, t))
            else:
                raise ValueError("Attempting to add a type of kind "
                                 + str(type(t))
                                 + " to module " + self.name)


class Model:
    def __init__(self, name: str, *modules: Module):
        self.name: str = name
        self.modules: list[Module] = list(modules)
