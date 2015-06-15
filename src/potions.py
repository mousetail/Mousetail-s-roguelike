'''
Created on 28 feb. 2015

\image html "Drink potion.png"
@author: Maurits
also, just skil it
'''
import getitembyname
import items
from constants import *

class Potion(items.Item):
    """
    The way this works:
    \image html "Drink potion.png"
    I don't really get why this isn't showing up
    """
    imagename="potion.png"
    name="potion"
    pname="potions"
    weight=4
    def __init__(self, position, world, cage):
        """Requires no special arguments, and is directly compatible with the generatior"""
        items.Item.__init__(self, position, cage.lookup(self.imagename), cage, world, self.name, self.pname)
    
    def use(self):
        """Don't override, for different behavior, override
        potion effect, potion_message and alt potion message
        
        this function calls potion_effect(1),
        potion_message(1) and then removes the potion from it's owners inventory
        
        \image html "Drink potion.png"
        """
        self.owner.say("you drink the "+self.name)
        self.potion_effect(self.owner,1)
        self.potion_message(self.owner,1)
        self.owner.removebyidentity(self)
        return True
    
        
    def eat(self):
        """enables the same effect to happen when attempting to eat a potion"""
        return self.use()

        return True
    
    def potion_effect(self, obj, lessen=1.0):
        """Apply the effect on obj,
        lessen is usually 1, but if the effect is numerical
        eg. a health potion, you should multiply the amount of health
        increased by lessen. For more binary values, you can check if
        lessen is within a range, and do something extra or less"""
        pass
    
    def potion_message(self, obj, lessen=1.0):
        """message upon drinking the potion,
        should use obj.say
        with a discription of what happens
        """
        obj.say("nothing happens")
    def aircollision(self, other):
        """Don't override, calls apropriate functions when the potion hits something in the air"""
        self.potion_effect(other,1)
    #def alt_potion_message(self, obj):
    #    """called when"""
@getitembyname.ri("speed potion", 5, -3, 12, (ITM_ITEM, ITM_POTION))
class SpeedPotion(Potion):
    name="speed potion"
    pname="speed potions"
    imagename="potion_green.png"
    def potion_message(self, obj, lessen=1.0):
        
        obj.say("the world comes more sharply into focus")
    def potion_effect(self, obj, lessen=1.0):
        obj.flag(FLAG_FAST)
        self.world.spawnItem(items.EventScheduler(self.world, 8, obj.unflag,  FLAG_FAST))
        self.world.spawnItem(items.EventScheduler(self.world, 8, obj.say, "the world speeds up around you"))
        
    
@getitembyname.ri("healing potion", 1, -3, 12,(ITM_ITEM, ITM_POTION))
        
class HealingPotion(Potion):
    name="health potion"
    pname="heath potions"
    imagename="potion.png"
    def potion_message(self, obj, lessen=1.0):
        
        obj.say("you feel much better")
    def potion_effect(self, obj, lessen=1.0):
        obj.body.health+=((obj.body.maxhealth-obj.body.health)/2)*lessen