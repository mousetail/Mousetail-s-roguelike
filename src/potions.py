'''
Created on 28 feb. 2015

@author: Maurits
'''
import getitembyname
import items
from constants import *

class Potion(items.Item):
    imagename="potion.png"
    name="potion"
    pname="potions"
    weight=4
    def __init__(self, position, world, cage):
        items.Item.__init__(self, position, cage.lookup(self.imagename), cage, world, self.name, self.pname)
    def use(self):
        self.owner.say("you drink the "+self.name)
        self.owner.say("nothing happens")
        self.owner.removebyidentity(self)
        return True
    def eat(self):
        return self.use()

        return True
    #def aircollision(self):
    #    self.owner.

@getitembyname.ri("speed potion", 5, -3, 12, (ITM_ITEM, ITM_POTION))
class SpeedPotion(Potion):
    name="speed potion"
    pname="speed potions"
    imagename="potion_green.png"
    def use(self):
        self.owner.say("you drink the "+self.name)
        
        self.owner.say("the world comes more sharply into focus")
        self.owner.flag(FLAG_FAST)
        self.world.spawnItem(items.EventScheduler(self.world, 8, self.owner.unflag,  FLAG_FAST))
        self.world.spawnItem(items.EventScheduler(self.world, 8, self.owner.say, "the world speeds up around you"))
        self.owner.removebyidentity(self)
        
    
@getitembyname.ri("healing potion", 1, -3, 12,(ITM_ITEM, ITM_POTION))
        
class HealingPotion(Potion):
    name="health potion"
    pname="heath potions"
    imagename="potion.png"
    def use(self):
        self.owner.say("you drink the "+self.name)
        
        self.owner.say("you feel much better")
        self.owner.body.health+=(self.owner.body.maxhealth-self.owner.body.health)/2
        self.owner.removebyidentity(self)