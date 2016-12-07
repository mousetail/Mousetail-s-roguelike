'''
Created on 28 feb. 2015

\image html "Drink potion.png"
@author: Maurits
also, just skil it
'''

import items
from constants import *
import explosions


class Potion(items.Item):
    """
    The way this works:
    \image html "Drink potion.png"
    I don't really get why this isn't showing up
    """

    def checkUse(self, **kwargs):
        return None

    def use(self, **kwargs):
        """Don't override, for different behavior, override
        potion effect, potion_message and alt potion message
        
        this function calls potion_effect(1),
        potion_message(1) and then removes the potion from it's owners inventory
        
        \image html "Drink potion.png"
        """
        self.potion_effect(self.owner, 1)
        msg = "you drink the ", self, self.potion_message(self.owner, 1)
        # self.owner.identify(self)
        self.owner.removeByIdentity(self)
        return msg

    def eat(self):
        """enables the same effect to happen when attempting to eat a potion"""
        return self.use(), 0

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
        if hasattr(obj, "say"):
            obj.say("nothing happens")

    def aircollision(self, other):
        """Don't override, calls apropriate functions when the potion hits something in the air"""
        self.explode()

    def land(self):
        items.Item.land(self)
        self.explode()

    def explode(self):
        explosions.Explosion.explode(self.world, self.position, self.cage, self.cage.lookup("explosion.png"), 1,
                                     ((self.potion_effect, 0.5), (self.potion_message,), (self.reverse_identify)))
        self.markdead()

    def reverse_identify(self, towhat):
        if hasattr(towhat, "identify"):
            towhat.identify(self)


class SpeedPotion(Potion):
    def potion_message(self, obj, lessen=1.0):
        return "the world comes more sharply into focus"

    def potion_effect(self, obj, lessen=1.0):
        if hasattr(obj, "flag") and hasattr(obj, "unflag"):
            obj.flag(FLAG_FAST)
            self.world.spawnItem(items.EventScheduler(self.world, 8, obj.unflag, FLAG_FAST))
            if hasattr(obj, "say"):
                self.world.spawnItem(items.EventScheduler(self.world, 8, obj.say, "the world speeds up around you"))


class HealingPotion(Potion):
    def potion_message(self, obj, lessen=1.0):
        return "you feel much better"

    def potion_effect(self, obj, lessen=1.0):
        if hasattr(obj, "body") and hasattr(obj.body, "health"):
            if hasattr(obj.body, "maxhealth"):
                obj.body.health += ((obj.body.maxhealth - obj.body.health) / 2) * lessen
            else:
                obj.body.health += 10 * lessen
