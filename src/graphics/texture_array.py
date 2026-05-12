import moderngl as mgl
from PIL import Image

from src.unit.i_unit import IUnit


class TextureArray(IUnit):
    def __init__(
        self,
        ctx: mgl.Context,
        textures: dict[str, str],
        filter: int
    ):
        """
        :param textures:
            {
                "grass": "textures/grass.png",
                "stone": "textures/stone.png",
                ...
            }
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
            size=(width, height, len(images)),
            components=4,
            data=data
        )

        # Common defaults
        self.texture.filter = (filter, filter)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        self.texture.build_mipmaps()

    def get_index(self, key: str) -> int:
        return self.key_to_index[key]

    def use(self, location: int = 0):
        self.texture.use(location)

    def release(self):
        self.texture.release()