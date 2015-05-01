'''
Created on 29 dec. 2014

@author: Maurits
'''
import generator
import pygame
import random
import player_input
import items
import getitembyname
class World(object):
    '''
    It is a level object that will change if levels change
    A class that keeps track of:
    *The grid
    *The object list
    *a light table(if I implement one)
    *Level generation
    '''


    def __init__(self, size=[100,100],cage=None,generatetype=1):
        '''
        Constructor
        '''
        self.grid_size=size
        self.grid=generator.Generator(size)
        self.objects=self.grid.generate()
        tmpobjects=[]
        self.cage=cage
        
        for i in self.objects:
            if i[1]=="player":
                pbody=player_input.monster_body.HumanBody
                tmpobjects.append(player_input.PlayerObject(i[0],pbody,self.cage,self))
                self.focus=tmpobjects[-1]
                self.player=self.focus #These are usually equal, but sometimes the screen could focus on something else
                
            else:
                tmpobjects.append(getitembyname.itemRandomizer.fastrandomitem(i[0], self, self.cage, 1, (i[1],)))
            #elif i[1]=="monster":
            #    tmpobjects.append(getitembyname.itemRandomizer.fastrandommonster(i[0],self,self.cage,1))
            #elif i[1]=="item":
            #    tmpobjects.append(getitembyname.itemRandomizer.fastrandomitem(i[0],self,self.cage,1))
            
        
        #print getitembyname.itemRandomizer.items
        
        self.objects=tmpobjects
        self.objects.append(player_input.ObjectSpawner(self,2))
        #self.objects.append(player_input.EventScheduler(self,10))
        self.dirty=True
        self.objindex=0
        self.newround=False
    def update(self):
        self.dirty=False
        for i in self.objects:
            if hasattr(i, "update"):
                self.dirty=self.dirty or i.update()
        deadobj=[]
        for obj in self.objects:
            if hasattr(obj, "dead") and obj.dead:
                deadobj.append(obj)
        for obj in deadobj:
                self.objects.remove(obj)
                if self.player==deadobj:
                    #self.player=None
                    pass
        while True:
            i=self.objects[self.objindex]
            if hasattr(i,"action_points") and i.action_points>0:
                if hasattr(i,"AIturn"):
                    i.AIturn()
                if hasattr(i,"gameTurn"):
                    if  (not hasattr(i,"actions") or len(i.actions)>0):
                        change=i.gameTurn()
                    else:
                        change=0
                    if change<=0:
                        
                        #print "waiting for player..."
                        break
                    else:
                        if not isinstance(i,player_input.MonsterObject):
                            #print "not waiting for player..."
                            pass
                        if hasattr(i,"body"):
                            i.body.get_visible()
                        if hasattr(i,"action_points"):
			  i.action_points-=change
                        self.newround=True
                        #break #todo: fix this
                else:
                    pass
                    #print "not having gameTurn"
            
            self.objindex+=1
            #print "next object"
            if self.objindex>=len(self.objects):
                self.objindex=0
                if not self.newround:
                    
                    for i in self.objects:
                        if hasattr(i,"action_points"):
                            if hasattr(i, "getspeed"):
                                i.action_points+=i.getspeed()
                            else:
                                i.action_points+=i.speed
                else:
                    
                    self.dirty=True
                    self.newround=False
                    
                    break
                
                self.newround=False
            elif isinstance(i,player_input.PlayerObject):
                #print "not having action_points",i
                pass
                #print "not having action points"
        
    def event(self, event):
        for i in self.objects:
            if hasattr(i,"receiveEvent"):
                
                i.receiveEvent(event)
    def spawnItem(self, item):
        item.owner=self
        self.objects.append(item)     

if __name__=="__main__":
    print "please run 3d_render.py"
    print dir(World)
    pygame.time.delay(5000)