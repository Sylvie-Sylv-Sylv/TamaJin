import moderngl as mgl
from PIL import Image


class Texture:
    """
    A wrapper for ModernGL texture objects, handling loading from disk via PIL
    and OpenGL state configuration.
    """

    def __init__(self, ctx: mgl.Context, path: str, filter: int):
        """
        Initializes and uploads a texture to the GPU.

        :param ctx: The ModernGL context.
        :param path: Filesystem path to the image file.
        :param filter: The OpenGL texture filter to use (e.g., mgl.NEAREST, mgl.LINEAR).
        """
        img = Image.open(path).convert("RGBA")
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        self.texture = ctx.texture(size=img.size, components=4, data=img.tobytes())

        self.texture.filter = (filter, filter)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        self.texture.build_mipmaps()

    def use(self, location: int = 0):
        """
        Binds the texture to a specific texture unit.

        :param location: The texture unit index to bind to.
        """
        self.texture.use(location)

    def release(self):
        """
        Releases the OpenGL resources associated with this texture.
        Should be called when the texture is no longer needed.
        """
        self.texture.release()
