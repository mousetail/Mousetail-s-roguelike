'''
Created on 22 apr. 2015

@author: Maurits
'''
import items

import pygame
from constants import *

class Container(items.Item):
    '''
    (ABSTRACT)
    A item that holds other items
    '''
    item_capacity=0
    weight_capacity=0

    def __init__(self, position):
        '''
        Constructor
        '''
        items.Item.__init__(self, position)
        
        self.inventory=[]
    def use(self):
        self.owner.say("do you want to a) put something in the "+self.name+" b) take something out or c) see what is in the "+self.name)
        self.owner.redictInput(self.interpretEvent)
    def interpretEvent(self, event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_RETURN:
                return ("normal", None)
            elif event.key==pygame.K_a:
            
                self.say("what would you like to put in the "+self.name+"?")
                return (self.putInEvent, None)
            elif event.key==pygame.K_b:
            
                self.owner.say("the "+self.name+"contains: ")
                for i in range(len(self.inventory)):
                    self.owner.say("g}"+items.alphabet[i]+": "+self.inventory[i].name)
                    
                
                return (self.takeOutEvent, None)
            elif event.key==pygame.K_c:
                self.owner.say("the "+self.name+"contains: ")
                for i in range(len(self.inventory)):
                    self.owner.say("g}"+items.alphabet[i]+": "+self.inventory[i].name)
                 
                return ("normal", None)
            else:
                return (self.interpretEvent, None)
        else:
            return (self.interpretEvent, None)
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
        if self.item_capacity and len(self.inventory)>=self.item_capacity:
            self.say("R}the "+self.name+" can't hold any more items!")
            return 1
        if self.weight_capacity and self.getWeight()-self.weight+sum(i.getWeight() for i in command.data["item"])>self.weight_capacity:
            self.say("R}the "+self.name+" can't hold any more weight!")
            return 1
        
        self.inventory.extend(command.data["item"])
        
        self.say("put the "+command.data["item"][0].name+" in the "+self.name)
        self.inventory.sort()
        return 50+int(12*(len(command.data["item"])**0.5))
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
        self.say("took a "+itm.name+" out of the "+self.name)
        return 100
    def getWeight(self):
        return self.weight+sum(i.getWeight() for i in self.inventory)
#@getitembyname.ri("sack", 5, 0,20,(ITM_ITEM, ITM_CONTAINER))
class Sack (Container):
    name="sack"
    pname="sacks"
    weight=2
    
    item_capacity=3
    weight_capacity=10
    def __init__(self, position, world, cage):
        #print "sacked"
        Container.__init__(self, position)
        self.image=cage.lookup("sack.png")
        self.inventory.append(getitembyname.itemRandomizer.fastrandomitem([-1,-1],world, cage, 1, (ITM_ARMOR,)))