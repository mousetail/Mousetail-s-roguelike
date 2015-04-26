'''
Created on 25 apr. 2015

@author: Maurits
'''
import items
import getitembyname
from constants import *

class Weapon(items.Item):
    __isweapon__=True
    damage=(0,0,0,0,0,0,0,0)
    twohanded=False
    
    
    speed=800
    
    range=8
    
    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, damage=None):
        items.Item.__init__(self, position, image, cage, world, name, pname, weight)
        if damage:
            self.damage=damage
        
        self.isflying=False
        self.direction=(0,0)
    
    def throw(self, direction):
        assert self in self.world.objects
        self.direction=direction
        self.isflying=True
        self.turnsinair=0
    
    def throwEvent(self, event):
        if event.type==KEYDOWN:
            if event.key==K_DOWN:
                return "normal", items.Command("throw",item=self,direction=(-1,0))
            elif event.key==K_UP:
                return "normal", items.Command("throw",item=self,direction=(1,0))
            elif event.key==K_LEFT:
                return "normal", items.Command("throw",item=self,direction=(0,-1))
            elif event.key==K_RIGHT:
                return "normal", items.Command("throw",item=self, direction=(0,1))
        return self.throwEvent, None
    
    def gameTurn(self):
        if self.isflying:
            newposition=self.position[0]+self.direction[0],self.position[1]+self.direction[1]
            if self.world.grid.hasindex(newposition) and (not self.world.grid[newposition] in WALLS):
                self.isflying=False
                return 100
            else:
                self.position=newposition
            
            
            self.turnsinair+=1
            if self.turnsinair > self.range:
                self.isflying=False
        return  100


@getitembyname.ri("short sword",1,0,99,(ITM_ITEM, ITM_WEAPON))
def short_sword(position, world, cage):
    return Weapon(position,cage.lookup("shortsword.png"),cage, world, "sword","swords",5,1)
@getitembyname.ri("dagger",5,0,99,(ITM_ITEM, ITM_WEAPON))
def dagger(position, world, cage):
    return Weapon(position,cage.lookup("dagger.png"),cage, world, "dagger","daggers",5,0.5)
    