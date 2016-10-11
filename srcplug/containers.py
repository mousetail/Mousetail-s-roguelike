'''
Created on 22 apr. 2015

@author: Maurits
'''
import items

import pygame
from constants import *
import drops_calculator

class Container(items.Item):
    '''
    (ABSTRACT)
    A item that holds other items
    '''

    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, fakename=None, fakepname=None, range=1, startinginv=(),
                 **kwargs):
        '''
        Constructor
        '''
        items.Item.__init__(self, position, image, cage, world, name, pname, weight, fakename, fakepname, range, **kwargs
                            )
        self.item_capacity=kwargs["item_capacity"]
        self.weight_capacity=kwargs["weight_capacity"]
        if self.item_capacity==-1:
            self.item_capacity=None
        if self.weight_capacity==-1:
            self.weight_capacity=None
        self.inventory=drops_calculator.calculateDrops(world, cage, startinginv)
    def use(self):
        self.owner.say("do you want to a) put something in the ",self," b) take something out or c) see what is in the ", self)
        self.owner.redictInput(self.interpretEvent)
    def interpretEvent(self, event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_RETURN:
                return ("normal", None)
            elif event.key==pygame.K_a:
            
                self.say("what would you like to put in the ",self,"?")
                return (self.putInEvent, None)
            elif event.key==pygame.K_b:
            
                self.listItems()
                    
                
                return (self.takeOutEvent, None)
            elif event.key==pygame.K_c:
                self.listItems()
                return ("normal", None)
            else:
                return (self.interpretEvent, None)
        else:
            return (self.interpretEvent, None)
    def listItems(self):
        if len(self.inventory)==0:
            self.owner.say("the ",self," is empty")
        else:
            self.owner.say("the ",self," contains: ")
            for i in range(len(self.inventory)):
                self.owner.say("g}"+items.alphabet[i]+": ",self.inventory[i])
    def putInEvent(self, event):
        if event.type==pygame.KEYDOWN:
            
            itm=self.owner.removebyletter(event.unicode, True)
            if itm:
                return "normal", items.Command("other", action=self.putIn, item=itm)
                
        return self.putInEvent, None
    def __eq__(self, other):
        if isinstance(other, Container):
            if len(self.inventory)==0 and len(other.inventory)==0:
                return True
        return False
    def putIn(self, command):
        sc=True
        if isinstance(command.data["item"], Container) or command.data["item"] is self:
            self.say("R}you can't put a container into another container")
            sc=False
        elif self.item_capacity and len(self.inventory)>=self.item_capacity:
            self.say("R}the ",self," can't hold any more items!")
            sc=False
        elif self.weight_capacity and self.getWeight()-self.weight+sum(i.getWeight() for i in command.data["item"])>self.weight_capacity:
            self.say("R}the",self," can't hold any more weight!")
            sc=False
        if sc:
        
            self.inventory.extend(command.data["item"])
            
            self.say("you put the ",command.data["item"][0]," in the ",self)
            self.inventory.sort()
            return 50+int(12*(len(command.data["item"])**0.5))
        else:
            self.owner.addtoinventory(command.data["item"])
            return 0
    def takeOutEvent(self, event):
        
        if event.type==pygame.KEYDOWN:
            if event.unicode in items.alphabet and items.alphabet.index(event.unicode)<len(self.inventory):
                return "normal", items.Command("other", action=self.takeOut, letter=event.unicode)
            elif event.key==pygame.K_RETURN:
                return "normal", None
            else:
                self.owner.say("out of range, please try again")
            
            return self.takeOutEvent, None
        else:
            return self.takeOutEvent, None
    def takeOut(self, command):
        itm=self.inventory[items.alphabet.index(command.data["letter"])]
        self.owner.addtoinventory(itm)
        self.inventory.remove(itm)
        itm.owner=self.owner
        self.say("took a ",itm," out of the",self)
        return 100
    def getWeight(self):
        return self.weight+sum(i.getWeight() for i in self.inventory)