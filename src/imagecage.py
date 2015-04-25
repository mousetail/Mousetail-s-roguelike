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
        self.data={}
    def lookup(self, name):
        """
        looks up a item by filename, loads it if it dousn't exits yet
        loads from "../art folder"
        """
        if name in self.data:
            return self.data[name]
        else:
            img=pygame.image.load("../art/"+name)
            self.data[name]=img
            return img
    def release(self, name):
        del self.data[name]