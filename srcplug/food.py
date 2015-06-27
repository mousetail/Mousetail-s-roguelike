'''
Created on 27 jun. 2015

@author: Maurits
'''
import items

class Food(items.Item):
    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, nutrition=0):
        items.Item.__init__(self, position, image, cage, world, name, pname, weight)
        self.nutrition=nutrition
    def eat(self):
        return "you eat the "+self.name