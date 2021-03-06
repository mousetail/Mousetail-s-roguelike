'''
Created on 25 apr. 2015

@author: Maurits
'''
import items
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
    def getname(self):
        return self.name

class Weapon(items.Item):
    __isweapon__=True
    damage=(0,0,0,0,0,0,0,0)
    twohanded=False
    

    speed=100
    
    range=8
    
    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, fake_name=None, fake_pname=None, range=1, damage=None, **kwargs):
        items.Item.__init__(self, position, image, cage, world, name, pname, weight, fake_name, fake_pname, range, **kwargs)
        if damage:
            self.damage=damage
    
    def aircollision(self, other):
        if hasattr(other, "body"):
            FakeBodyToRepresentFlyingObject(100,self.thrower.body.target,self.thrower,self.name,0.5).attack(other,self,False)