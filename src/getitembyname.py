'''
Created on 5 jan. 2015

@author: Maurits
'''
import items, player_input, monster_body
import random
from constants import *

class ItemStore:
    def __init__(self):
        
        self.items=[]
    def random_item(self,dungeon_level,tags=None):
        frequency=random.choice((1,5,5,5,5,5))
        tmplist=[]
        for i in self.items:
            if not (i[1]<=dungeon_level<=i[2]):
                #print "REASON: LEV",i, dungeon_level
                continue
            if not (i[0]==frequency):
                continue
            if tags:
                #print tags
                working=True
                for j in tags:
                    if j not in i[4]:
                        #print "MISSING TAG ",j
                        working=False
                        break
                if not working:
                    continue
            tmplist.append(i)
        #print frequency, tags
        try:
            return random.choice(tmplist)
        except IndexError:
            raise RandomError("Failed to find something for dungeon level ",dungeon_level, " tags ",tags, "frequency",frequency)
    def register_item(self, name, frequency, minlevel, maxlevel, tags=None):
        if not isinstance(tags, tuple):
            tags=(tags,)
        def register_internal(function):
                
            self.items.append((frequency,minlevel,maxlevel,name,tags, function))
            return function
        return register_internal
    def fastrandommonster(self, position, world, cage, dungeon_level=1):
        c=self.random_item(dungeon_level)
        return c[5](position, world, cage)
    def fastrandomitem(self, position, world, cage, dungeon_level=1, tags=None):
        c=self.random_item(dungeon_level, tags)
        return c[5](position, world, cage)
        #print "generated"+str(c[3])
    def fast_register_monster(self, name, frequency, minlevel, maxlevel, tags=None, starting_inventory=[]):
        if not tags:
            tags=(0,)
        else:
            tags+=(0,)
        def defregint(cls):
            @self.register_item(name, frequency, minlevel, maxlevel, tags)
            def defaultregistermonster(position, world, cage):
                return player_input.MonsterObject(position, cls, cage, world, cls.speed, name)
            return cls
        return defregint
    def getitembyname(self, name):
        for i in self.items:
            if i[3]==name:
                return i
    def fastitembyname(self, name,position,world, cage):
        itm=self.getitembyname(name)
        if itm:
            return self.getitembyname(name)[5](position,world,cage)
itemRandomizer=ItemStore()
ri=itemRandomizer.register_item
rm=itemRandomizer.register_item
#@ri("healing potion",5,0,99)
#def healing_potion(position, world, cage):
#    return items.HealingPotion(position,cage.lookup("potion.png"), cage, world, "red potion", "red potions", 2)
@ri("plate mail",5,0,99, (ITM_ITEM, ITM_ARMOR))
def breastplate(position, world, cage):
    return items.Armor(position,cage.lookup('armor.png'), cage, world, "plate mail", "plate mail",15,"body",(0,9,1,1,1,1,1,1,1,1))
@ri("cotton pants",1,0,99,(ITM_ITEM, ITM_ARMOR))
def pants(position, world, cage):
    return items.Armor(position,cage.lookup("pants.png"), cage, world, "pants","pants",5,"legs",(0.5,1,1,1,1,1,1,1,1))
@ri("meat",0,0,0,(ITM_ITEM, ITM_FOOD))
def meat(position, world, cage):
    return items.Food(position,cage.lookup("meat.png"),cage, world, "meat", "meat",4,400)
@ri("time book",0,0,0,(ITM_ITEM, ITM_FOOD)) #not generated
def time_book(position, world, cage):
    return items.Item(position,cage.lookup("book time.png"),cage, world, "book", "books")
@ri("iron helmet",0,0,0,(ITM_ITEM,ITM_ARMOR))
def iron_helmet(position, world, cage):
    return items.Armor(position,cage.lookup("ironHelmet.png"), world, cage, "helmet", "helmets", 5,"head", (0.9,1,1,1,1,1,1,1))

@ri("banana",5,0,99,(ITM_ITEM, ITM_FOOD))
def banana(position, world, cage):
    return items.Food(position,cage.lookup("banana.png"),cage, world, "banana", "bananas",1,100)
@ri("key",0,0,0,(ITM_ITEM, ITM_UTIL))
def key(position, world, cage):
    return items.Key(position, cage.lookup("twisted_key.png"),cage, world, "twisted key", "twisted keys")
#-------------------------------------------------------------------------------------#
#MONSTERS                                                                             #            
#                             MONSTERS                                                #    
#                                                                                     #    
#-------------------------------------------------------------------------------------#




@rm("lizard",5,0,15,ITM_MONSTER)
def lizard(position, world, cage):
    return player_input.MonsterObject(position,monster_body.lizard,cage,world)
