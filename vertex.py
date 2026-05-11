import struct
import moderngl as mgl

class Vertex:
    def __init__(self, program: mgl.Program, **kwargs):
        """
        Automatically builds a vertex schema based on the shader program's 'in' variables.
        """
        self.attributes = []
        self.format_parts = []
        self.data_values = []

        # 1. Introspect the program attributes
        # ModernGL program.attributes contains metadata for all 'in' variables
        for name in program:
            attr = program[name]
            if isinstance(attr, mgl.Attribute):
                self.attributes.append(name)
                
                # attr.array_length and attr.dimension help determine the float count
                # e.g., vec3 = 3, float = 1
                count = attr.dimension
                self.format_parts.append(f"{count}f")
                
                # 2. Assign values from kwargs or default to zeros
                # We expect the user to pass kwargs with the same name as the shader variables
                val = kwargs.get(name, [0.0] * count)
                setattr(self, name, val)
                
                # Flatten lists/tuples for packing
                if isinstance(val, (list, tuple)):
                    self.data_values.extend(val)
                else:
                    self.data_values.append(val)

        self.format_str = " ".join(self.format_parts)

    def pack(self) -> bytes:
        """Packs the data into raw binary format for the GPU."""
        return struct.pack(f"{len(self.data_values)}f", *self.data_values)