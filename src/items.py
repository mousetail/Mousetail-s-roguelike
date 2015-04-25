'''
Created on 1 jan. 2015

@author: Maurits
'''
import player_input
import generator



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
class Item(player_input.StaticObject):
    '''
    A base class that all items inherit
    '''
    name="invalid item"
    pname="invalid items"
    image=None
    weight=0

    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None): #Assumed to be a class level attribute if not passed
        '''
        crates a item object
        '''
        player_input.StaticObject.__init__(self, position, image, cage, world, 0, False)
        self.owner=None
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
class Weapon(Item):
    __isweapon__=True
    damage=(0,0,0,0,0,0,0,0)
    twohanded=False
    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, damage=None):
        Item.__init__(self, position, image, cage, world, name, pname, weight)
        if damage:
            self.damage=damage
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
        
