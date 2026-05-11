import moderngl as mgl

from i_texture import ITexture
from pg_texture import PGTexture
from texture import Texture

class ITextureLoader():
        """
                Utility class for loading textures using ModernGL.
                This class provides methods to load textures from files and create texture objects that can be used in rendering.
        """
        
        def load_texture(self, file_path : str) -> ITexture:
                pass

class PGTextureLoader(ITextureLoader):
        """
                Implementation of ITextureLoader using the Pillow library to load textures.
                This class can be used to load textures from image files and create texture objects that can be used in rendering.
        """
        def load_texture(self, file_path : str) -> ITexture:
                from PIL import Image
                import pygame as pg
                
                image = Image.open(file_path).convert("RGBA")
                mode = image.mode
                size = image.size
                data = image.tobytes()
                
                surface = pg.image.fromstring(data, size, mode)
                
                return PGTexture(surface)

class MGLTextureLoader(ITextureLoader):
        """
                Implementation of ITextureLoader using the Pillow library to load textures.
                This class can be used to load textures from image files and create texture objects that can be used in rendering.
        """
        def __init__(self, ctx : mgl.Context):
                self.ctx = ctx
        
        def load_texture(self, file_path : str) -> ITexture:
                from PIL import Image
                import moderngl as mgl
                
                image = Image.open(file_path).convert("RGBA")
                mode = image.mode
                size = image.size
                data = image.tobytes()
                
                texture = self.ctx.texture(size, 4, data)
                
                return Texture(texture)