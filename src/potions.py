'''
Created on 28 feb. 2015

@author: Maurits
'''
import getitembyname
import items
from constants import *

@getitembyname.ri("speed potion", 5, -3, 12, (ITM_ITEM, ITM_POTION))
class SpeedPotion(items.Potion):
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
        
class HealingPotion(items.Potion):
    name="health potion"
    pname="heath potions"
    imagename="potion.png"
    def use(self):
        self.owner.say("you drink the "+self.name)
        
        self.owner.say("you feel much better")
        self.owner.body.health+=(self.owner.body.maxhealth-self.owner.body.health)/2
        self.owner.removebyidentity(self)