class Config:
        def __init__(self, size: tuple[int, int] = (800, 600), fps: int = 60, substeps: int = 4):
                self.size = size
                self.fps = fps
                self.substeps = substeps