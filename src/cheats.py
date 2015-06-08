from constants import *

class CheatHandler(object):
    def __init__(self, world, player):
        self.world=world
        self.player=player
        self.tmpstring=""
        self.player.say("R}You lousy cheater!")
        self.player.say("R}>",False)

    def cheatInput(self, event):
        #print "CHEATING ..."
        if event.type==KEYDOWN:
            if event.key==K_RETURN:
                self.player.say()
                self.cheat(self.tmpstring)
                return "normal", None
            elif event.key==K_BACKSPACE:
                self.tmpstring=self.tmpstring[:-1]
                if len(self.tmpstring)>=0:
                    self.player.say("\b",False)
            else:
                self.tmpstring+=event.unicode
                self.player.say(event.unicode,False)
                return self.cheatInput, None
            
        
        return self.cheatInput, None
  
    def cheat(self, string):
        if string=="Doctor Nostra Quakus":
            self.player.body.health=self.player.body.maxhealth
            self.player.say("You used the cheat code \"Doctor Nostra Quakus\"")
        elif string=="#227 BLAZE IT!":
            for i in self.player.xp.keys():
                self.player.add_xp(i,500)
            self.player.say("Blazed it.")
        else:
            self.player.say("No cheat code \""+string+"\" is recognized")
                
            
