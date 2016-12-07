'''
Created on 7 dec. 2014

@author: Maurits
'''
import pygame
import random
import generator
import itertools
from constants import *
import sys
import drops_calculator
import items
import cheats


class FakeList(object):
    def append(self, what):
        pass


class ObjectSpawner(object):
    def __init__(self, world, dlevel, chance=12):
        self.world = world
        self.grid = world.grid
        self.player = world.player
        self.chance = chance
        self.speed = 100
        self.action_points = 0
        self.dlevel = dlevel

    def gameTurn(self):
        if random.randint(0, self.chance * len(self.world.objects) + 2) == 1:
            room = random.choice(self.grid.rooms)
            if (not room.instersects(self.player.position[:2])) and (not room.special):
                position = random.randint(room.bounds[0], room.bounds[0] + room.bounds[2]), random.randint(
                    room.bounds[1], room.bounds[1] + room.bounds[3]), self.dlevel
                self.world.spawnItem(
                    self.world.itemPicker.fastRandomItem(position, self.world, self.world.cage, 0, (ITM_MONSTER,)))
                print "G}you hear some noises"

        return 300


class ArmorContainer(object):
    def __init__(self, armorSlots, weaponSlots):
        self.armor = {i: None for i in itertools.chain(armorSlots, weaponSlots)}
        self.armor_letters = {}
        self.armor_slots = armorSlots
        self.weaponSlots = weaponSlots

    def checkAdd(self, item):
        if not (hasattr(item, "__isweapon__") or hasattr(item, "__isarmor__")):
            return item, "is not a weapon or armor"
        if hasattr(item, "__isweapon__"):
            ready = True
            for i in self.weaponSlots:
                if self.armor[i] is None:
                    ready = False
            if ready:
                return "You don't have a hand free"
        else:
            if item.slot not in self.armor:
                return "You can't wear this type of weapon"
            elif self.armor[item.slot] is not None:
                return "You are allready wearing a ", item.slot

    def addToInventory(self, item):
        slot = ""
        if hasattr(item, "__isweapon__"):
            slot = None
            for i in self.weaponSlots:
                if self.armor[i] is None:
                    slot = i
        elif hasattr(item, "__isarmor__"):
            if not item.slot:
                pass
            elif self.armor[item.slot] is None:
                slot = item.slot
            else:
                slot = None
        if slot:
            letter = items.getfirstemptyletter(self.armor_letters)
            self.armor[slot] = item
            self.armor_letters[letter] = slot
            return True
        raise ValueError("you didn't call check")

    def checkRemove(self, letter, removeItem=True, amount=0):
        if letter not in self.armor_letters:
            return "You are not wearing something in slot " + letter
        elif amount > 1:
            return "You can't remove multiple items at once"

    def removeByLetter(self, letter, removeItem=True, amount=0):
        if letter in self.armor_letters:
            slot = self.armor_letters[letter]
            itm = self.armor[slot]
            if removeItem:
                self.armor[slot] = None
                del self.armor_letters[letter]
            return itm
        return False

    def removeByIdentity(self, item):
        for i in self.armor_letters:
            slot = self.armor_letters[i]
            if self.armor[slot] == item:
                del self.armor[slot]
            #       checkRemoveByIdentity

    def checkRemoveByIdentity(self, item):
        if item not in self.armor.values():
            return "You are not wearing the ", item, "you are wearing ", self.armor.values()

    def getSlot(self, slot):
        return self.armor[slot]

    def iterSlots(self):
        return self.armor.iteritems()

    def __iter__(self):
        for key, value in self.armor_letters.iteritems():
            yield key, (self.armor[value],)


class PlayerInventory(items.BasicContainer):
    pass

class PlayerObject(items.StaticObject):
    '''
    A class that represents a player
    
    functions:
    getstat: get the experience level
    wear(item, saystuff=True): put a item into a armor slot
    addtoinventory(itm): add the item to inventory
    receiveevent: called when receiving a event
    add_xp(xp): excercise a skill
    level_up: increase the players level
    say: send a message to the player, displayed in the right side bar
    kill(message): called if the player dies, don't call unless HP is negative
    update: process events
    removearmorbyletter: get the armor out of its slot
    removebyidentity: remove a object from the inventory
    drop: drop a item to the floor
    AIturn: called when a AI should get a turn
    '''
    name = "Player"

    def getstat(self, stat):
        "get experience level, depending on monster type"
        return self.body.ratios[stat] * self.stats[stat]

    def moveToLevel(self, level, direction):
        self.world.loadLevel(level, direction)
        self.position[2] = level

    def setPosition(self, position):
        self.position[0] = position[0]
        self.position[1] = position[1]

    def __init__(self, position, body, cage, world, advanced_visibility_check=False, startinginv=(), safemode=False):
        """
        note that startinginv is in (prob, ammount, name) format. 
        """
        self.speed = body.speed
        self.dirty = False
        self.world = world
        if not safemode:
            self.visible = generator.Grid(self.world.grid_size, False)
        self.action_points = 0
        self.advanced_visibility_check = advanced_visibility_check
        self.dead = False
        self.actions = [Command("move", {"direction": (1, 0)})] * 2
        self.stats = {"level": 1, "accuracy": 1, "constitution": 1, "strength": 1}
        self.xp = self.stats.copy()

        self.input_mode = "normal"
        self.status_messages = []

        self.body = body
        self.body.mind = self
        self.body.updatemaxweight()
        self.inventory = PlayerInventory()
        self.armor = ArmorContainer(self.body.armor_slots, self.body.weapon_slots)
        self.body.recalculateEverything()

        self.identified_items = []

        self.events = []
        self.fullness = 1000  # BASE 1000
        self.name = self.body.name
        if not safemode:
            items.StaticObject.__init__(self, position, cage.getProxy(self.body.imagename, True), cage, world.grid,
                                        self.body.speed, True)
        else:
            self.position = position
        invitems = drops_calculator.calculateDrops(self.world, self.cage, startinginv, self.position[:], False)
        for i in invitems:
            self.inventory.addToInventory(i)
        self.statsDirty = True
        self.invDirty = True

    def clearEquipment(self, saystuff=False):
        for i in self.equipment_letters.keys():
            self.removearmorbyletter(i, True, saystuff, True)
        self.invDirty = True

    def welcomeMessage(self):
        """give a help message"""
        self.say("B}Welcome to Mousetail's roguelike")
        self.say("B}Use the arrow keys to walk arround")
        self.say("B} ',' to pick up items")
        self.say("B}'w' to wield or wear")
        self.say("B}'e' to eat, 'a' to apply")
        self.say("B}'h' to repeat this message")
        self.say("B}thanks for playing!")
        self.say()

    def eat(self, itm, saystuff=False, dostuff=True):
        """
        tries to eat the item,
        see wear for documentation of the arguments
        """
        if hasattr(itm, "eat"):
            if hasattr(itm, "nutrition"):
                msg, nut = itm.eat()
                if saystuff:
                    self.say(msg)
                if dostuff:
                    self.fullness += nut
                    self.add_xp("strength", int((itm.nutrition / 100) ** 0.5))
                self.update_nutrition(saystuff)
                return True
            else:
                return itm.eat()
        else:
            if saystuff:
                self.say("you try to bite the " + itm.name + " but it's to solid, you almost break a tooth!")
            self.update_nutrition(saystuff)
            return False

    def update_nutrition(self, saystuff=False):
        """should be called when something changes the fullness,
        updates the status messages HUNGRY, VERY HUNGRY, FULL and VERY FULL"""
        oldmsg = []
        self.statsDirty = True
        for i in [FLAG_HUNGRY_2, FLAG_HUNGRY, FLAG_FULL, FLAG_FULL_2]:
            if i in self.status_messages:
                self.unflag(i)
                oldmsg.append(i)
        if self.fullness > 1400:
            self.flag(FLAG_FULL_2)
            if saystuff and FLAG_FULL_2 not in oldmsg:
                self.say("your belly feels like its bursting!")
        elif self.fullness > 1000:
            self.flag(FLAG_FULL)
            if saystuff and FLAG_FULL not in oldmsg:
                self.say("you feel comfortabally full")
        elif self.fullness > 0:
            pass
        elif self.fullness > -400:

            self.flag(FLAG_HUNGRY)
            if saystuff and FLAG_HUNGRY not in oldmsg:
                self.say("you are starting to feel hungry")
        else:
            self.flag(FLAG_HUNGRY_2)
            if saystuff and FLAG_HUNGRY_2 not in oldmsg:
                self.say("all you can think about is food now")

    def getspeed(self):
        """checks if any status messages affect the speed, and checks the base speed,
        return the value"""
        s = self.speed
        if FLAG_BURDENED in self.status_messages:
            s -= 25
        if FLAG_FULL_2 in self.status_messages:
            s -= 25
        elif FLAG_FULL in self.status_messages:
            s += 10
        if FLAG_HUNGRY in self.status_messages:
            s -= 25
        elif FLAG_HUNGRY_2 in self.status_messages:
            s -= 35
        if FLAG_FAST in self.status_messages:
            s *= 2
        elif FLAG_FAST_2 in self.status_messages:
            s *= 3
        if s < 1:
            s = 1
        return s

    def update_storage_fullness(self):
        """If weapons or inventory or annything changed, 
        this function will update burdened flags"""
        s = sum(i[1].getWeight() for i in self.iterInventory())
        s += sum(i[2].getWeight() for i in self.iterArmor())
        if s <= self.body.maxweight:
            if FLAG_BURDENED in self.status_messages:
                self.unflag(FLAG_BURDENED)
        else:
            if FLAG_BURDENED not in self.status_messages:
                self.flag(FLAG_BURDENED)

    def receiveEvent(self, event):
        """called when a even is forwarded fromt the world class"""
        self.events.append(event)

    def add_xp(self, skill, ammount):
        """adds the specified ammount of xp to a skill of choice"""
        self.xp[skill] += ammount
        while self.xp[skill] > (5 ** self.stats[skill]):
            self.level_up(skill, True)

    def level_up(self, skill, changexp=False):
        """called by add_xp, gives appropriate messages after a level increase"""
        self.statsDirty = True
        if changexp:
            self.xp[skill] -= 5 ** self.stats[skill]
            self.stats[skill] += 1
        if skill == "level":
            self.say("You sudenly feel very confident")
        elif skill == "accuracy":
            if self.stats["accuracy"] < 10:
                obj = "mountain"
            elif self.stats["accuracy"] < 50:
                obj = "cow"
            else:
                obj = "needle"
            self.say(
                "B}You feel like you could hit a " + obj + " at " + str(10 * self.stats["accuracy"]) + "M distance")
        elif skill == "constitution":
            self.body.updatemaxhealth()
            self.say("B}You feel healthy")
        elif skill == "strength":
            self.body.updatemaxweight()
            self.say("B}You feel strong")

    def say(self, *what, **kwargs):  # I have to use kwargs because I cant put newline after regular args
        """send a message to the player, to be displayed in the log
        """
        if len(what) == 1 and isinstance(what[0], tuple):
            for i in what[0]:
                self.say(i)
            return
        self.dirty = True
        text = ""
        for i in what:
            if hasattr(i, "getName") and hasattr(i, "getFakeName"):
                text += self.getitemname(i)
            else:
                text += str(i)
        if "newline" not in kwargs or kwargs["newline"]:
            sys.stdout.write(text + "\n")
        else:
            sys.stdout.write(text + "")

    def kill(self, message):
        """called when the player dies"""
        self.say("1}you die")
        self.say("1}you where killed by a " + message)
        self.body.drop()
        self.dead = True

    def update(self):
        """handles events"""
        if self.events:
            self.old_postion = self.position[:]
            for event in self.events:
                if not self.input_mode or self.input_mode == "normal":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.actions.append(Command("move", {"direction": (1, 0)}))
                        elif event.key == pygame.K_DOWN:
                            self.actions.append(Command("move", {"direction": (-1, 0)}))
                        elif event.key == pygame.K_LEFT:
                            self.actions.append(Command("move", {"direction": (0, -1)}))
                        elif event.key == pygame.K_RIGHT:
                            self.actions.append(Command("move", {"direction": (0, 1)}))
                        elif event.key == pygame.K_h:
                            self.welcomeMessage()
                        elif event.key == pygame.K_PERIOD:
                            self.actions.append(Command("wait"))
                        elif event.key == pygame.K_d:
                            self.startSimpleAction("drop", "What would you like to drop?")
                        elif event.key == pygame.K_w:
                            self.startSimpleAction("wear", "What would you like to wear/wield?")
                        elif event.key == pygame.K_r:
                            self.startSimpleAction("remove", "What would you like to take of?", USER_TYPE_ARMOR)
                        elif event.key == pygame.K_a:
                            self.startSimpleAction("use", "What would you like to apply/use?", func=self.useDelegate)
                        elif event.key == pygame.K_e:
                            self.startSimpleAction("eat", "what would you like to eat?")
                        elif event.key == pygame.K_p:
                            self.startSimpleAction("put", "what would you like to put into something?",
                                                   func=self.putInDelegate)
                        elif event.key == pygame.K_o:
                            self.actions.append(Command("open"))
                        elif event.unicode == "c":
                            self.actions.append(Command("close"))
                        elif event.key == pygame.K_COMMA:
                            self.actions.append(Command("pickup"))
                        elif event.key == pygame.K_t:
                            self.input_mode = "throw1"
                            self.say("what would you like to throw?")
                        elif event.unicode == "C":
                            self.startSimpleAction("cheat", "R}enter a cheatcode:",
                                                   USER_TYPE_STRING, key="code",
                                                   func=cheats.CheatHandler(self.world, self).cheatInput)
                elif isinstance(self.input_mode, tuple):
                    if event.type == pygame.KEYDOWN:
                        # input mode is list action, type, key, temp, func
                        action, type, key, temp, func = self.input_mode
                        done = False
                        if type == USER_TYPE_INT:
                            if event.unicode in "1234567890":
                                temp += event.key
                            elif event.key == pygame.K_BACKSPACE:
                                self.say("\b", newline=False)
                                temp = temp[:-1]
                            elif event.key == K_RETURN:
                                action[key] = int(temp)
                                done = True
                        elif type == USER_TYPE_STRING:
                            if len(event.unicode) != 0 and event.unicode not in "\n\b\r\t":
                                self.say(event.unicode, newline=False)
                                temp += event.unicode
                            elif event.key == pygame.K_BACKSPACE:
                                self.say("\b", newline=False)
                                temp = temp[:-1]
                            elif event.key == K_RETURN:
                                action[key] = temp
                                done = True
                        elif type == USER_TYPE_ITEM or type == USER_TYPE_ITEM_STACK:
                            if len(event.unicode) == 1 and event.unicode in items.alphabet:
                                temp += event.unicode
                                if (self.inventory.checkRemove(temp)):
                                    self.say("r} ", newline=False)
                                    self.say(self.inventory.checkRemove(temp))
                                    self.input_mode = "normal"
                                else:
                                    itm = self.inventory.removeByLetter(temp, False)
                                    if not isinstance(itm[0], items.BasicContainer):
                                        if type == USER_TYPE_ITEM:
                                            action[key] = itm[0]
                                        else:
                                            action[key] = itm
                                        done = True
                            elif event.key == pygame.K_BACKSPACE:
                                temp = temp[:-1]
                                self.say("\b", newline=False)
                            elif event.key == pygame.K_RETURN:
                                error = self.inventory.checkRemove(temp)
                                if error:
                                    self.say()
                                    self.say("r} ", newline=False)
                                    self.say(error)
                                    self.input_mode = "normal"
                                else:
                                    itm = self.inventory.removeByLetter(temp)
                                    if type == USER_TYPE_ITEM:
                                        action[key] = itm[0]
                                    else:
                                        action[key] = itm
                                    done = True
                        elif type == USER_TYPE_LETTER:
                            if len(event.unicode) == 1 and event.unicode not in "\n\r\b\t":
                                action[key] = event.unicode
                                done = True
                        elif type == USER_TYPE_ARMOR:
                            if self.armor.checkRemove(event.unicode):
                                self.say(self.armor.checkRemove(event.unicode))
                                self.input_mode = "normal"
                            else:
                                action[key] = self.armor.removeByLetter(event.unicode, False)
                                done = True

                        if done:
                            if func is None:
                                self.actions.append(action)
                                self.input_mode = "normal"
                            else:
                                out = func(action)
                                if out is None:
                                    self.actions.append(action)
                                    self.input_mode = "normal"
                                elif out is False:
                                    self.input_mode = "normal"  # cancel action
                                else:
                                    question, type, key, func = out
                                    self.say(question)
                                    self.input_mode = action, type, key, temp, func
                        elif self.input_mode != "normal":
                            self.input_mode = action, type, key, temp, func
                else:
                    raise ValueError("This method is now invalid: " + str(self.input_mode))
        self.events[:] = []
        old_dirty = self.dirty
        self.dirty = False
        return old_dirty

    def startSimpleAction(self, actionName, question, type=USER_TYPE_ITEM, key="item", func=None):
        self.say(question)
        self.input_mode = Command(actionName), type, key, "", func

    def useDelegate(self, action):
        if hasattr(action["item"], "getUseArgs"):
            return action["item"].getUseArgs()
        else:
            return None

    def putInDelegate(self, action):
        return "what would you like to put " + self.getitemname(action["item"]) + " in?", USER_TYPE_ITEM, "dest", None

    def drop(self, itm, saystuff=True):
        """another internal action function, puts a specified item on the ground
        itm can be a Item object, or a list or tuple of Item objects"""

        itm.move(self.position)

    def AIturn(self):
        """called when the AI has a chance to update"""
        return True

    def gameTurn(self):
        """update function called by the worlds turn time calculator
        this is a mirror function of update() handling the actions the world put here,
        and for AI entities, this function handles the actions they spawned
        use redict input method for costom behaviour"""
        actions = 0
        if self.actions:
            action = self.actions.pop()
            if action.typ == "move":
                old_position = self.position[:]
                actions += 100
                old_position[0] += action.data["direction"][0]
                old_position[1] += action.data["direction"][1]
                for i in self.world.objects:
                    if (hasattr(i, "position") and i is not self and i.position[0] == old_position[0] and
                                i.position[1] == old_position[1]):
                        if isinstance(i, PlayerObject):
                            old_position = self.position[:]
                            self.body.attack(i)
                if self.world.grid.hasindex(self.position) and (not self.world.grid[old_position] in WALLS):
                    if self.world.grid[old_position] in STAIRS:
                        self.moveToLevel(self.position[2] + STAIRS[self.world.grid[old_position]][0],
                                         STAIRS[self.world.grid[old_position]][1])
                    else:
                        self.position[:] = old_position
                        actions -= 1
            elif action.typ == "wait":
                actions += 100
            elif action.typ == "drop":
                if "letter" in action.data:
                    raise ValueError("using letters is outdated")
                elif "item" in action.data:
                    self.drop(action["item"])
                actions += 100
            elif action.typ == "wear":
                if "letter" in action.data:
                    raise ValueError("using letters is outdated")
                elif "item" in action.data:
                    if self.armor.checkAdd(action["item"]):
                        print self.armor.checkAdd(action["item"])
                    else:
                        self.armor.addToInventory(action["item"])
                        self.inventory.removeByIdentity(action["item"])
                        self.say("you wear the ", action["item"])
                        actions += 100
            elif action.typ == "remove":
                if "letter" in action.data:
                    raise ValueError("accessing items by letter is outdated")
                elif "item" in action.data:
                    if self.armor.checkRemoveByIdentity(action["item"]):
                        print self.armor.checkRemoveByIdentity(action["item"])
                    else:
                        self.armor.removeByIdentity(action["item"])
                        self.inventory.addToInventory(action["item"])
                        actions += 100

            elif action.typ == "use":
                if "item" in action.data:
                    itm = action.data["item"]
                    if itm.checkUse(**action.data):
                        self.say(itm.checkUse(**action.data))
                    else:
                        del action.data["item"]
                        self.say(itm.use(**action.data))
                else:
                    raise ValueError("using letters rather than items is outdated")
                actions += 100
            elif action.typ == "eat":
                if "letter" in action.data:
                    raise ValueError("using letters rather than items is outdated")

                elif "item" in action.data:
                    itm = action["item"]
                    if itm:
                        if not self.eat(itm, True):
                            self.inventory.addToInventory(itm)
                actions += 300
            elif action.typ == "open":
                # This one should work without intervention
                wk = False
                for i in generator.getadjacent(self.position, self.world.grid_size, 0, 0, 1):
                    if self.world.grid[i] in generator.door_pair_reverse:
                        self.world.grid[i] = generator.door_pair_reverse[self.world.grid[i]]
                        self.say("you open the door")
                        actions += 100
                        wk = True
                        break
                    elif self.world.grid[i] in generator.door_pair_lock:
                        self.say("that door is locked")
                        wk = True
                if not wk:
                    self.say("There is no door here")
                actions += 100
            elif action.typ == " close":
                wk = False
                for i in generator.getadjacent(self.position, self.world.grid_size, 0, 0, 1):
                    if self.world.grid[i] in generator.door_pairs:
                        self.world.grid[i] = generator.door_pairs[self.world.grid[i]]
                        self.say("you close the door")
                        actions += 100
                        wk = True
                        break
                if not wk:
                    self.say("There is no door here")
                    actions -= 1
            elif action.typ == "pickup":
                f = False
                for i in self.world.objects:
                    if (hasattr(i, "position") and i is not self and i.position[0] == self.position[0]
                        and i.position[1] == self.position[1]):
                        if isinstance(i, items.Item):
                            l = i.checkMove(self.inventory)
                            if l:
                                print l
                            else:
                                i.move(self.inventory)
                                f = True
                                break

                if not f:
                    self.say("there is nothing to pick up!")
                else:
                    actions += 100
            elif action.typ == "throw":

                if "letter" in action.data:
                    raise ValueError("using letters is outdated")
                elif "item" in action.data:
                    itm = action.data["item"]
                    self.drop(itm, False)
                    actions += itm.throw(self, action.data["direction"])
            elif action.typ == "put":
                if action["dest"].addtoinventory(action["item"], True):
                    self.inventory.removeByIdentity(action["item"])
            elif action.typ == "other" or action.typ == "costom":
                actions += action.data["action"](action)

        self.body.update()
        self.fullness -= 1
        if FLAG_BURDENED in self.status_messages:
            self.fullness -= 1
        self.update_nutrition(True)

        return actions

    def iterArmor(self):
        """a iterator that iterates over the equipment, returning letter, slot, item"""
        for letter in self.equipment_letters:
            if self.equipment[self.equipment_letters[letter]]:
                yield letter, self.equipment_letters[letter], self.equipment[self.equipment_letters[letter]]

    def flag(self, flag):
        """adds a flag to the flags"""
        self.status_messages.append(flag)

    def unflag(self, flag):
        """removes a flag"""
        self.statsDirty = True
        if flag in self.status_messages:
            self.status_messages.remove(flag)
        else:
            print >> sys.stderr, "ERROR, FLAG NOT IN STATUS MESSAGES (player_input.PlayerObject.unflag(flag))"

    def getitemname(self, item, p=False):
        if item.name in self.identified_items:
            return item.getName(p)
        else:
            return item.getFakeName(p)

    def identify(self, item):
        self.invDirty = True
        self.identified_items.append(item.name)

    def getLevelSpecificState(self):
        return self.visible

    def setLevelSpecificState(self, state):
        self.visible = state

    def getDefaultLevelSpecificState(self):
        return generator.Grid(self.visible.size, False)

    def getInvDirty(self):
        """Checks if the inventory or equipment for this object needs to be redrawn"""
        if self.invDirty:
            self.invDirty = False
            return True
        return False

    def getStatsDirty(self):
        """Checks if the stats (level, hunger etc.) need to be redrawn"""
        if self.statsDirty:
            self.statsDirty = False
            return True
        return False


class MonsterObject(PlayerObject):
    def receiveEvent(self, event):
        pass

    def say(self, what=None, that=None):
        pass

    def moveToLevel(self, level, type):
        self.dead = True

    def AIturn(self):
        for letter, lst in self.inventory:
            for item in lst:
                if hasattr(item, "__isarmor__") and item.slot in self.body.armor_slots and self.equipment[
                    item.slot] == None:
                    self.actions.append(Command("pickup", letter=letter))

        adjpositions = tuple(itertools.chain(generator.getadjacent(self.position, self.world.grid_size, 1, 0, 1),
                                             generator.longrangegetadjacent(self.position, self.world.grid_size, 10, 1,
                                                                            2)))

        target = None
        for obj in self.world.objects:
            if (isinstance(obj, PlayerObject) and tuple(obj.position[:2]) in adjpositions and self.visible[
                obj.position[:2]] and
                        type(obj).__name__ != type(self).__name__):
                target = obj
        if not target:
            self.actions.append(Command("move", direction=random.choice(((0, 1), (0, -1), (1, 0), (-1, 0)))))
        else:
            if target.position[0] > self.position[0]:
                self.actions.append(Command("move", direction=(1, 0)))
            elif target.position[0] < self.position[0]:
                self.actions.append(Command("move", direction=(-1, 0)))
            elif target.position[1] < self.position[1]:
                self.actions.append(Command("move", direction=(0, -1)))

            else:
                self.actions.append(Command("move", direction=(0, 1)))

        return False

    def update(self):

        return PlayerObject.update(self)


Command = items.Command
