'''
Created on 7 dec. 2014

@author: Maurits
'''
import pygame
import random
import generator
import itertools
from constants import *


class FakeList(object):
    def append(self,what):
        pass
class ObjectSpawner(object):
    def __init__(self, world, chance=12):
        self.world=world
        self.grid=world.grid
        self.player=world.player
        self.chance=chance
        self.speed=100
        self.action_points=0
    def gameTurn(self):
        #print "generating object..."
        if random.randint(0,self.chance*len(self.world.objects)+2)==1:
            #print "Good chance..."
            room=random.choice(self.grid.rooms)
            if (not room.instersects(self.player.position)) and (not room.special):
                position=random.randint(room.bounds[0],room.bounds[0]+room.bounds[2]),random.randint(room.bounds[1],room.bounds[1]+room.bounds[3])
                self.world.objects.append(getitembyname.itemRandomizer.fastrandomitem(position, self.world, self.world.cage, 0, ITM_MONSTER))
                print "G}you hear some noises"
                
        return 300

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
        if recieveevent:
            self.events=[]
        else:
            self.events=FakeList()
    def draw(self,screen,position):
        if self.image and self.image.get_height()==128:
            screen.blit(self.image,(position[0],position[1]-32))
        elif self.image:
            
            screen.blit(self.image,(position[0],position[1]))
            
    def receiveEvent(self, event):
        pass
    def update(self):
        return False, False
    def __repr__(self):
        return ("<"+type(self).__name__+" at "+str(self.position)+">")
    

class PlayerObject(StaticObject):
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
    name="Player"
    
    def getstat(self, stat):
        return self.body.ratios[stat]*self.stats[stat]
    
    def __init__(self,position,body,cage,world, speed=100, name=None):
        self.speed=speed
        
        self.world=world
        self.visible=generator.Grid(self.world.grid_size,False)
        self.action_points=0
        self.dead=False
        self.actions=[Command("move",{"direction":(1,0)})]*2
        self.equipment={i:None for i in body.armor_slots+body.weapon_slots}
        self.equipment_letters={}
        self.stats={"level":1,"accuracy":1,"constitution":1,"strength":1}
        self.xp=self.stats.copy()
        self.inventory={}#"a":[items.Weapon((0,0),self.cage.lookup("shortsword.png"),self.cage,self.world,"short sword","short swords",1,1)]*2,
                        #"b":[items.Item((0,0),self.cage.lookup("shield.png"),self.cage,self.world,"shield","shields")]}
        
        self.input_mode="normal"
        self.status_messages=[]
        self.body=body(self, world)
        self.body.updatemaxweight()
        self.fullness=1000 #BASE 1000
        if name:
            self.name=name
        else:
            self.name=self.body.name
        StaticObject.__init__(self,position,cage.lookup(self.body.image_name),cage,world.grid,speed,True)
    def welcomeMessage(self):
        
        self.say("B}Welcome to Mousetail's roguelike")
        self.say("B}Use the arrow keys to walk arround")
        self.say("B} ',' to pick up items")
        self.say("B}'w' to wield or wear")
        self.say("B}'e' to eat, 'a' to apply")
        self.say("B}'h' to repeat this message")
        self.say("B}thanks for playing!")
        self.say()
    def wear(self, item, saystuff=True, dostuff=True):
        slot=""
        if isinstance(item,items.Weapon):
            slot=None
            for i in self.body.weapon_slots:
                if self.equipment[i]==None:
                    slot=i
            if not slot:
                if saystuff:
                    self.say("you don't have a hand free")
        elif isinstance(item, items.Armor):
            if not item.slot:
                if saystuff:
                    self.say(item.name+" is not a valid piece of armor")
            elif item.slot not in self.equipment:
                if saystuff:
                    self.say("A "+self.body.name+" can't wear anything on his "+ item.slot)
            elif self.equipment[item.slot]==None:
                slot=item.slot
                if saystuff:
                    self.say("you wear the "+item.name)
            else:
                slot=None
                if saystuff:
                    self.say("you are allready wearing a "+item.slot)
        if slot:
            letter=items.getfirstemptyletter(self.equipment_letters)
            if dostuff:
                self.equipment[slot]=item
                self.equipment_letters[letter]=slot
            self.update_storage_fullness()
            return True
        elif slot=="":
            if saystuff:
                self.say(item.name+" is not a weapon")
            return False
        else:
            return False
    def eat(self, itm, saystuff=False, dostuff=True):
        if hasattr(itm,"eat"):
            if hasattr(itm,"nutrition"):
                self.fullness+=itm.nutrition
                if dostuff:
                    msg=itm.eat()
                if saystuff:
                    self.say(msg)
                if dostuff:    
                    self.add_xp("strength", int((itm.nutrition/100)**0.5))
                return True
            else:
                return itm.eat()
        else:
            if saystuff:
                self.say("you try to bite the "+itm.name+" but it's to solid, you almost break a tooth!")
            return False
        self.update_nutrition(saystuff)
    
    def update_nutrition(self, saystuff=False):
        oldmsg=[]
        for i in [FLAG_HUNGRY_2,FLAG_HUNGRY,FLAG_FULL,FLAG_FULL_2]:
            if i in self.status_messages:
                self.status_messages.remove(i)
                oldmsg.append(i)
        if self.fullness>1400:
            self.status_messages.append(FLAG_FULL_2)
            if saystuff and FLAG_FULL_2 not in oldmsg:
                self.say("your belly feels like its bursting!")
        elif self.fullness>1000:
            self.status_messages.append(FLAG_FULL)
            if saystuff and FLAG_FULL not in oldmsg:
                self.say("you feel comfortabally full")
        elif self.fullness>0:
            pass
        elif self.fullness>-400:
            
            self.status_messages.append(FLAG_HUNGRY)
            if saystuff and FLAG_HUNGRY not in oldmsg:
                self.say("you are starting to feel hungry")
        else:
            self.status_messages.append(FLAG_HUNGRY_2)
            if saystuff and FLAG_HUNGRY_2 not in oldmsg:
                self.say("all you can think about is food now")
    def addtoinventory(self, itm):
        
        itm.position=(0,0) #So they are equal in the inventory but not in the map
        if len(self.inventory)>0:
            for i in self.inventory:
                if self.inventory[i][0]==itm:
                    self.inventory[i].append(itm)
                    itm.owner=self
                    self.update_storage_fullness()
                    return True
            nextletter=items.getfirstemptyletter(self.inventory)
            #print nextletter
        else:
            nextletter=items.alphabet[0]
        self.inventory[nextletter]=[itm]
        itm.owner=self
        self.update_storage_fullness()
        return True
    def getspeed(self):
        
        s=self.speed
        if FLAG_BURDENED in self.status_messages:
            s-=25
        if FLAG_FULL_2 in self.status_messages:
            s-=25
        elif FLAG_FULL in self.status_messages:
            s+=10
        if FLAG_HUNGRY in self.status_messages:
            s-=25
        elif FLAG_HUNGRY_2 in self.status_messages:
            s-=35
        if FLAG_FAST in self.status_messages:
            s*=2
            #print "YOU ARE FASTER!"
        elif FLAG_FAST_2 in self.status_messages:
            s*=3
        if s<1:
            s=1
        return s
    def update_storage_fullness(self):
        s=sum(i[1].getWeight() for i in self.iterInventory())
        s+=sum(i[2].getWeight() for i in self.iterArmor())
        if s<=self.body.maxweight:
            if FLAG_BURDENED in self.status_messages:
                self.status_messages.remove(FLAG_BURDENED)
        else:
            if FLAG_BURDENED not in self.status_messages:
                self.status_messages.append(FLAG_BURDENED)
    def receiveEvent(self, event):
        self.events.append(event)
    def add_xp(self, skill, ammount):
        self.xp[skill]+=ammount
        if self.xp[skill]>(5**self.stats[skill]):
            self.level_up(skill, True)
    def level_up(self, skill, changexp=False):
        if changexp:
            self.xp[skill]-=5**self.stats[skill]
            self.stats[skill]+=1
        if skill=="level":
            self.say("You sudenly feel very confident")
        elif skill=="accuracy":
            if self.stats["accuracy"]<10:
                obj="mountain"
            elif self.stats["accuracy"]<50:
                obj="cow"
            else:
                obj="needle"
            self.say("B}You feel like you could hit a "+obj+" at "+str(10*self.stats["accuracy"])+"M distance")
        elif skill=="constitution":
            self.body.updatemaxhealth()
            self.say("B}You feel healthy")
        elif skill=="strength":
            self.body.updatemaxweight()
            self.say("B}You feel strong")
    def say(self, what=""):
        """send a message to the player, to be displayed in the log"""
        print what
    def kill(self, message):
        self.say("1}you die")
        self.say("1}you where killed by a "+message)
        self.body.drop()
        self.dead=True
    def update(self):
        actions=0
        redraws=0
        if self.events:
            self.old_postion=self.position[:]
            for event in self.events:
                if self.input_mode=="normal":
                    if event.type==pygame.KEYDOWN:
                        
                        actions+=1
                        redraws+=1
                        if event.key==pygame.K_UP:
                            self.actions.append(Command("move",{"direction":(1,0)}))
                        elif event.key==pygame.K_DOWN:
                            self.actions.append(Command("move",{"direction":(-1,0)}))
                        elif event.key==pygame.K_LEFT:
                            self.actions.append(Command("move",{"direction":(0,-1)}))
                        elif event.key==pygame.K_RIGHT:
                            self.actions.append(Command("move",{"direction":(0,1)}))
                        elif event.key==pygame.K_h:
                            self.actions.append(Command("help"))
                        elif event.key==pygame.K_PERIOD:
                            self.actions.append(Command("wait"))
                        elif event.key==pygame.K_d:
                            self.say("what would you like to drop?")
                            actions-=1
                            self.input_mode="drop"
                        elif event.key==pygame.K_w:
                            self.say("what would you like to wear/wield")
                            actions-=1
                            self.input_mode="wear"
                        elif event.key==pygame.K_r:
                            self.say("what would you like to take off?")
                            actions-=1
                            self.input_mode="remove"
                        elif event.key==pygame.K_a:
                            self.say("what would you like to use?")
                            actions-=1
                            self.input_mode="use"
                        elif event.key==pygame.K_e:
                            self.say("what would you like to eat?")
                            actions-=1
                            self.input_mode="eat"
                        elif event.key==pygame.K_o:
                            self.actions.append(Command("open"))
                        elif event.key==pygame.K_c:
                            self.actions.append(Command("close"))
                        elif event.key==pygame.K_COMMA:
                            self.actions.append(Command("pickup"))
    
                        else:
                            actions-=1
                elif self.input_mode=="drop":
                    if event.type==pygame.KEYDOWN:
                        if event.key==pygame.K_RETURN:
                            self.input_mode="normal"
                            self.say("whatever")
                        else:
                            
                            self.say(event.unicode)
                            itm=self.removebyletter(event.unicode,True)
                            if itm:
                                self.actions.append(Command("drop",item=itm))
                                self.input_mode="normal"
                            else:
                                self.say("try again: ")
                            
                        
                        actions+=1
                        redraws+=1
                elif self.input_mode=="wear":
                    
                    if event.type==pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key==pygame.K_RETURN:
                            self.input_mode="normal"
                            self.say("whatever")
                            redraws+=1
                        else:
                            itm=self.removebyletter(event.unicode,False,True,1)
                            if itm and itm[0] and self.wear(itm[0], True, False):
                                self.actions.append(Command("wear",letter=event.unicode))
                                self.input_mode="normal"
                            else:
                                self.say("try again:")
                        redraws+=1
                elif self.input_mode=="remove":
                    if event.type==pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key==pygame.K_RETURN:
                            self.input_mode="normal"
                            self.say("whatever")
                            redraws+=1
                        else:
                            itm=self.removearmorbyletter(event.unicode,False, True)
                            if itm:
                                self.input_mode="normal"
                                self.actions.append(Command("remove",letter=event.unicode))
                            else:
                                self.say("try again: ")
                                redraws+=1
                elif self.input_mode=="use":
                    #-----------------------------------------I WANT TO ADD MORE COMplicATED BEHAVIOR FOR THIS
                    #TODO: allow advanced methods
                    if event.type==pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key==pygame.K_RETURN:
                            self.input_mode="normal"
                            self.say("whatever")
                            if random.randint(0,100)==33:
                                self.say("I am just trying to help...")
                            redraws+=1
                        else:
                            itm=self.removebyletter(event.unicode,False, True, 1)
                            if itm:
                                self.actions.append(Command("use",item=itm[0]))
                                self.input_mode="normal"
                                actions+=1
                                redraws+=1
                            else:
                                self.say("try again: ")
                                redraws+=1
                elif self.input_mode=="eat":
                    if event.type==pygame.KEYDOWN:
                        self.say(event.unicode)
                        if event.key==pygame.K_RETURN:
                            self.input_mode="normal"
                            self.say("whatever")
                            redraws+=1
                        else:
                            itm=self.removebyletter(event.unicode,False, True, 1)
                            if itm and itm[0]:
                                self.actions.append(Command("eat",letter=event.unicode))
                                self.input_mode="normal"
                                actions+=1
                                redraws+=1
                            else:
                                self.say("try again: ")
                                redraws+=1        
                elif callable(self.input_mode):
                    if event.type!=pygame.KEYDOWN or event.key!=pygame.K_ESCAPE:
                        output=self.input_mode(event)
                        self.input_mode=output[0]
                        if output[1]:
                            self.actions.append(output[1])
                    else:
                        self.input_mode="normal"
                elif isinstance(self.input_mode, tuple):
                    raise NotImplementedError("I don't even know what the function requestmoreinfo is supposed to do")
                    pass #Relates to requestmoreinfo function
                            
        self.events[:]=[]
        return bool(redraws)
    def requestmoreinfo(self, callback, infotype, **kwars):
        if infotype is not None:
            self.input_mode=(infotype, callback)
        else:
            self.input_mode="normal"
    def removearmorbyletter(self, letter, removeitem=True, saystuff=False):
        if letter in self.equipment_letters:
            slot=self.equipment_letters[letter]
            itm=self.equipment[slot]
            if removeitem:
                self.equipment[slot]=None #Don't delete the slot, its permanent
                del self.equipment_letters[letter]
            self.update_storage_fullness()
            return itm
        else:
            if saystuff:
                self.say("you are not wielding anything with that name")
            self.update_storage_fullness()
            return False
        
    def removebyletter(self, letter, removeitem=True, saystuff=False, ammount=0):
        if letter in self.inventory:
            if ammount==0:
                itm=self.inventory[letter]
                if removeitem:
                    del self.inventory[letter]
                self.update_storage_fullness()
                return itm
            else:
                itm=self.inventory[letter][:ammount]
                if removeitem:
                    del self.inventory[letter][:ammount]
                    if len(self.inventory[letter])==0:
                        del self.inventory[letter]
                self.update_storage_fullness()
                return itm
        else:
            if saystuff:
                self.say("1}you don't have anything in slot "+letter)
            return False
        
        self.update_storage_fullness()
    def removebyidentity(self, itm):
        for i in self.inventory:
            for j in range(len(self.inventory[i])):
                if self.inventory[i][j] is itm:
                    del self.inventory[i][j]
                    if len(self.inventory[i])==0:
                        del self.inventory[i]
                    self.update_storage_fullness()
                    return j
        self.update_storage_fullness()
        return False
    def drop(self, itm):
        for i in itm:
            i.position=self.position[:]
            
            i.owner=self.world
        self.world.objects.extend(itm)
        if len(itm)==1:
            self.say("dropped a "+itm[0].name)
            return True
        else:
            self.say("dropped "+str(len(itm))+" "+itm[0].pname)
            return True
    
    def redictInput(self, method):
        self.input_mode=method
    def AIturn(self):
        return True
    def gameTurn(self):
        actions=0
        redraws=0
        if self.actions:
            action=self.actions.pop()
            if action.typ=="move":
                self.old_position=self.position[:]
                
                actions+=100
                redraws+=1
                self.old_position[0]+=action.data["direction"][0]
                self.old_position[1]+=action.data["direction"][1]
                for i in self.world.objects:
                    if hasattr(i,"position") and i is not self and i.position==self.old_position:
                        if isinstance(i,PlayerObject):
                            self.old_position=self.position
                            self.body.attack(i)
                if self.world.grid.hasindex(self.position) and (not self.world.grid[self.old_position] in WALLS):
                    #self.say("you walk from "+str(self.position)+" to "+str(self.old_position))
                    self.position[:]=self.old_position
                    actions-=1
            elif action.typ=="help":
                self.welcomeMessage()
            elif action.typ=="wait":
                actions+=100
            elif action.typ=="drop": #------------------------
                if "letter" in action.data:
                    itm=self.removebyletter(action.data["letter"], True, False, 1)
                    self.drop(itm)
                elif "item" in action.data:
                    self.drop(action.data["item"])
                actions+=100
            elif action.typ=="wear":
                if "letter" in action.data:
                    itm=self.removebyletter(action.data["letter"],True, False, 1)
                    if itm:
                        self.wear(itm[0], False)
                elif "item" in action.data:
                    self.wear(action.data["item"], False)
                actions+=100
            elif action.typ=="remove":
                if "letter" in action.data:
                    itm=self.removearmorbyletter(action.data["letter"], True, False)
                    self.addtoinventory(itm)
                elif "item" in self.action.data:
                    raise NotImplementedError("line 523 in player input can't be fullfilled till a remove item by identity is implemented")
                actions+=100
               
            elif action.typ=="use":
                if "letter" in action.data:
                    itm=self.removebyletter(action.data["letter"],False, True, 1)
                    itm.owner=self
                    itm[0].use()
                elif "item" in action.data:
                    itm=action.data["item"]
                    itm.owner=self
                    itm.use()
                actions+=100
            elif action.typ=="eat":
                if "letter" in action.data:
                    itm=self.removebyletter(action.data["letter"], True, False, 1)
                    if itm and itm[0]:
                        if not self.eat(itm[0], True):
                            self.addtoinventory(itm[0])
                            
                elif "item" in action.data:
                    itm=self.removebyidentity(action.data["item"])
                    self.eat(action.data["item"],False)
                actions+=300
            elif action.typ=="open":
                #This one should work without intervention
                wk=False
                for i in generator.getadjacent(self.position, self.world.grid_size, 0, 0, 1):
                    if self.world.grid[i] in generator.door_pair_reverse:
                        self.world.grid[i]=generator.door_pair_reverse[self.world.grid[i]]
                        self.say("you open the door")
                        redraws+=1
                        actions+=100
                        wk=True
                        break
                    elif self.world.grid[i] in generator.door_pair_lock:
                        self.say("that door is locked")
                        wk=True
                if not wk:
                    
                    self.say("There is no door here")
                redraws+=1
                actions+=100
            elif action.typ=="close":
                wk=False
                for i in generator.getadjacent(self.position, self.world.grid_size, 0, 0, 1):
                    if self.world.grid[i] in generator.door_pairs:
                        self.world.grid[i]=generator.door_pairs[self.world.grid[i]]
                        self.say("you close the door")
                        redraws+=1
                        actions+=100
                        wk=True
                        break
                if not wk:
                    self.say("There is no door here")
                    actions-=1
                redraws+=1
            elif action.typ=="pickup":
                f=False
                for i in self.world.objects:
                    if hasattr(i,"position") and i is not self and i.position==self.position:
                        if isinstance(i,items.Item):
                            self.world.objects.remove(i)
                            self.addtoinventory(i)
                            f=True
                            break
                if not f:
                    self.say("there is nothing to pick up!")
                actions+=100
            elif action.typ=="other" or action.typ=="costom":
                actions+=action.data["action"](action)
                    
                
                
                
                
                
                 
        self.body.update()
        self.fullness-=1
        if FLAG_BURDENED in self.status_messages:
            self.fullness-=1
        self.update_nutrition(True)
        
        return actions
    def iterInventory(self):
        for letter in self.inventory:
            for item in self.inventory[letter]:
                yield letter, item
    def iterArmor(self):
        for letter in self.equipment_letters:
            if self.equipment[self.equipment_letters[letter]]:
                yield letter, self.equipment_letters[letter], self.equipment[self.equipment_letters[letter]]
                #print letter, self.equipment_letters[letter], self.equipment[self.equipment_letters[letter]]
    def flag(self, flag):
        self.status_messages.append(flag)
    def unflag(self, flag):
        self.status_messages.remove(flag)
class MonsterObject(PlayerObject):
    
    def receiveEvent(self, event):
        pass
    def say(self, what): pass
    def AIturn(self):
        for letter, item in self.iterInventory():
            if isinstance(item, items.Armor) and item.slot in self.body.armor_slots and self.equipment[item.slot]==None:
                self.actions.append(Command("pickup", letter=letter))
                
                
        adjpositions= tuple(itertools.chain(generator.getadjacent(self.position, self.world.grid_size, 1, 0, 1),
                                            generator.longrangegetadjacent(self.position,self.world.grid_size, 10, 1, 2)))
        
        target=None
        for obj in self.world.objects:
            if (isinstance(obj, PlayerObject) and tuple(obj.position) in adjpositions and self.visible[obj.position] and
                    type(obj).__name__!=type(self).__name__):
                target=obj
        if not target:
            self.actions.append(Command("move",direction=random.choice(((0,1),(0,-1),(1,0),(-1,0)))))
        else:
            if target.position[0]>self.position[0]:
                self.actions.append(Command("move", direction=(1,0)))
            elif target.position[0]<self.position[0]:
                self.actions.append(Command("move", direction=(-1,0)))
                #print "Moved down"
            elif target.position[1]<self.position[1]:
                self.actions.append(Command("move", direction=(0,-1)))
                #print "moved left"
            else:
                self.actions.append(Command("move", direction=(0,1)))
                #print "moved right"
        return False
    def update(self):
        
        return PlayerObject.update(self)

import items
import monster_body
import getitembyname

Command=items.Command