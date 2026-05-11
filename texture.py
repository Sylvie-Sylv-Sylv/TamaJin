import moderngl as mgl
import pygame as pg

from i_unit import IUnit

class Texture(IUnit):
    def __init__(self, ctx: mgl.Context, path: str):
        surface = pg.image.load(path).convert_alpha()

        surface = pg.transform.flip(surface, False, True)

        self.width = surface.get_width()
        self.height = surface.get_height()

        data = pg.image.tobytes(surface, "RGBA")

        # Create GPU texture
        self.texture = ctx.texture(
            (self.width, self.height),
            4,
            data
        )

        # Common defaults
        self.texture.filter = (mgl.LINEAR, mgl.LINEAR)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

        # Optional but usually desirable
        self.texture.build_mipmaps()

    def use(self, location: int = 0):
        self.texture.use(location)

    def release(self):
        self.texture.release()