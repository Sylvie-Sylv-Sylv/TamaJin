import moderngl as mgl
from PIL import Image


class Texture:
    """A wrapper for ModernGL texture objects
    Handles loading from disk via PIL, converting them to the correct format,
    and managing the OpenGL state configuration.
    """

    def __init__(self, ctx: mgl.Context, path: str, filter: int):
        """Initializes and uploads a texture to the GPU.

        Args:
            ctx (mgl.Context): The active ModernGL context.
            path (str): Filesystem path to the image file.
            filter (int): The OpenGL texture filter to use (e.g., mgl.NEAREST,
                mgl.LINEAR).

        """
        img = Image.open(path).convert("RGBA")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        self.texture = ctx.texture(size=img.size, components=4, data=img.tobytes())

        self.texture.filter = (filter, filter)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        self.texture.build_mipmaps()

    def use(self, location: int = 0):
        """Binds the texture to a specific texture unit.

        Args:
            location (int, optional): The texture unit index to bind to. Defaults to 0.

        """
        self.texture.use(location)

    def release(self):
        """Releases the OpenGL resources associated with this texture.

        This should be called explicitly when the texture is no longer needed
        to free up GPU memory.
        """
        self.texture.release()
