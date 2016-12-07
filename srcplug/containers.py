'''
Created on 22 apr. 2015

@author: Maurits
'''
import items

import pygame
from constants import *
from sys import stderr
import drops_calculator


class Container(items.Item, items.BasicContainer):
    '''
    (ABSTRACT)
    A item that holds other items
    '''

    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, fakename=None,
                 fakepname=None, range=1, startinginv=(), **kwargs):
        '''
        Constructor
        '''
        items.Item.__init__(self, position, image, cage, world, name, pname, weight, fakename, fakepname, range,
                            **kwargs)
        items.BasicContainer.__init__(self)
        self.item_capacity = kwargs["item_capacity"]
        self.weight_capacity = kwargs["weight_capacity"]
        if self.item_capacity == -1:
            self.item_capacity = None
        if self.weight_capacity == -1:
            self.weight_capacity = None
        for item in drops_calculator.calculateDrops(world, cage, startinginv):
            print "adding item", item
            if self.checkAdd(item):
                print "check: " + self.checkAdd(item)
            else:
                self.addToInventory(item)
        print "made sack, inventory: ", self.inventory, startinginv

    def __eq__(self, other):
        if isinstance(other, Container):
            if len(self.inventory) == 0 and len(other.inventory) == 0:
                return True
        return False

    def getWeight(self):
        weight = self.weight
        for key, value in self.inventory.items():
            for item in value:
                weight += item.getWeight()
        return weight

    def checkAdd(self, itm):
        if self.item_capacity >= 0 and self.item_capacity <= len(self.inventory):
            return ("the bag can not hold any more weight")
        if self.weight_capacity >= 0 and self.getWeight() - self.weight + itm.getWeight() > self.weight_capacity:
            return ("the bag can not hold any more items")
        return items.BasicContainer.checkAdd(self, itm)
