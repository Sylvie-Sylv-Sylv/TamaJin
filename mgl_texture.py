import moderngl as mgl

import i_texture

class MGLTexture(i_texture.ITexture):
        def __init__(self, texture : mgl.Texture):
                self.texture = texture