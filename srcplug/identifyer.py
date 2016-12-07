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

    def getUseArgs(self):
        return "what would you like to identify?", USER_TYPE_ITEM, "target", None

    def use(self, **args):
        assert "target" in args, str(args)
        itm = args["target"]
        if itm:
            self.owner.identify(itm)
            self.charges -= 1
            self.owner.identify(self)
            return "this is a " + itm.getName()
        else:
            raise ValueError("itm may not be none")

    def getName(self, p=False):
        if not p:
            return self.name+"("+str(self.charges)+" charges)"
        else:
            return self.pname