'''
Created on 1 jan. 2015

@author: Maurits
'''
import generator
import itemGui
from constants import *


class StaticObject(object):
    """A object that draws itself bu dous nothing else"""

    def __init__(self, position, image, cage=None, world=None, speed=0, recieveevent=False):
        self.position = list(position)
        assert len(self.position) == 3, "position seems to be missing a dungeon level value [2]"
        # print "-----------------------------------------------"
        # print position
        # print position[1]-position[0]
        self.image = image
        self.cage = cage
        # if not self.image:
        #    print "didn't get a image"

    def draw(self, screen, position):
        """draws itself on the screen, at position"""
        if self.image and self.image.get_height() == 128:
            screen.blit(self.image.toSurf(), (position[0], position[1] - 32))
        elif self.image:
            screen.blit(self.image.toSurf(), (position[0], position[1]))

    def receiveEvent(self, event):
        pass

    def __repr__(self):
        return ("<" + type(self).__name__ + " at " + str(self.position) + ">")

    def markdead(self):
        self.dead = True


# UTILITY FUNCTION
alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class EventScheduler():
    """calls "event" after time
    should be added to the worlds object list using spawnItem()
    to work properly"""

    def __init__(self, world, time, event, *args):
        self.world = world
        self.speed = 1
        self.action_points = -time
        self.event = event
        self.args = args

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
        self.typ = typ
        if data:
            assert isinstance(data, dict)
            self.data = data
        else:
            self.data = kwargs

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]


class Item(StaticObject):
    '''
    A base class that all items inherit, all a item will do is being able to be picked up, dropped, thrown and weited.
    '''

    def __init__(self, position, image=None, cage=None, world=None, name=None, pname=None, weight=None, fakename=None,
                 fakepname=None, mxrange=1, **kwargs):
        '''
        crates a item object
        '''
        StaticObject.__init__(self, position, image, cage, world, 0, False)
        self.owner = None
        self.guiInterface = itemGui.ItemGui()
        self.isflying = False
        self.direction = (0, 0)
        # self.action_points=0
        self.range = mxrange
        # print "name: "+repr(name)+"range: "+repr(self.range)+" type: "+repr(type(self.range))
        if name:
            self.name = name
        if pname:
            self.pname = pname
        else:
            print pname
            self.pname = self.name + "s"
        if image:
            self.image = image
        if weight:
            self.weight = weight
        if world:
            self.world = world
        self.fakename = fakename
        self.fakepname = fakepname

    def getGui(self):
        return self.guiInterface

    def move(self, dest):
        if self.owner:
            self.owner.removeByIdentity(self)
        if isinstance(dest, list) or isinstance(dest, tuple):
            self.position = tuple(dest)
            self.world.spawnItem(self)
            self.owner = self.world
        else:
            self.position = (0, 0)
            dest.addToInventory(self)
            self.owner = dest

    def checkMove(self, dest):
        if self.owner:
            st = self.owner.checkRemoveByIdentity(self)
            if st:
                return st
        if isinstance(dest, list) or isinstance(dest, tuple):
            return self.world.checkAddToInventory(self)
        else:
            return dest.checkAdd(self)

    def checkUse(self, **kwargs):
        return "You don't know how to use", self

    def use(self, **kwargs):
        """called when trying to use "A" on a item"""
        raise ValueError("you didn't call check")

    def say(self, *args, **kwargs):
        """passes on the say event to the owner"""
        if hasattr(self.owner, "say"):
            return self.owner.say(*args, **kwargs)

    def __eq__(self, other):
        """check if the names and positions are equal
        used for stacking, so override if you have items with the same
        name that don't stack"""
        try:
            if self.name == other.name and self.position == other.position:
                return True
            else:
                return False
        except AttributeError:
            return False

    def getWeight(self):
        """return the weight, with any modifiers"""
        return self.weight

    def throw(self, owner, direction):
        """called when the player tries to throw the item, default range is one tile, so don't bother overriding if you don't want youre item to fly,
        you can just set the range to 0"""
        self.direction = direction
        self.isflying = True
        self.turnsinair = 0
        self.thrower = owner
        self.action_points = 10 * self.range
        # print repr(self.action_points)+" range: "+repr(self.range)
        return 50 + 12 * self.weight

    def throwEvent(self, event):
        """don't override! internal method used to thow the item
        (unless, you want the throw command to work differently with this item eg. it dousn't require a direction)
        be carefull though"""
        if event.type == KEYDOWN:
            if event.key == K_DOWN:
                return "normal", Command("throw", item=self, direction=(-1, 0))
            elif event.key == K_UP:
                return "normal", Command("throw", item=self, direction=(1, 0))
            elif event.key == K_LEFT:
                return "normal", Command("throw", item=self, direction=(0, -1))
            elif event.key == K_RIGHT:
                return "normal", Command("throw", item=self, direction=(0, 1))
        return self.throwEvent, None

    def gameTurn(self):
        """used for throwing, usually not called
        this can be overriden for costom throwing behavior, eg bumerang
        pretty safely"""
        if self.isflying:
            newposition = self.position[0] + self.direction[0], self.position[1] + self.direction[1]
            if self.world.grid.hasindex(newposition) and (not self.world.grid[newposition] in WALLS):
                self.position = newposition
            else:
                self.land()
            for i in self.world.objects:
                if (i is not self and hasattr(i, "position") and i.position[0] == self.position[0] and i.position[1] ==
                    self.position[1]):
                    # print i
                    # print self
                    self.aircollision(i)
                    break

            self.turnsinair += 1
            if self.turnsinair >= self.range:
                self.land()
            return 10

        return 100

    def aircollision(self, other):
        if not isinstance(other, Item):
            self.isflying = False
            self.position = tuple(self.position[i] - self.direction[i] for i in xrange(2))

    def land(self):
        del self.action_points
        self.isflying = False
        return 10

    def getName(self, p=False):
        if p:
            return self.pname
        else:
            return self.name

    def getFakeName(self, p=False):
        if p:
            return self.fakepname
        else:
            return self.fakename


class BasicContainer(StaticObject):
    def __init__(self):
        self.inventory = {}

    def checkRemove(self, letter, removeItem=True, ammount=0):
        if len(letter) == 0:
            return "no text entered"
        elif letter[0] not in self.inventory:
            return "You don't have enything in slot " + letter
        elif len(letter) > 1:
            itm = self.inventory[letter[0]][0]
            if (not hasattr(itm, "removeByLetter")):
                return itm, " is not a container"
            else:
                return itm.checkRemove(letter[1:], removeItem, ammount)
        elif len(self.inventory[letter]) < ammount:
            return "You don't have " + str(ammount), self.inventory[letter], "s"

    def removeByLetter(self, letter, removeItem=True, ammount=0):
        """takes a inventory item out of the inventory, then returns a list, containting amount of the specified item
        if there are less then amount items in a slot, only the amount available is returned"""
        if letter[0] in self.inventory:
            if len(letter) > 1:
                itm = self.inventory[letter[0]][0]
                if hasattr(itm, "removeByLetter"):
                    return itm.removeByLetter(letter[1:], ammount)
            elif ammount == 0:
                itm = self.inventory[letter]
                if removeItem:
                    del self.inventory[letter]
                self.update_storage_fullness()

                self.update_storage_fullness()
                return itm
            else:
                itm = self.inventory[letter][:ammount]
                if removeItem:
                    del self.inventory[letter][:ammount]
                    if len(self.inventory[letter]) == 0:
                        del self.inventory[letter]
                return itm
                self.update_storage_fullness()
                self.update_storage_fullness()

    def removeByIdentity(self, itm):
        """removes a item from the invectory using "is" operator,
        usefull for having items remove themselves"""

        assert isinstance(itm, Item)

        for i in self.inventory:
            for j in range(len(self.inventory[i])):
                if self.inventory[i][j] is itm:
                    del self.inventory[i][j]
                    if len(self.inventory[i]) == 0:
                        del self.inventory[i]
                    self.update_storage_fullness()
                    self.invDirty = True
                    return j
        return False

    def checkRemoveByIdentity(self, itm):
        for i in self.inventory.values():
            if itm in i:
                return None
        return "YOu don't have the ", itm

    def checkAdd(self, itm):
        return None

    def addToInventory(self, itm):
        """adds a item to the players inventory, correctly stacking similar items,
        and calculating the weight"""
        self.invDirty = True
        if isinstance(itm, list) or isinstance(itm, tuple):
            for i in itm:
                self.addToInventory(i)
        else:

            assert isinstance(itm, Item)
            itm.position = (0, 0)  # So they are equal in the inventory but not in the map

            if self.checkAdd(itm):
                return False

            if len(self.inventory) > 0:
                for i in self.inventory:
                    if self.inventory[i][0] == itm:
                        self.inventory[i].append(itm)
                        itm.owner = self
                        self.update_storage_fullness()
                        return True
                nextletter = getfirstemptyletter(self.inventory)
            else:
                nextletter = alphabet[0]
            self.inventory[nextletter] = [itm]
            itm.owner = self
            return True
        return False

    def iterInventory(self):
        """a iterator that iterates over the inventory, returning letter, item on each next"""
        for letter in self.inventory:
            for item in self.inventory[letter]:
                yield letter, item

    def update_storage_fullness(self):
        pass

    def __iter__(self):
        return self.inventory.iteritems()


class Key(Item):
    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)

    pmessage = "you unlock the door"
    nmessage = "there is no locked door here"
    replace_dict = generator.door_pair_lock

    def use(self):
        for i in generator.getadjacent(self.owner.position, self.world.grid_size, 0, 0, 1):
            if self.world.grid[i] in self.replace_dict:
                self.world.grid[i] = self.replace_dict[self.world.grid[i]]
                self.owner.say(self.pmessage)
                self.owner.identify(self)
                # if False:
                #    if True:
                #        if True and False and True is not False:
                #            self.owner.say("the minion is dead allready")
                #        else:
                #            self.minion.kill() #Kill self.minion, if you have a minion, else, don't kill it.
                # else:
                #    if False:
                #        if False or True is not False:
                #             self.owner.say("that is not your minion")
                #        elif False or not True:
                #             self.owner.say("that minion is no longer loyal to you"
                #        else:
                #             self.owner.say("you don't have a minion")
                return True
        self.owner.say(self.nmessage)
        self.owner.identify(self)
        return False
