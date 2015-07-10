'''
Created on 30 jun. 2015

@author: Maurits
'''
import items
#import inspect

from constants import *

class Identifier(items.Item):
    '''
    classdocs
    '''


    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        
        
        items.Item.__init__(self, *args, **kwargs)
        self.charges=1
    def use(self):
        #TODO: make a event sequence to prompt for the item to identify, check the number of uses remaining etc.
        if self.charges>0:
            self.owner.say("What would you like to identify?")
            self.owner.redictInput(self.identify_event)
    def identify_event(self, event):
        if event.type==KEYDOWN:
            
            itm=self.owner.removebyletter(event.unicode, False)
            if itm:
                self.owner.identify(itm[0])
                self.owner.say("this is a "+itm[0].getName())
                self.charges-=1
                self.owner.identify(self)
                return "normal",None
                
        return self.identify_event, None
    def getName(self, p=False):
        if not p:
            return self.name+"("+str(self.charges)+" charges)"
        else:
            return self.pname