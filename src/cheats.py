from constants import *

class CheatHandler(object):
    def __init__(self, world, player):
        self.world=world
        self.player=player
        self.tmpstring=""
        self.player.say("r}cheating ...")
        self.player.say("your score is invalidiated")

    def cheatInput(self, event):
        #print "CHEATING ..."
        if event.type==KEYDOWN:
            if event.key==K_RETURN:
                self.cheat(self.tmpstring)
                return "normal", None
            elif event.key==K_BACKSPACE:
                self.tmpstring=self.tmpstring[:-1]
            else:
                self.tmpstring+=event.unicode
                self.player.say(event.unicode,False)
                return self.cheatInput, None
            
        
        return self.cheatInput, None
  
    def cheat(self, string):
        if string=="Doctor Nostra Quakus":
            player.body.health=player.body.maxhealth
                
            
