from generator.c_header_generator import CHeaderGenerator
from generator.python_module_generator import PythonModuleGenerator
from model.model import Module, Enumeration, Struct, Field, PrimitiveType

colorEnum = Enumeration('Color', 'Red', 'Green', 'Blue')

module = Module(
    'tiny',
    colorEnum,
    Struct(
        'Car',
        Field('color', colorEnum),
    Field('x', PrimitiveType.UInt16)))

pythonGenerator = PythonModuleGenerator(module)
pythonGenerator.run()
print(pythonGenerator.result())

cGenerator = CHeaderGenerator(module)
cGenerator.run()
print(cGenerator.result())
