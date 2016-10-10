'''
Created on 2 jan. 2015

@author: Maurits
'''
import pygame


class ImageCage(object):
    '''
    Stores all images
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.data = {}

    def getProxy(self, name, alpha):
        return ImageProxy(self, name, alpha)

    def lookup(self, name, alpha):
        """
        looks up a item by filename, loads it if it dousn't exits yet
        loads from "../art folder"
        """
        if name in self.data:
            return self.data[name]
        else:
            if alpha:
                img = pygame.image.load("../art/" + name).convert_alpha()
            else:
                img = pygame.image.load("../art/" + name).convert()
            self.data[name] = img
            return img

    def release(self, name):
        del self.data[name]


class ImageProxy:
    def __init__(self, cage, name, alpha=True):
        # type: (ImageCage, str, bool) -> None
        self.name = name
        self.cage = cage
        self.surf = cage.lookup(self.name, alpha)
        self.alpha = alpha

    def toSurf(self):
        return self.surf

    def subsurface(self, rect):
        return self.toSurf().subsurface(rect)

    def get_height(self):
        return self.surf.get_height()

    def get_width(self):
        return self.surf.get_width()
