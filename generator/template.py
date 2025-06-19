import os

from generator.c_header_generator import CHeaderGenerator
from generator.c_python_conversion_generator import CPythonConversionGenerator
from generator.python_model_generator import PythonModuleGenerator
from model.model import Module


def f():
    print('Hi!')

def write_with_template(name: str, suffix: str, code: str, directory: str = '.'):
    input_path = os.path.join(directory, name + '.' + suffix + '.template')
    with open(input_path, 'r') as inputFile:
        content = inputFile.read().replace('@_code;', code.strip())
    output_path = os.path.join(directory, name + '.' + suffix)
    with open(output_path, 'w') as outputFile:
        outputFile.write(content)

def write_module_with_template(module: Module, directory: str = '.', module_prefix='python.generated'):
    python_generator = PythonModuleGenerator(module)
    python_generator.run()
    write_with_template(
        f'python_{module.name}_protocol',
        'py',
        python_generator.result(),
        directory)

    header_generator = CHeaderGenerator(module)
    header_generator.run()
    write_with_template(
        f'{module.name}_protocol',
        'h',
        header_generator.result(),
        directory)

    conversion_generator = CPythonConversionGenerator(module, module_prefix)
    conversion_generator.run()
    write_with_template(
        f'{module.name}_conversion',
        'h',
        conversion_generator.result()[0],
        directory)
    write_with_template(
        f'{module.name}_conversion',
        'c',
        conversion_generator.result()[1],
        directory)
