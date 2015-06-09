'''
Created on 25 apr. 2015

@author: Maurits
'''
import items
import getitembyname
from constants import *
import monster_body

class FakeBodyToRepresentFlyingObject(monster_body.CombatOnlyBody):
    max_attack_height_ratio=1.1
    def __init__(self, size=100, target=None, mind=None, name=None, skill_ratio=1):
        self.size=size
        self.target=target
        self.mind=mind
        self.name=name
        self.skill_ratio=skill_ratio
    def getstat(self, stat):
        return self.mind.getstat(stat)*self.skill_ratio

class Weapon(items.Item):
    __isweapon__=True
    damage=(0,0,0,0,0,0,0,0)
    twohanded=False
    

    speed=100
    
    range=8
    
    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, damage=None):
        items.Item.__init__(self, position, image, cage, world, name, pname, weight)
        if damage:
            self.damage=damage
    
    def aircollision(self, other):
        if hasattr(other, "body"):
            FakeBodyToRepresentFlyingObject(100,self.thrower.body.target,self.thrower,self.name,0.5).attack(other,self)



@getitembyname.ri("short sword",1,0,99,(ITM_ITEM, ITM_WEAPON))
def short_sword(position, world, cage):
    return Weapon(position,cage.lookup("shortsword.png"),cage, world, "sword","swords",5,1)
@getitembyname.ri("dagger",5,0,99,(ITM_ITEM, ITM_WEAPON))
def dagger(position, world, cage):
    return Weapon(position,cage.lookup("dagger.png"),cage, world, "dagger","daggers",3,0.5)

    