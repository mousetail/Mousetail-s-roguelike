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
        self.equipment_letters = {}
        self.equipment = {}
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
        self.inventory = {}

        self.input_mode = "normal"
        self.status_messages = []

        self.body = body
        self.body.mind = self
        self.body.updatemaxweight()
        self.clearAndRefreshEquipment()
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
            self.addtoinventory(i)
        self.statsDirty = True
        self.invDirty = True

    def clearAndRefreshEquipment(self):
        if hasattr(self, "equipment") and hasattr(self, "equipment_letters"):
            self.clearEquipment()

        self.equipment = {i: None for i in itertools.chain(self.body.armor_slots, self.body.weapon_slots)}
        self.equipment_letters = {}

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
        # self.say()
        # self.say("B}A friend of me named amish has the motto: \"Sometimes things don't add up, but maybe the series diverges\"")
        self.say()

    def wear(self, item, saystuff=True, dostuff=True):
        """A function used by event handling. Automatically puts a item into a slot, including the weapon slot
        is saystuff is true, it gives a message when something goes wrong, or when sucsesfull
        if dostuff is false, the function just validiates wheter it's possible to wear something, though it could still give a message
        annyway
        this is used to sepperate the validiation and messages in the even handling system"""
        slot = ""
        self.invDirty = True
        if hasattr(item, "__isweapon__"):
            slot = None
            for i in self.body.weapon_slots:
                if self.equipment[i] == None:
                    slot = i
            if not slot:
                if saystuff:
                    self.say("you don't have a hand free")
        elif hasattr(item, "__isarmor__"):
            if not item.slot:
                if saystuff:
                    self.say(item.name + " is not a valid piece of armor")
            elif item.slot not in self.equipment:
                if saystuff:
                    self.say("A " + str(self.body.name) + " can't wear anything on his " + str(item.slot))
            elif self.equipment[item.slot] is None:
                slot = item.slot
                if saystuff:
                    self.say("you wear the " + item.name)
            else:
                slot = None
                if saystuff:
                    self.say("you are allready wearing a " + item.slot)
        if slot:
            letter = items.getfirstemptyletter(self.equipment_letters)
            if dostuff:
                self.equipment[slot] = item
                self.equipment_letters[letter] = slot
            self.update_storage_fullness()
            return True
        elif slot == "":
            if saystuff:
                self.say(item.name + " is not a weapon")
            return False
        else:
            return False

    def eat(self, itm, saystuff=False, dostuff=True):
        """
        tries to eat the item,
        see wear for documentation of the arguments
        """
        if hasattr(itm, "eat"):
            if hasattr(itm, "nutrition"):
                self.fullness += itm.nutrition
                if dostuff:
                    msg = itm.eat()
                if saystuff:
                    self.say(msg)
                if dostuff:
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

    def addtoinventory(self, itm):
        """adds a item to the players inventory, correctly stacking similar items,
        and calculating the weight"""
        self.invDirty = True
        if isinstance(itm, list) or isinstance(itm, tuple):
            for i in itm:
                self.addtoinventory(i)
        else:
            itm.position = (0, 0)  # So they are equal in the inventory but not in the map
            if len(self.inventory) > 0:
                for i in self.inventory:
                    if self.inventory[i][0] == itm:
                        self.inventory[i].append(itm)
                        itm.owner = self
                        self.update_storage_fullness()
                        return True
                nextletter = items.getfirstemptyletter(self.inventory)
                # print nextletter
            else:
                nextletter = items.alphabet[0]
            self.inventory[nextletter] = [itm]
            itm.owner = self
            self.update_storage_fullness()
            return True

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
            # print "YOU ARE FASTER!"
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

    def say(self, *what, **kwargs):
        """send a message to the player, to be displayed in the log
        """
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
        actions = 0
        if self.events:
            self.old_postion = self.position[:]
            for event in self.events:
                if not self.input_mode or self.input_mode == "normal":
                    if event.type == pygame.KEYDOWN:

                        actions += 1
                        if event.key == pygame.K_UP:
                            self.actions.append(Command("move", {"direction": (1, 0)}))
                        elif event.key == pygame.K_DOWN:
                            self.actions.append(Command("move", {"direction": (-1, 0)}))
                        elif event.key == pygame.K_LEFT:
                            self.actions.append(Command("move", {"direction": (0, -1)}))
                        elif event.key == pygame.K_RIGHT:
                            self.actions.append(Command("move", {"direction": (0, 1)}))
                        elif event.key == pygame.K_h:
                            self.actions.append(Command("help"))
                        elif event.key == pygame.K_PERIOD:
                            self.actions.append(Command("wait"))
                        elif event.key == pygame.K_d:
                            self.say("what would you like to drop?")
                            actions -= 1
                            self.input_mode = "drop"
                        elif event.key == pygame.K_w:
                            self.say("what would you like to wear/wield")
                            actions -= 1
                            self.input_mode = "wear"
                        elif event.key == pygame.K_r:
                            self.say("what would you like to take off?")
                            actions -= 1
                            self.input_mode = "remove"
                        elif event.key == pygame.K_a:
                            self.say("what would you like to use?")
                            actions -= 1
                            self.input_mode = "use"
                        elif event.key == pygame.K_e:
                            self.say("what would you like to eat?")
                            actions -= 1
                            self.input_mode = "eat"
                        elif event.key == pygame.K_o:
                            self.actions.append(Command("open"))
                        elif event.unicode == "c":
                            self.actions.append(Command("close"))
                        elif event.key == pygame.K_COMMA:
                            self.actions.append(Command("pickup"))
                        elif event.key == pygame.K_t:
                            self.input_mode = "throw1"
                            actions -= 1
                            self.say("what would you like to throw?")
                        elif event.unicode == "C":
                            self.input_mode = cheats.CheatHandler(self.world, self).cheatInput

                        else:
                            actions -= 1
                elif self.input_mode == "drop":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.input_mode = "normal"
                            self.say("whatever")
                        else:
                            self.say(event.unicode)
                            itm = self.removebyletter(event.unicode, True)
                            if itm:
                                self.actions.append(Command("drop", item=itm))
                                self.input_mode = "normal"
                            else:
                                self.say("try again: ")
                        actions += 1
                elif self.input_mode == "wear":
                    if event.type == pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key == pygame.K_RETURN:
                            self.input_mode = "normal"
                            self.say("whatever")
                        else:
                            itm = self.removebyletter(event.unicode, False, True, 1)
                            if itm and itm[0] and self.wear(itm[0], True, False):
                                self.actions.append(Command("wear", letter=event.unicode))
                                self.input_mode = "normal"
                            else:
                                self.say("try again:")
                elif self.input_mode == "remove":
                    if event.type == pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key == pygame.K_RETURN:
                            self.input_mode = "normal"
                            self.say("whatever")
                        else:
                            itm = self.removearmorbyletter(event.unicode, False, True)
                            if itm:
                                self.input_mode = "normal"
                                self.actions.append(Command("remove", letter=event.unicode))
                            else:
                                self.say("try again: ")
                elif self.input_mode == "throw1":
                    if event.type == pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key == pygame.K_RETURN:
                            self.input_mode = "normal"
                            self.say("whatever")
                        else:
                            itm = self.removebyletter(event.unicode, False, True, 1)
                            if itm and itm[0] and hasattr(itm[0], "throw") and hasattr(itm[0], "throwEvent"):
                                self.redictInput(itm[0].throwEvent)
                            elif not itm or not itm[0]:
                                self.say("try again:")
                            else:
                                self.say("you can't throw a " + itm[0].name)
                elif self.input_mode == "use":
                    if event.type == pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key == pygame.K_RETURN:
                            self.input_mode = "normal"
                            self.say("whatever")
                            if random.randint(0, 100) == 33:
                                self.say("I am just trying to help...")
                        else:
                            itm = self.removebyletter(event.unicode, False, True, 1)
                            if itm:
                                self.actions.append(Command("use", item=itm[0]))
                                self.input_mode = "normal"
                                actions += 1
                            else:
                                self.say("try again: ")
                elif self.input_mode == "eat":
                    if event.type == pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key == pygame.K_RETURN:
                            self.input_mode = "normal"
                            self.say("whatever")
                        else:
                            itm = self.removebyletter(event.unicode, False, True, 1)
                            if itm and itm[0]:
                                self.actions.append(Command("eat", letter=event.unicode))
                                self.input_mode = "normal"
                                actions += 1
                            else:
                                self.say("try again: ")
                elif callable(self.input_mode):
                    if event.type != pygame.KEYDOWN or event.key != pygame.K_ESCAPE:
                        output = self.input_mode(event)
                        self.input_mode = output[0]
                        if output[1]:
                            self.actions.append(output[1])
                    else:
                        self.input_mode = "normal"
                elif isinstance(self.input_mode, tuple):
                    raise NotImplementedError("I don't even know what the function requestmoreinfo is supposed to do")
                    pass
        self.events[:] = []
        olddirty = self.dirty
        self.dirty = False
        return olddirty

    def removearmorbyletter(self, letter, removeitem=True, saystuff=False, addtoinv=True
                            ):
        """takes off armor and place it into the inventory of the player"""
        self.invDirty = True
        if letter in self.equipment_letters:
            slot = self.equipment_letters[letter]
            itm = self.equipment[slot]
            if removeitem:
                self.equipment[slot] = None  # Don't delete the slot, its permanent
                del self.equipment_letters[letter]
                if addtoinv:
                    self.addtoinventory(itm)
            self.update_storage_fullness()
            return itm
        else:
            if saystuff:
                self.say("you are not wielding anything with that name")
            self.update_storage_fullness()
            return False

    def removebyletter(self, letter, removeitem=True, saystuff=False, ammount=0):
        """takes a inventory item out of the inventory, then returns a list, containting amount of the specified item
        if there are less then amount items in a slot, only the amount available is returned"""
        self.invDirty = True
        if letter in self.inventory:
            if ammount == 0:
                itm = self.inventory[letter]
                if removeitem:
                    del self.inventory[letter]
                self.update_storage_fullness()

                self.update_storage_fullness()
                return itm
            else:
                itm = self.inventory[letter][:ammount]
                if removeitem:
                    del self.inventory[letter][:ammount]
                    if len(self.inventory[letter]) == 0:
                        del self.inventory[letter]
                self.update_storage_fullness()
                self.update_storage_fullness()
                return itm
        else:
            if saystuff:
                self.say("1}you don't have anything in slot " + letter)
            self.update_storage_fullness()
            return False

    def removebyidentity(self, itm):
        """removes a item from the invectory using "is" operator,
        usefull for having items remove themselves"""
        for i in self.inventory:
            for j in range(len(self.inventory[i])):
                if self.inventory[i][j] is itm:
                    del self.inventory[i][j]
                    if len(self.inventory[i]) == 0:
                        del self.inventory[i]
                    self.update_storage_fullness()
                    return j
        self.update_storage_fullness()
        return False

    def drop(self, itm, saystuff=True):
        """another internal action function, puts a specified item on the ground
        itm can be a Item object, or a list or tuple of Item objects"""
        if isinstance(itm, list) or isinstance(itm, tuple):
            for i in itm:
                i.position = self.position[:]

                i.owner = self.world
            self.world.objects.extend(itm)
            if len(itm) == 1:
                if saystuff:
                    self.say("dropped a " + itm[0].name)
                return True
            else:
                if saystuff:
                    self.say("dropped " + str(len(itm)) + " " + itm[0].pname)
                return True
        else:
            self.removebyidentity(itm)
            itm.position = self.position[:]
            self.world.spawnItem(itm)
            if saystuff:
                self.say("dropped a " + itm.name)
            return True

    def redictInput(self, method):
        """call the method with input data next update
        the method should take a pygame.Event object and return
        a tuple, first item being the next input mode ("normal" is back to normal controll,
        function is a function under same perimeters)
        second item is a action that has to be performed, which is a functon to be
        executed by the world's turn time calculator, this function should return the number of
        ticks the action should cost (average is 100)"""
        self.input_mode = method

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
            elif action.typ == "help":
                self.welcomeMessage()
            elif action.typ == "wait":
                actions += 100
            elif action.typ == "drop":
                if "letter" in action.data:
                    itm = self.removebyletter(action.data["letter"], True, False, 1)
                    self.drop(itm)
                elif "item" in action.data:
                    self.drop(action.data["item"])
                actions += 100
            elif action.typ == "wear":
                if "letter" in action.data:
                    itm = self.removebyletter(action.data["letter"], True, False, 1)
                    if itm:
                        self.wear(itm[0], False)
                elif "item" in action.data:
                    self.wear(action.data["item"], False)
                actions += 100
            elif action.typ == "remove":
                if "letter" in action.data:
                    self.removearmorbyletter(action.data["letter"], True, False, True)
                elif "item" in self.action.data:
                    raise NotImplementedError("line 523 in player input can't be fullfilled till a remove item by"
                                              "identity is implemented")
                actions += 100

            elif action.typ == "use":
                if "letter" in action.data:
                    itm = self.removebyletter(action.data["letter"], False, True, 1)
                    itm.owner = self
                    itm[0].use()
                elif "item" in action.data:
                    itm = action.data["item"]
                    itm.owner = self
                    itm.use()
                actions += 100
            elif action.typ == "eat":
                if "letter" in action.data:
                    itm = self.removebyletter(action.data["letter"], True, False, 1)
                    if itm and itm[0]:
                        if not self.eat(itm[0], True):
                            self.addtoinventory(itm[0])

                elif "item" in action.data:
                    self.removebyidentity(action.data["item"])
                    self.eat(action.data["item"], False)
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
                            self.world.objects.remove(i)
                            self.addtoinventory(i)
                            f = True
                            break

                if not f:
                    self.say("there is nothing to pick up!")
                actions += 100
            elif action.typ == "throw":

                if "letter" in action.data:
                    itm = self.removebyletter(action.data["letter"], False, True, 1)
                    self.drop(itm, False)
                    actions += itm[0].throw(self, action.data["direction"])
                elif "item" in action.data:
                    itm = action.data["item"]
                    self.drop(itm, False)
                    actions += itm.throw(self, action.data["direction"])

            elif action.typ == "other" or action.typ == "costom":
                actions += action.data["action"](action)

        self.body.update()
        self.fullness -= 1
        if FLAG_BURDENED in self.status_messages:
            self.fullness -= 1
        self.update_nutrition(True)

        return actions

    def iterInventory(self):
        """a iterator that iterates over the inventory, returning letter, item on each next"""
        for letter in self.inventory:
            for item in self.inventory[letter]:
                yield letter, item

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
        for letter, item in self.iterInventory():
            if isinstance(item, items.Armor) and item.slot in self.body.armor_slots and self.equipment[
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
