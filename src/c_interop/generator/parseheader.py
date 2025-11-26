import re
from dataclasses import dataclass
from typing import List, Optional

from codewriter import CodeWriter
from codewriter import CodeWriterMode


@dataclass
class CConstant:
    name: str
    value: str
    comment: Optional[str] = None


@dataclass
class CEnumMember:
    name: str
    value: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class CEnum:
    name: str
    members: List[CEnumMember]
    comment: Optional[str] = None


@dataclass
class CStructMember:
    name: str
    type: str
    comment: Optional[str] = None


@dataclass
class CStruct:
    name: str
    members: List[CStructMember]
    comment: Optional[str] = None


class HeaderParser:
    def __init__(self):
        self.constants: List[CConstant] = []
        self.enums: List[CEnum] = []
        self.structs: List[CStruct] = []

    def _clean_comment(self, comment: str) -> str:
        """Clean C-style comments."""
        if not comment:
            return ""
        return re.sub(r'/\*|\*/|//', '', comment).strip()

    def _parse_constant(self, line: str) -> Optional[CConstant]:
        """Parse #define constant."""
        define_match = re.match(r'#define\s+(\w+)\s+(.+?)(?:/[/*](.+?)(?:\*/)?)?$', line)
        if define_match:
            name, value, comment = define_match.groups()
            return CConstant(name, value.strip(), self._clean_comment(comment))
        return None

    def _parse_enum(self, content: str, start_idx: int) -> tuple[Optional[CEnum], int]:
        """Parse enum definition."""
        enum_match = re.match(r'enum\s+(\w+)\s*{', content[start_idx:])
        if not enum_match:
            return None, start_idx

        name = enum_match.group(1)
        members = []
        current_value = 0
        idx = start_idx + enum_match.end()

        while idx < len(content):
            line = content[idx:content.find('\n', idx)].strip()
            if '}' in line:
                break

            member_match = re.match(r'(\w+)(?:\s*=\s*([^,]+))?\s*,?\s*(?:/[/*](.+?)(?:\*/)?)?$', line)
            if member_match:
                member_name, value, comment = member_match.groups()
                if value:
                    try:
                        current_value = eval(value)
                    except:
                        current_value = value
                members.append(CEnumMember(member_name, str(current_value), self._clean_comment(comment)))
                current_value = int(current_value) + 1

            idx = content.find('\n', idx) + 1

        return CEnum(name, members), idx

    def _parse_struct(self, content: str, start_idx: int) -> tuple[Optional[CStruct], int]:
        """Parse struct definition."""
        struct_match = re.match(r'struct\s+(\w+)\s*{', content[start_idx:])
        if not struct_match:
            return None, start_idx

        name = struct_match.group(1)
        members = []
        idx = start_idx + struct_match.end()

        while idx < len(content):
            line = content[idx:content.find('\n', idx)].strip()
            if '}' in line:
                break

            member_match = re.match(r'(\w+)\s+(\w+)\s*;(?:\s*/[/*](.+?)(?:\*/)?)?$', line)
            if member_match:
                type_name, member_name, comment = member_match.groups()
                members.append(CStructMember(member_name, type_name, self._clean_comment(comment)))

            idx = content.find('\n', idx) + 1

        return CStruct(name, members), idx

    def parse_file(self, filepath: str) -> None:
        """Parse a C header file."""
        with open(filepath, 'r') as f:
            content = f.read()

        idx = 0
        while idx < len(content):
            line = content[idx:content.find('\n', idx)].strip()

            if line.startswith('#define'):
                constant = self._parse_constant(line)
                if constant:
                    self.constants.append(constant)

            elif line.startswith('enum'):
                enum_def, new_idx = self._parse_enum(content, idx)
                if enum_def:
                    self.enums.append(enum_def)
                    idx = new_idx
                    continue

            elif line.startswith('struct'):
                struct_def, new_idx = self._parse_struct(content, idx)
                if struct_def:
                    self.structs.append(struct_def)
                    idx = new_idx
                    continue

            idx = content.find('\n', idx) + 1
            if idx <= 0:
                break

    def generate_module(self, output_path: str) -> None:
        """Generate Python module from parsed header."""
        writer = CodeWriter(CodeWriterMode.Python)
        
        # Import statements
        writer.writeln("from dataclasses import dataclass")
        writer.writeln("from typing import Dict, List, Union, Optional")
        writer.writeln("from enum import IntEnum")
        writer.writeln()

        for const in self.constants:
            if const.comment:
                writer.writeln("# ", const.comment)
            writer.writeln(const.name, " = ", const.value)
            writer.writeln()

        for enum in self.enums:
            if enum.comment:
                writer.writeln("# ", enum.comment)
            writer.write("class ", enum.name, "(IntEnum):")
        
            def write_enum_body():
                for member in enum.members:
                    if member.comment:
                        writer.writeln("# ", member.comment)
                    writer.writeln(member.name, " = ", member.value)
        
            writer.block(write_enum_body)
            writer.writeln()

        for struct in self.structs:
            if struct.comment:
                writer.writeln("# ", struct.comment)
            writer.writeln("@dataclass")
            writer.write("class ", struct.name, ":")
        
            def write_struct_body():
                for member in struct.members:
                    if member.comment:
                        writer.writeln("# ", member.comment)
                    writer.writeln(member.name, ": ", self._get_python_type(member.type))
        
            writer.block(write_struct_body)
            writer.writeln()

        # Write output
        with open(output_path, 'w') as outputFile:
            outputFile.write(writer.result())

    def _get_python_type(self, c_type: str) -> str:
        """Convert C type to Python type annotation."""
        type_map = {
            'bool': 'bool',
            'char': 'int',
            'unsigned char': 'int',
            'short': 'int',
            'unsigned short': 'int',
            'int': 'int',
            'unsigned int': 'int',
            'long': 'int',
            'unsigned long': 'int',
            'float': 'float',
            'double': 'float',
            'char*': 'str',
            'void*': 'Any'
        }
        return type_map.get(c_type, 'Any')  # Default to Any for unknown types


def parse_header(header_path: str, output_path: str) -> None:
    """
    Parse a C header file and generate a Python module.

    Args:
        header_path: Path to the C header file
        output_path: Path where to save the generated Python module
    """
    parser = HeaderParser()
    parser.parse_file(header_path)
    parser.generate_module(output_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python parseheader.py <header_file> <output_file>")
        sys.exit(1)
    parse_header(sys.argv[1], sys.argv[2])


def generate_something(writer: CodeWriter, class_name: str, fields: list[str]):
    # CodeWriter with comma separation for generated code
    writer.writeln("class ", class_name, ":")
    
    def write_body():
        for field in fields:
            # f-string for the comment because it's not part of the generated code
            debug_info = f"Adding field: {field}"
            print(debug_info)  # or logger.debug(debug_info)
            
            writer.writeln(field, ": str = ''")
    
    writer.block(write_body)