'''
Created on 29 dec. 2014

@author: Maurits
'''
import generator
import pygame
import time
import player_input
import generator_controller
import multiprocessing

#import items
import XMLloading
from sys import stdout as sysstdout
import constants
import os
class World(object):
    '''
    It is a level object that will change if levels change
    A class that keeps track of:
    *The grid
    *The object list
    *a light table(if I implement one)
    *Level generation
    '''


    def __init__(self, size=[50,50],cage=None,generatetype=1,stdout=sysstdout):
        '''
        Constructor
        '''
        self.level=-1
        self.player=None
        self.focus=None
        self.grid_size=size
        print "pipe starting..."
        self.pipe=multiprocessing.Pipe()
        print "process starting..."
        self.proc=multiprocessing.Process(target=generator_controller.generate,args=(self.pipe[1],))
        print "stage 2 process starting..."
        print self.proc.start()
        print self.pipe[0].recv()
        self.startGenerLevel(1)
        print "waiting..."
        self.dungeon_level=1
        self.itemPicker=XMLloading.XMLloader()
        self.itemPicker.loadFile(os.path.join("..","data","human.xml"))
        self.itemPicker.flush()
        self.cage=cage
        print ("Waiting for level to generate...")
        #print self.pipe[0].recv()
        print ("...")
        
        self.loadLevel(1)
         
        print "Finished finding objects"
        #self.objects.append(player_input.EventScheduler(self,10))
        self.dirty=True
        self.objindex=0
        self.newround=False
    def finalize(self):
        print(dir(self.proc))
        self.proc.terminate()
    def startGenerLevel(self, level):
        self.pipe[0].send("gener")
        print ("sent gener")
        self.pipe[0].send(level)
        print ("sent dungeon level...")
        self.pipe[0].send(self.grid_size)
        self.levelBeingGenerated=level
    
    def loadLevel(self, level):
        if self.level==level:
            return
        elif self.levelBeingGenerated==level:
            #CHECK IF EVERYTHING IS DONE
            print "R}loading level..."
            assert not self.pipe[0].poll(), "Some leftover information got stuck before loop"
            numstats=0
            status=1
            
            #SHOW PROGRESS...
            
            while status:
                self.pipe[0].send("stat")
                numstats+=1
                print "G}not yet got back from stat..."
                status=self.pipe[0].recv()
                print "(outside) status="+repr(status)+" numstats="+repr(numstats)
                assert not self.pipe[0].poll(), "Halfway loop, extra stuff got stuck"
                #time.sleep(0.1)
            
            assert not self.pipe[0].poll(), "Some leftover information got stuck"
            #if self.pipe[0].poll:
            #    self.pipe[0].recv()
            print "G}Ready to receive..."
            self.pipe[0].send("retu")
            
            self.grid=self.pipe[0].recv()
            print "receivd grid"
            print "the grid is:",self.grid
            objects=self.pipe[0].recv()
            self.objects=[]
            print "the objects are:",self.objects
            print ("level generated")
            for i in objects:
                if i[1]=="player":
                    if self.player is None:
                        pbody=self.itemPicker.fastItemByName("human",i[0],self,self.cage,returnbody=True)
                        self.objects.append(player_input.PlayerObject(i[0],pbody,self.cage,self,True))
                        self.focus=self.objects[-1]
                        self.player=self.focus #These are usually equal, but sometimes the screen could focus on something else
                        self.grid[self.player.position]=constants.TS_STAIRS_DOWN
                    else:
                        self.player.position=list(i[0])
                        self.objects.append(self.player)
                    
                else:
                    try:
                        assert len(i[0])==3
                        self.objects.append(self.itemPicker.fastRandomItem(i[0], self, self.cage, level, (i[1],)))
                    except IndexError:
                        print "r} CANT FIND OBJ FOR TAGS",i[1]
            
            self.objects.append(player_input.ObjectSpawner(self,2,self.dungeon_level))
            
            self.startGenerLevel(level+1)
            
    def update(self):
        """
        first calls update on all objects (for updating animations)
        then calculates who'se turn it is to move, then returns to
        3d_render
        """
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
            
        
    def event(self, event):
        """passes on events to objects"""
        for i in self.objects:
            if hasattr(i,"receiveEvent"):
                
                i.receiveEvent(event)
    def spawnItem(self, *items):
        """adds one or more object to the world, preferable over adding it yourself"""
        for item in items:
            item.owner=self
            self.objects.append(item)     
    def getsolid(self, position):
        return self.grid[position] in constants.WALLS
    def getcollisions(self, position):
        objs=[]
        for i in self.objects:
            if hasattr(i, "position") and i.position[0]==position[0] and i.position[1]==position[1]:
                objs.append(i)
        return objs
    def quit(self):
        for i in self.objects:
            if hasattr(i,"quit"):
                i.quit()
        self.pipe[0].send("quit")
        self.proc.join(1)
        self.pipe[0].close()
            
if __name__=="__main__":
    print "please run 3d_render.py"
    print dir(World)
    pygame.time.delay(5000)
