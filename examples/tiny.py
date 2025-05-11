from generator.c_header_generator import CHeaderGenerator
from generator.c_python_conversion_generator import CPythonConversionGenerator
from generator.pyi_generator import PythonModuleInformationGenerator
from model.model import Module, Enumeration, Struct, Field, PrimitiveType

colorEnum = Enumeration('Color', 'Red', 'Green', 'Blue')

module = Module(
    'tiny',
    colorEnum,
    Struct(
        'Car',
        Field('color', colorEnum),
    Field('x', PrimitiveType.UInt16)))

pythonGenerator = PythonModuleInformationGenerator(module)
pythonGenerator.run()
print(pythonGenerator.result())

cGenerator = CHeaderGenerator(module)
cGenerator.run()
print(cGenerator.result())

conversionGenerator = CPythonConversionGenerator(module)
conversionGenerator.run()
print(conversionGenerator.result()[1])
