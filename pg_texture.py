import pygame as pg

import i_texture

class PGTexture(i_texture.ITexture):
        def __init__(self, surface : pg.Surface):
                self.surface = surface
        
