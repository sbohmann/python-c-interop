from abc import abstractmethod
from enum import Enum


class KindOfType(Enum):
    Primitive = 1
    Struct = 2
    Enum = 3
    List = 4
    Set = 5
    Map = 6


class Type:
    name: str
    kind_of_type: KindOfType
    type_arguments: list['Type']

    @abstractmethod
    def __init__(self, name: str, type_arguments: list['Type']):
        pass


class PrimitiveType(Type):
    def __init__(self, name: str):
        self.name = name
        self.kind_of_type = KindOfType.Primitive
        self.type_arguments = []


PrimitiveType.Boolean = PrimitiveType('Boolean')
PrimitiveType.Integer = PrimitiveType('Integer')
PrimitiveType.Int8 = PrimitiveType('Int8')
PrimitiveType.UInt8 = PrimitiveType('UInt8')
PrimitiveType.Int16 = PrimitiveType('Int16')
PrimitiveType.UInt16 = PrimitiveType('UInt16')
PrimitiveType.Int32 = PrimitiveType('Int32')
PrimitiveType.UInt32 = PrimitiveType('UInt32')
PrimitiveType.Int64 = PrimitiveType('Int64')
PrimitiveType.UInt64 = PrimitiveType('UInt64')
PrimitiveType.Float = PrimitiveType('Float')
PrimitiveType.String = PrimitiveType('String')


class Field:
    name: str
    type: Type


class Struct(Type):
    fields: list[Field]

    def __init__(self, name: str, fields: list[Field]):
        self.name = name
        self.kind_of_type = KindOfType.Struct
        self.fields = fields


class Enum(Type):
    values: list[str]

    def __init__(self, name: str, values: list[str]):
        self.name = name
        self.kind_of_type = KindOfType.Enum
        self.values = values


class List(Type):
    def __init__(self, name: str, element_type: Type):
        self.name = name
        self.kind_of_type = KindOfType.List
        self.type_arguments = [element_type]


class Set(Type):
    def __init__(self, name: str, element_type: Type):
        self.name = name
        self.kind_of_type = KindOfType.Set
        self.type_arguments = [element_type]


class Map(Type):
    def __init__(self, name: str, key_type: Type, value_type: Type):
        self.name = name
        self.kind_of_type = KindOfType.Map
        self.type_arguments = [key_type, value_type]


class Module:
    structs: list[Struct]
    structForName: dict[str, Struct]
    enums: list[Enum]
    enumForName: dict[str, Enum]


class Model:
    modules: list[Module]
