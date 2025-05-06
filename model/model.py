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
    is_primitive: bool
    type_arguments: list['Type']
    @abstractmethod
    def __init__(self, name: str, type_arguments: list['Type']):
        pass

class PrimitiveType(Type):
    def __init__(self, name: str):
        self.name = name
        self.is_primitive = True

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

class Struct:
    name: str
    fields: list[Field]

class Enum:
    values: list[str]

class Module:
    structs: list[Struct]
    structForName: dict[str, Struct]
    enums: list[Enum]
    enumForName: dict[str, Enum]

class Model:
    modules: list[Module]
