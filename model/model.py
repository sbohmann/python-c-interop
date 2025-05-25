import typing
from abc import abstractmethod
from lib2to3.pgen2.tokenize import double3prog


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
    Double: 'PrimitiveType'
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
PrimitiveType.Double = PrimitiveType('Double')
PrimitiveType.String = PrimitiveType('String')


class Constant:
    def __init__(self, name: str, value):
        self.name = name
        self.type = type
        if type(value) is int:
            self.type = PrimitiveType.Integer
        elif type(value) is bool:
            self.type = PrimitiveType.Boolean
        elif type(value) is float:
            self.type = PrimitiveType.Double
        elif type(value) is str:
            self.type = PrimitiveType.String
        else:
            raise ValueError("Unsupported constant type: " + str(type(value)))
        self.value = value


class Field:
    def __init__(self, name: str, type_: Type):
        self.name: str = name
        self.type: Type = type_


class Struct(Type):
    def __init__(self, name: str, *fields: Field, typedef=False):
        super().__init__(name)
        self.fields: list[Field]
        self.typedef = typedef
        if len(fields) == 0:
            raise ValueError("No fields provided")
        self.fields = list(fields)


class Enumeration(Type):
    def __init__(self, name: str, *values: str, first_ordinal: int = 1, typedef: bool = False) -> None:
        super().__init__(name)
        if len(values) == 0:
            raise ValueError("No values provided")
        self.values: list[str] = list(values)
        self.typedef = typedef
        self.first_ordinal = first_ordinal


class List(Type):
    def __init__(self, element_type: Type, maximum_length: Constant = None):
        super().__init__(f'List[{element_type.name}]')
        self.element_type = element_type
        self.type_arguments = [element_type]
        if maximum_length is not None:
            if maximum_length.type is not PrimitiveType.Integer:
                raise ValueError(f'Unsupported list maximum length type: ${maximum_length.type}')
            self.maximum_length: str = maximum_length.name


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
