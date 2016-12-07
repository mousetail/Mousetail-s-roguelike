'''
Created on 27 jun. 2015

@author: Maurits
'''
import items

class Food(items.Item):
    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, fake_name=None,
                 fake_pname=None, range=1, nutrition=0, **kwargs):
        items.Item.__init__(self, position, image, cage, world, name, pname, weight, fake_name, fake_pname, range, **kwargs)
        self.nutrition = nutrition
    def eat(self):
        return ("you eat the " + str(self), self.nutrition)
