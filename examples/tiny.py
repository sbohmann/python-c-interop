from c_interop.generator.c_header_generator import CHeaderGenerator
from c_interop.generator.c_python_conversion_generator import CPythonConversionGenerator
from c_interop.generator.python_model_generator import PythonModuleGenerator
from c_interop.model.model import Module, Enumeration, Struct, Field, PrimitiveType

colorEnum = Enumeration(
    'Color',
    'Red',
    'Green',
    'Blue')

car = Struct(
    'Car',
    Field('color', colorEnum),
    Field('x', PrimitiveType.UInt16))

module = Module(
    'tiny',
    colorEnum,
    car)

pythonGenerator = PythonModuleGenerator(module)
pythonGenerator.run()
print(pythonGenerator.result())

cGenerator = CHeaderGenerator(module)
cGenerator.run()
print(cGenerator.result())

conversionGenerator = CPythonConversionGenerator(module)
conversionGenerator.run()
print(conversionGenerator.result()[1])
