'''
Created on 16 jun. 2015

@author: Maurits
'''
import items
import generator
import constants

class Explosion(items.StaticObject):
    '''
    DON'T CALL INIT YOURSEL
    '''

    @staticmethod
    def explode(world, position, cage, image, radius, effects):
        """Makes a explosion. Effects should be a sequence of
        tuples (or lists) containint function, *arguments)
        radius is a square radius, not a real circle, and
        it can't go threw walls
        Right now it freezes the game for 30 seconds, then fills the entire screen"""
        places=[position]
        for k in xrange(radius):
            #print ("K: "+str(k)+" r:"+str(radius)+" l:"+str(len(places)))
            nplaces=[]
            for i in places:
                l=tuple(generator.getadjacent(i, (constants.GRIDSIZE_X,constants.GRIDSIZE_Y), False, True, True))
                for j in l:
                    if (j not in places and not world.getsolid(j)):
                        nplaces.append(j)
            places.extend(nplaces)
            #print ("K: "+str(k)+" r:"+str(radius)+" l:"+str(len(places))+" ll: "+str(len(l))+" j: "+str(j))
        for k in places:
            for l in world.getcollisions(k):
                for m in effects:
                    m[0](l,*m[1:])
        for k in places:
            world.spawnItem(Explosion(k, image))
    def __init__(self, position, image):
        '''
        Constructor
        '''
        items.StaticObject.__init__(self, position, image)
        self.action_points=-200
        self.speed=100
    def gameTurn(self):
        self.markdead()
        