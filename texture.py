import moderngl as mgl
import pygame as pg
from PIL import Image

from i_unit import IUnit

class Texture(IUnit):
    def __init__(self, ctx: mgl.Context, path: str, filter: int):
        img = Image.open(path).convert('RGBA')
        img = img.transpose(Image.FLIP_TOP_BOTTOM)

        self.texture = ctx.texture(
            size=img.size, 
            components=4,
            data=img.tobytes()
        )

        # Common defaults
        self.texture.filter = (filter, filter)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        # Optional but usually desirable
        self.texture.build_mipmaps()

    def use(self, location: int = 0):
        self.texture.use(location)

    def release(self):
        self.texture.release()