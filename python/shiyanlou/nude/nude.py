import sys
import os
import _io  #built-in module
from collections import namedtuple
from PIL import Image

Skin=namedtuple("Skin","id skin region x y")

class Nude:
    def __init__(self,path_or_image):
        if isinstance(path_or_image,Image.Image):
            self.image=path_or_image
        elif isinstance(path_or_image,str):
            self.image=Image.open(path_or_image)
        assert isinstance(self.image,Image.Image)
        bands=self.image.getbands()
        
