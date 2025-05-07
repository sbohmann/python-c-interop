import typing
from abc import abstractmethod


class Type:
    name: str
    type_arguments: list['Type']

    @abstractmethod
    def __init__(self, name: str, type_arguments: list['Type']):
        pass


class PrimitiveType(Type):
    is_integer: bool

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
    name: str
    type: Type


class Struct(Type):
    fields: list[Field]

    def __init__(self, name: str, fields: list[Field]):
        self.name = name
        self.fields = fields


class Enumeration(Type):
    values: list[str]

    def __init__(self, name: str, values: list[str]):
        self.name = name
        self.values = values


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
    name: str
    structs: list[Struct]
    structForName: dict[str, Struct]
    enums: list[Enumeration]
    enumForName: dict[str, Enumeration]

    def __init__(self, name: str):
        self.name = name

    def add(self, new_type: Type):
        if type(new_type) is Struct:
            self.structs.append(typing.cast(Struct, new_type))
        elif type(new_type) is Enumeration:
            self.enums.append(typing.cast(Enumeration, new_type))
        else:
            raise ValueError("Attempting to add a type of kind "
                             + str(type(new_type))
                             + " to module " + self.name)


class Model:
    modules: list[Module]

    def addModule(self, moduleName: str):
        newModule = Module(moduleName)
        self.modules.append(newModule)
        return newModule
