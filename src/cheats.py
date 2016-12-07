from constants import *


class CheatHandler(object):
    def __init__(self, world, player):
        self.world=world
        self.player=player

    def cheatInput(self, action):
        self.cheat(action["code"])
  
    def cheat(self, string):
        if string == "Doctor Nostra Quakus":
            self.player.body.health=self.player.body.maxhealth
            self.player.say("You used the cheat code \"Doctor Nostra Quakus\"")
        elif string == "#227 BLAZE IT!":
            for i in self.player.xp.keys():
                self.player.add_xp(i,500)
            self.player.say("Blazed it.")
        elif string == "BinaryStew101":
            self.player.addtoinventory(self.world.itemPicker.fastRandomItem((0,0,0),self.player.world,self.player.cage,1,(ITM_ITEM,)))
        else:
            self.player.say("No cheat code \""+string+"\" is recognized")