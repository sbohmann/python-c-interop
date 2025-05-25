import re
import os
from typing import Dict, List, Union, Optional
from dataclasses import dataclass
from codewriter import CodeWriter
from generator.codewriter import CodeWriterMode


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

        # Write constants
        if self.constants:
            writer.write_line("# Constants")
            for const in self.constants:
                if const.comment:
                    writer.write_line(f"# {const.comment}")
                writer.write_line(f"{const.name} = {const.value}")
            writer.write_line("")

        # Write enums
        if self.enums:
            writer.write_line("from enum import IntEnum")
            writer.write_line("")

            for enum in self.enums:
                if enum.comment:
                    writer.write_line(f"# {enum.comment}")
                writer.write_line(f"class {enum.name}(IntEnum):")
                with writer.indent():
                    for member in enum.members:
                        if member.comment:
                            writer.write_line(f"# {member.comment}")
                        writer.write_line(f"{member.name} = {member.value}")
                writer.write_line("")

        # Write structs
        if self.structs:
            writer.write_line("from dataclasses import dataclass")
            writer.write_line("from typing import Any")
            writer.write_line("")

            for struct in self.structs:
                if struct.comment:
                    writer.write_line(f"# {struct.comment}")
                writer.write_line("@dataclass")
                writer.write_line(f"class {struct.name}:")
                with writer.indent():
                    for member in struct.members:
                        if member.comment:
                            writer.write_line(f"# {member.comment}")
                        writer.write_line(f"{member.name}: Any  # type: {member.type}")
                writer.write_line("")

        # Save to file
        with open(output_path, 'w') as f:
            f.write(writer.get_value())


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
        print("Usage: python hsmlib.py <header_file> <output_file>")
        sys.exit(1)
    parse_header(sys.argv[1], sys.argv[2])