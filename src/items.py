'''
Created on 1 jan. 2015

@author: Maurits
'''
import generator
from constants import *


class StaticObject(object):
    def __init__(self,position,image, cage=None,world=None, speed=0, recieveevent=False):
        self.position=list(position)
        #print "-----------------------------------------------"
        #print position
        #print position[1]-position[0]
        self.image=image
        self.cage=cage
        #if not self.image:
        #    print "didn't get a image"
        
    def draw(self,screen,position):
        if self.image and self.image.get_height()==128:
            screen.blit(self.image,(position[0],position[1]-32))
        elif self.image:
            
            screen.blit(self.image,(position[0],position[1]))
            
    def receiveEvent(self, event):
        pass
    
    def __repr__(self):
        return ("<"+type(self).__name__+" at "+str(self.position)+">")
#UTILITY FUNCTION
alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
class EventScheduler():
    def __init__(self, world, time, event, *args):
        self.world=world
        self.speed=1
        self.action_points=-time
        self.event=event
        self.args=args
    def gameTurn(self):
        self.event(*self.args)
        self.world.objects.remove(self)
        return 100
def getfirstemptyletter(dictionary):
    for i in alphabet:
        if i not in dictionary:
            return i
            break
    return None
class Command(object):
    def __init__(self, typ, data=None, **kwargs):
        self.typ=typ
        if data:
            self.data=data
        else:
            self.data=kwargs
class Item(StaticObject):
    '''
    A base class that all items inherit
    '''
    name="invalid item"
    pname="invalid items"
    image=None
    weight=0
    range=1
    speed=100

    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None): #Assumed to be a class level attribute if not passed
        '''
        crates a item object
        '''
        StaticObject.__init__(self, position, image, cage, world, 0, False)
        self.owner=None
        
        self.isflying=False
        self.direction=(0,0)
        #self.action_points=0
        
        if name:
            self.name=name
        if pname:
            self.pname=pname
        elif self.pname=="invalid items":
            self.pname=self.name+"s"
        if image:
            self.image=image
        if weight:
            self.weight=weight
        if world:
            self.world=world
    def use(self):
        self.owner.say("You don't know how to use "+self.name)
    def say(self, *args):
        return self.owner.say(*args)
    
    def __eq__(self, other):
        try:
            if self.name==other.name and self.position==other.position:
                return True
            else:
                return False
        except AttributeError:
            return False
    def getWeight(self):
        return self.weight;
    def throw(self, owner, direction):
        self.direction=direction
        self.isflying=True
        self.turnsinair=0
        self.thrower=owner
        self.action_points=10*self.range
        return 50+12*self.weight
    
    def throwEvent(self, event):
        if event.type==KEYDOWN:
            if event.key==K_DOWN:
                return "normal", Command("throw",item=self,direction=(-1,0))
            elif event.key==K_UP:
                return "normal", Command("throw",item=self,direction=(1,0))
            elif event.key==K_LEFT:
                return "normal", Command("throw",item=self,direction=(0,-1))
            elif event.key==K_RIGHT:
                return "normal", Command("throw",item=self, direction=(0,1))
        return self.throwEvent, None
    
    def gameTurn(self):
        if self.isflying:
            newposition=self.position[0]+self.direction[0],self.position[1]+self.direction[1]
            if self.world.grid.hasindex(newposition) and (not self.world.grid[newposition] in WALLS):
                self.position=newposition
            else:
	        del self.action_points
                self.isflying=False
                return 10
            for i in self.world.objects:
                if hasattr(i, "position") and i.position[0]==self.position[0] and i.position[1]==self.position[1]:
                    self.aircollision(i)
                    break
                    
            
            
            self.turnsinair+=1
            if self.turnsinair >= self.range:
                self.isflying=False
            return 10
            
        return  100
    def aircollision(self, other):
        if not isinstance(other, Item):
            self.isflying=False
            self.position=tuple(self.position[i]-self.speed[i] for i in xrange(2))
class Potion(Item):
    imagename="potion.png"
    name="potion"
    pname="potions"
    weight=4
    def __init__(self, position, world, cage):
        Item.__init__(self, position, cage.lookup(self.imagename), cage, world, self.name, self.pname)
    def use(self):
        self.owner.say("you drink the "+self.name)
        self.owner.say("nothing happens")
        self.owner.removebyidentity(self)
        return True
    def eat(self):
        return self.use()

        return True
class Armor(Item):
    def __init__(self, position, image, cage, world, name, pname=None, weight=0, slot=None, defence=None):
        Item.__init__(self, position, image, cage, world, name, pname, weight)
        if slot:
            self.slot=slot
        if defence:
            self.defence=defence
    __isarmor__=True
    defence=(1,)*8
    slot=""

class Food(Item):
    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, nutrition=0):
        Item.__init__(self, position, image, cage, world, name, pname, weight)
        self.nutrition=nutrition
    def eat(self):
        return "you eat the "+self.name
class Key(Item):
    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)
    pmessage="you unlock the door"
    nmessage="there is no locked door here"
    replace_dict=generator.door_pair_lock
    def use(self):
        for i in generator.getadjacent(self.owner.position,self.world.grid_size,0,0,1):
            if self.world.grid[i] in self.replace_dict:
                self.world.grid[i]=self.replace_dict[self.world.grid[i]]
                self.owner.say(self.pmessage)
                #if False:
                #    if True:
                #        if True and False and True is not False:
                #            self.owner.say("the minion is dead allready")
                #        else:
                #            self.minion.kill() #Kill self.minion, if you have a minion, else, don't kill it.
                #else:
                #    if False:
                #        if False or True is not False:
                #             self.owner.say("that is not your minion")
                #        elif False or not True:
                #             self.owner.say("that minion is no longer loyal to you"
                #        else:
                #             self.owner.say("you don't have a minion")
                return True
        self.owner.say(self.nmessage)
        return False
        
