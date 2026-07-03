import moderngl as mgl
from PIL import Image


class TextureArray:
    """
    Manages an OpenGL Texture Array (GL_TEXTURE_2D_ARRAY).

    This allows multiple textures of the same dimension to be stored in a single
    GPU resource, accessible via an index in shaders to reduce draw calls.

    Attributes:
        key_to_index (dict[str, int]): Maps texture keys to their corresponding
            index in the texture array.
        texture (mgl.TextureArray): The ModernGL texture array object.

    """

    def __init__(self, ctx: mgl.Context, textures: dict[str, str], filter: int):
        """Initializes and uploads a texture array to the GPU.

        Args:
            ctx (mgl.Context): The active ModernGL context.
            textures (dict[str, str]): A dictionary mapping string keys to
                filesystem  paths (e.g., {"grass": "textures/grass.png", "stone":
                "..."}).
            filter (int): The OpenGL texture filter to use (e.g., mgl.NEAREST,
                mgl.LINEAR).

        Raises:
            ValueError: If the `textures` dictionary is empty, or if the provided
                images do not all share the exact same dimensions.

        """

        if not textures:
            raise ValueError("TextureArray requires at least one texture")

        self.key_to_index: dict[str, int] = {}

        images = []

        # Load images and assign indices
        for index, (key, path) in enumerate(textures.items()):
            img = Image.open(path).convert("RGBA")
            img = img.transpose(Image.FLIP_TOP_BOTTOM)

            images.append(img)
            self.key_to_index[key] = index

        # Validate dimensions
        width, height = images[0].size

        for img in images:
            if img.size != (width, height):
                raise ValueError(
                    "All textures in a TextureArray must have the same dimensions"
                )

        # Merge all image data into one byte stream
        data = b"".join(img.tobytes() for img in images)

        # Create OpenGL texture array
        self.texture = ctx.texture_array(
            size=(width, height, len(images)), components=4, data=data
        )

        # Common defaults
        self.texture.filter = (filter, filter)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        self.texture.build_mipmaps()

    def get_index(self, key: str) -> int:
        """Returns the index of a texture in the array based on its key.

        Args:
            key (str): The string identifier of the texture.

        Returns:
            int: The index of the texture in the array.

        """
        return self.key_to_index[key]

    def use(self, location: int = 0):
        """Binds the texture array to a specific texture unit.

        Args:
            location (int, optional): The texture unit index to bind to. Defaults to 0.

        """
        self.texture.use(location)

    def release(self):
        """Releases the OpenGL resources associated with this texture array.

        This should be called explicitly when the texture array is no longer needed
        to free up GPU memory.
        """
        self.texture.release()
