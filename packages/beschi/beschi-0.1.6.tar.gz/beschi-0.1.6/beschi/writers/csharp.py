from ..protocol import Protocol, BASE_TYPE_SIZES
from ..writer import Writer
from .. import LIB_NAME, LIB_VERSION

LANGUAGE_NAME = "CSharp"


class CSharpWriter(Writer):
    language_name = LANGUAGE_NAME
    default_extension = ".cs"

    def __init__(self, p: Protocol):
        super().__init__(protocol=p, tab="    ")

        self.type_mapping["byte"] = "byte"
        self.type_mapping["bool"] = "bool"
        self.type_mapping["uint16"] = "ushort"
        self.type_mapping["int16"] = "short"
        self.type_mapping["uint32"] = "uint"
        self.type_mapping["int32"] = "int"
        self.type_mapping["uint64"] = "ulong"
        self.type_mapping["int64"] = "long"
        self.type_mapping["float"] = "float"
        self.type_mapping["double"] = "double"


    def deserializer(self, var_type: str, var_name: str, parent: str = "this") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        label = var_name
        if label.endswith("_i]"):
            label = "i_"
        if var_type in BASE_TYPE_SIZES:
            func = None
            if var_type == "byte":
                func = "ReadByte"
            elif var_type == "bool":
                func = "ReadBoolean"
            elif var_type == "uint16":
                func = "ReadUInt16"
            elif var_type == "int16":
                func = "ReadInt16"
            elif var_type == "uint32":
                func = "ReadUInt32"
            elif var_type == "int32":
                func = "ReadInt32"
            elif var_type == "uint64":
                func = "ReadUInt64"
            elif var_type == "int64":
                func = "ReadInt64"
            elif var_type == "float":
                func = "ReadSingle"
            elif var_type == "double":
                func = "ReadDouble"
            else:
                raise NotImplementedError(f"Type {var_type} not deserializable yet.")
            return [f"{pref}{var_name} = br.{func}();"]
        elif var_type == "string":
            return [
                f"uint {label}Length = br.ReadUInt32();",
                f"byte[] {label}Buffer = br.ReadBytes((int){label}Length);",
                f"{pref}{var_name} = System.Text.Encoding.UTF8.GetString({label}Buffer);",
            ]
        elif var_type in self.protocol.structs:
            return [
                f"{pref}{var_name} = {var_type}.FromBytes(br);"
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                f"uint {var_name}Length = br.ReadUInt32();",
                f"{pref}{var_name} = new {self.get_var(interior)}[{var_name}Length];",
                f"for (int {var_name}_i = 0; {var_name}_i < {var_name}Length; {var_name}_i++)",
                "{",
            ]
            out += [
                self.tab + deser for deser in self.deserializer(
                    interior, f"{var_name}[{var_name}_i]", parent
                )
            ]
            out += ["}"]
            return out
        else:
            raise NotImplementedError(f"Type {var_type} not deserializable yet.")


    def serializer(self, var_type: str, var_name: str, parent: str = "this") -> list[str]:
        if parent:
            pref = parent + "."
        else:
            pref = ""
        if var_type in BASE_TYPE_SIZES:
            return [f"bw.Write({pref}{var_name});"]
        elif var_type == "string":
            return [
                f"byte[] {var_name}Buffer = System.Text.Encoding.UTF8.GetBytes({pref}{var_name});",
                f"bw.Write((uint){var_name}Buffer.Length);",
                f"bw.Write({var_name}Buffer);",
            ]
        elif var_type in self.protocol.structs:
            return [
                f"{pref}{var_name}.WriteBytes(bw);"
            ]
        elif var_type[0] == "[" and var_type[-1] == "]":
            interior = var_type[1:-1]
            out = [
                f"bw.Write((uint){pref}{var_name}.Length);",
                f"foreach ({self.get_var(interior)} el in {pref}{var_name})",
                "{"
            ]
            out += [self.tab + ser for ser in self.serializer(interior, "el", None)]
            out += ["}"]
            return out
        else:
            raise NotImplementedError(f"Type {var_type} not serializable yet.")


    def gen_measurement(self, s: tuple[str, list[tuple[str,str]]], accessor_prefix: str = "") -> tuple[list[str], int]:
        lines: list[str] = []

        accum = 0
        if self.protocol.is_simple(s[0]):
            lines.append(f"return {self.protocol.calculate_size(s[0])};")
        else:
            size_init = "int size = 0;"
            lines.append(size_init)

            for var_name, var_type in s[1]:
                if self.protocol.is_simple(var_type):
                    accum += self.protocol.calculate_size(var_type)
                else:
                    if var_type == "string":
                        accum += BASE_TYPE_SIZES["uint32"]
                        lines.append(f"size += System.Text.Encoding.UTF8.GetBytes({accessor_prefix}{var_name}).Length;")
                    elif var_type == "[string]":
                        accum += BASE_TYPE_SIZES["uint32"]
                        lines.append(f"foreach (var s in {accessor_prefix}{var_name})")
                        lines.append("{")
                        lines.append(f"{self.tab}size += {BASE_TYPE_SIZES['uint32']} + System.Text.Encoding.UTF8.GetBytes(s).Length;")
                        lines.append("}")
                    elif var_type[0] == "[" and var_type[-1] == "]":
                        listed_var_type = var_type[1:-1]
                        if self.protocol.is_simple(listed_var_type):
                            accum += BASE_TYPE_SIZES["uint32"]
                            lines.append(f"size += {accessor_prefix}{var_name}.Length * {self.protocol.calculate_size(listed_var_type)};")
                        else:
                            accum += BASE_TYPE_SIZES["uint32"]
                            lines.append(f"foreach (var s in {accessor_prefix}{var_name})")
                            lines.append("{")
                            clines, caccum = self.gen_measurement((var_type, self.protocol.structs[listed_var_type]), f"s.")
                            if clines[0] == size_init:
                                clines = clines[1:]
                            clines.append(f"size += {caccum};")
                            lines += [f"{self.tab}{l}" for l in clines]
                            lines.append("}")
                    else:
                        clines, caccum = self.gen_measurement((var_type, self.protocol.structs[var_type]), f"{accessor_prefix}{var_name}.")
                        if clines[0] == size_init:
                            clines = clines[1:]
                        lines += clines
                        accum += caccum
        return lines, accum

    def gen_struct(self, s: tuple[str, list[tuple[str,str]]]):
        is_message = s[0] in self.protocol.messages
        if is_message:
            self.write_line(f"public class {s[0]} : Message")
        else:
            self.write_line(f"public class {s[0]}")
        self.write_line("{")
        self.indent_level += 1

        for var_name, var_type in s[1]:
            if var_type[0] == "[" and var_type[-1] == "]":
                self.write_line(f"public {self.get_var(var_type[1:-1])}[] {var_name};")
            else:
                self.write_line(f"public {self.get_var(var_type)} {var_name};")

        if is_message:
            self.write_line()
            self.write_line(f"public override MessageType GetMessageType() {{ return MessageType.{s[0]}Type; }}")
            self.write_line()
            self.write_line("public override int GetSizeInBytes()")
            self.write_line("{")
            self.indent_level +=1
            measure_lines, accumulator = self.gen_measurement(s, "this.")
            [self.write_line(s) for s in measure_lines]
            if accumulator > 0:
                self.write_line(f"size += {accumulator};")
            if len(measure_lines) > 1:
                self.write_line(f"return size;")
            self.indent_level -=1
            self.write_line("}")

        self.write_line()
        override = ""
        tag = ""
        if is_message:
            override = "override "
            tag = ", bool tag"
        self.write_line(f"public {override}void WriteBytes(BinaryWriter bw{tag})")
        self.write_line("{")
        self.indent_level += 1
        if is_message:
            self.write_line("if (tag)")
            self.write_line("{")
            self.indent_level += 1
            self.write_line(f"bw.Write((byte)MessageType.{s[0]}Type);")
            self.indent_level -= 1
            self.write_line("}")
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.serializer(var_type, var_name)]
        self.indent_level -= 1
        self.write_line("}")

        self.write_line()
        self.write_line(f"public static {s[0]} FromBytes(BinaryReader br)")
        self.write_line("{")
        self.indent_level += 1
        if is_message:
            self.write_line("try")
            self.write_line("{")
            self.indent_level += 1
        self.write_line(f"{s[0]} n{s[0]} = new {self.get_var(s[0])}();")
        for var_name, var_type in s[1]:
            [self.write_line(s) for s in self.deserializer(var_type, var_name, f"n{s[0]}")]
        self.write_line(f"return n{s[0]};")
        if is_message:
            self.indent_level -= 1
            self.write_line("}")
            self.write_line("catch (System.IO.EndOfStreamException)")
            self.write_line("{")
            self.indent_level += 1
            self.write_line("return null;")
            self.indent_level -= 1
            self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")

        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

    def gen_message(self, m: tuple[str, list[tuple[str,str]]]):
        self.gen_struct(m)

    def generate(self) -> str:
        self.output = []

        self.write_line(f"// This file was automatically generated by {LIB_NAME} v{LIB_VERSION}.")
        self.write_line( "// <https://github.com/sjml/beschi>")
        self.write_line(f"// Do not edit directly.")
        self.write_line()
        self.write_line("using System;")
        self.write_line("using System.IO;")
        self.write_line("using System.Text;")
        self.write_line("using System.Collections.Generic;")
        self.write_line()

        if self.protocol.namespace:
            self.write_line(f"namespace {self.protocol.namespace}")
            self.write_line("{")
            self.indent_level += 1

        msg_types = [mt for mt in self.protocol.messages.keys()]

        self.write_line("public enum MessageType")
        self.write_line("{")
        self.indent_level += 1
        [self.write_line(f"{k}Type = {i+1},") for i, k in enumerate(msg_types)]
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        self.write_line("public abstract class Message {")
        self.indent_level += 1
        self.write_line("abstract public MessageType GetMessageType();")
        self.write_line("abstract public void WriteBytes(BinaryWriter bw, bool tag);")
        self.write_line("abstract public int GetSizeInBytes();")
        self.write_line()
        self.write_line("public static Message[] ProcessRawBytes(BinaryReader br)")
        self.write_line("{")
        self.indent_level += 1
        self.write_line("List<Message> msgList = new List<Message>();")
        self.write_line("while (br.BaseStream.Position < br.BaseStream.Length)")
        self.write_line("{")
        self.indent_level += 1
        self.write_line("byte msgType = br.ReadByte();")
        self.write_line("switch (msgType)")
        self.write_line("{")
        self.indent_level += 1
        for msg_type in msg_types:
            self.write_line(f"case (byte)MessageType.{msg_type}Type:")
            self.indent_level += 1
            self.write_line(f"msgList.Add({msg_type}.FromBytes(br));")
            self.write_line("break;")
            self.indent_level -= 1
        self.write_line("default:")
        self.indent_level += 1
        self.write_line("msgList.Add(null);")
        self.write_line("break;")
        self.indent_level -= 1
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("if (msgList[msgList.Count-1] == null) {")
        self.indent_level += 1
        self.write_line("break;")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line("return msgList.ToArray();")
        self.indent_level -= 1
        self.write_line("}")
        self.indent_level -= 1
        self.write_line("}")
        self.write_line()

        for s in self.protocol.structs.items():
            self.gen_struct(s)

        for m in self.protocol.messages.items():
            self.gen_message(m)

        if self.protocol.namespace:
            self.indent_level -= 1
            self.write_line("}")

        self.write_line()
        assert self.indent_level == 0

        return "\n".join(self.output)
