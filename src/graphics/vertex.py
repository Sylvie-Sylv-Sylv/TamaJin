import struct
import moderngl as mgl


class Vertex:
    def __init__(self, program: mgl.Program, is_instance: bool = False, **kwargs):
        """
        Automatically introspects shader attributes.

        Rules:
        - Regular vertex:
            takes attributes NOT starting with "i_"

        - Instance vertex:
            takes attributes starting with "i_"
        """

        self.attributes = []
        self.format_parts = []
        self.data_values = []

        for name in program:

            attr = program[name]

            if not isinstance(attr, mgl.Attribute):
                continue

            # ======================================================
            # Filter instance vs non-instance attributes
            # ======================================================

            is_instance_attr = name.startswith("i_")

            if is_instance != is_instance_attr:
                continue

            self.attributes.append(name)

            count = attr.dimension

            self.format_parts.append(f"{count}f")

            val = kwargs.get(name, [0.0] * count)

            setattr(self, name, val)

            if isinstance(val, (list, tuple)):
                self.data_values.extend(val)
            else:
                self.data_values.append(val)

        self.format_str = " ".join(self.format_parts)

    def pack(self) -> bytes:
        return struct.pack(f"{len(self.data_values)}f", *self.data_values)
