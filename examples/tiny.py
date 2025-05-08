from generator.PythonModuleGenerator import PythonModuleGenerator
from model.model import Module, Enumeration, Struct, Field, PrimitiveType

colorEnum = Enumeration('Colors', 'Red', 'Green', 'Blue')

module = Module(
    'tiny',
    colorEnum,
    Struct(
        'Car',
        Field('color', colorEnum),
    Field('x', PrimitiveType.UInt16)))

generator = PythonModuleGenerator(module)
generator.run()
print(generator.result())
