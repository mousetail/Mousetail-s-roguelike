'''
Created on 8 okt. 2014

@author: Maurits
'''
import datetime #used to calculate how much time it took to generate the level
from itertools import product as itertoolsproduct #uses itertools to calculate adjacent tiles from a tile in next line
from itertools import chain as itertoolschain
from constants import *
adjacent=[(-1,0),(0,-1),(1,0),(0,1)]
diognaladj=list(itertoolsproduct([-1,1],[-1,1]))

def getadjacent(coords, gridsize=(100,100), randomorder=False, diognal=False, straight=True):
    if randomorder:
        random.shuffle(adjacent)
    if straight:
        for i in adjacent:
            n=coords[0]+i[0],coords[1]+i[1]
            if (n[0]>0 and n[0]<gridsize[0] and n[1]>0 and n[1]<gridsize[1]):
                yield n
    if diognal:
        for i in diognaladj:
            n=coords[0]+i[0],coords[1]+i[1]
            if (n[0]>0 and n[0]<gridsize[0] and n[1]>0 and n[1]<gridsize[1]):
                yield n
def longrangegetadjacent(coords=(50,50), gridsize=(100,100), length=10, randomorder=False, minlength=1):
    if randomorder:
        random.shuffle(adjacent)
    for i in adjacent:
        for l in range(minlength,length):
            n=coords[0]+(i[0]*l),coords[1]+(i[1]*l)
            if (n[0]>0 and n[0]<gridsize[0] and n[1]>0 and n[1]<gridsize[1]):
                yield n
def distance(ns):
    n1=ns[0]
    n2=ns[1]
    return abs(n1[0]-n2[0])+abs(n1[1]-n2[1])
class Storage_Obj(object):
    def __init__(self,value=False):
        self.value=value
    def cleardeepnes(self):
        inner=self.value
        while isinstance(inner,Storage_Obj):
            inner=inner.value
        return inner

import random
class Grid(object):
    def __init__(self,size,objecttype=0):
        
        """objecttype:
        0 for int
        [] for list
        None for object
        """
        self.rowsize=size[0]
        self.data=[]
        self.size=size
        for i in range(size[0]*size[1]):
            self.data.append(objecttype)
    def hasindex(self,index):
        return (index[0]>=0 and index[0]<self.size[0] and
                index[1]>=0 and index[1]<self.size[1])
    def __getitem__(self,item):
        if item[0]<0 or item[0]>self.rowsize or item[1]<0:
            raise IndexError(item)
        try:
            item=self.data[item[1]*self.rowsize+item[0]]
        except IndexError:
            raise IndexError(item)
        return item
    def __setitem__(self,item,setto):
        if isinstance(item,slice):
            for i in self:
                if item.start[0]<=i[0]<=item.stop[0] and item.start[1]<=i[1]<=item.stop[1]:
                    self[i]=setto
                    #print i
        else:
            try:
                self.data[item[1]*self.rowsize+item[0]]=setto
            except IndexError:
                raise IndexError(item)
        #print self[item]
    
    def __iter__(self):
        for i in range(self.rowsize):
            for j in range(self.size[1]):
                yield i,j
class Room(object):
    def __init__(self, **kwargs):
        if "floortype" in kwargs.keys():
            self.floortype=kwargs["floortype"]
        else:
            self.floortype=None
        if "walltype" in kwargs.keys():
            self.walltype=kwargs["walltype"]
        else:
            self.walltype=None
        if "bounds" in kwargs.keys():
            self.bounds=kwargs["bounds"]
        else:
            self.bounds=None
        if "doortype" in kwargs.keys():
            self.doortype=kwargs["doortype"]
        else:
            self.doortype=0
        if "special" in kwargs:
            self.special=kwargs["special"]
        else:
            self.special=False
        self.doors=[]
        self.specialobjects=[]
    def instersects(self, other):
        if isinstance(other,Room):
            other=other.bounds
        if len(other)==4:
            if self.bounds[0]<=other[0]+other[2] and \
               self.bounds[0]+self.bounds[2]>=other[0] and \
               self.bounds[1]<=other[1]+other[3] and \
               self.bounds[1]+self.bounds[3]>=other[1]:
                return True
            else:
                return False
        elif len(other)==2:
            if self.bounds[0]<=other[0]<=self.bounds[0]+self.bounds[2] and \
               self.bounds[1]<=other[1]<=self.bounds[1]+self.bounds[3]:
                return True
            else:
                return False
        raise ValueError("List should have 2 or 4 items",other)
    def center(self):
        return (self.bounds[0]+self.bounds[2]//2,self.bounds[1]+self.bounds[3]//2)
    def distance(self,other):
        c1=self.center()
        c2=other.center()
        return -abs(c1[0]-c2[0])-abs(c2[1]-c1[1])
    def iscorner(self, point):
        if (point[0]==self.bounds[0] or point[0]==self.bounds[0]+self.bounds[2]) and \
           (point[1]==self.bounds[1] or point[1]==self.bounds[1]+self.bounds[3]):
            return True
        else:
            return False
            
        
        
class SpecialObject(object):
    def __init__(self,position,type_):
        self.position=position
        self.type=type_

class Generator(Grid):
    '''
    generates levels by first placing a room and then tracing the path to the closest room that already exists
    TODO: look at http://journal.stuffwithstuff.com/2014/12/21/rooms-and-mazes/
    Objectdefinitions: Keys:
    Roomtype: 0: ? 1:walltypes, 2: floortypes, 3:? 4: doortypes, 5:special
    Walltypes: Key: id, Value: Tuple/list of possible types, 1 item: type of wall. 4 items: Bottom, right, left, top. Each item is a tuple of possible values
    froortypes: Key: id, Value: indexes of types of floor, use constants
    paths: tuple of possible paths used between rooms. Random path is selected each tile.
    1perdungeon: tuple of tuples, of "value","type": value is tile index or category ID for generator, type="OBJ" for object, "TYPE" for type
    '''
    def __init__(self, size, dlevel=0, objectdefinitions=None,atributes=None):
        if objectdefinitions is None:
            self.objectdefinitions={"empty":TS_EMPTY,
                               "roomtypes":((7,(1,),(1,),(12,),((TS_DOOR_LEFT,TS_DOOR_OPEN_LEFT),(TS_DOOR_RIGHT,TS_DOOR_OPEN_RIGHT,)),False),
                                            (1,(2,),(3,),(),((TS_LOCKED_DOOR_LEFT,),(TS_LOCKED_DOOR_RIGHT,)),True)
                                            ), #frequency,(walltypes,),(floortypes,),(specialobjects,),(doors,),spawnsobjects
                               "walltypes":{1:((TS_WALL_BOTTOM,),(TS_WALL_RIGHT,),(TS_WALL_LEFT,),(TS_WALL_TOP,)),2:((TS_GREEN_WALL_1,TS_GREEN_WALL_2),)},
                               "floortypes":{1:(TS_FLOOR_NORMAL,TS_FLOOR_SPECIAL),3:(TS_GREEN_FLOOR_1,TS_GREEN_FLOOR_2,TS_GREEN_FLOOR_3)},
                               "specialobjectclasses":{1:14},
                               "paths":(11,12,13),
                               "1perdungeon":(("player","OBJ"),(TS_PAPRI,"TILE"),(TS_STAIRS_UP,"TILE"),(TS_STAIRS_DOWN,"TILE"))+((ITM_MONSTER,"OBJ"),)*12+((ITM_ITEM,"OBJ"),)*48
                               
                               }
            
            
            #print self.objectdefinitions
        else:
            
            self.objectdefinitions=objectdefinitions
            #print self.objectdefinitions,"2"
        if atributes==None:
            self.atributes={"roomfactor":512,
                            "roomsizex":(4,8),
                            "roomsizey":(4,8)}
        else:
            self.atributes=atributes
        self.dlevel=dlevel
        #print self.objectdefinitions
        Grid.__init__(self, size, self.objectdefinitions["empty"])

    def start(self):
        self.startime=datetime.datetime.now()
        self.numrooms=len(self.data)//self.atributes["roomfactor"]
        self.rooms=[]
        self.allpaths=[]
    def step(self):
            roomtype=random.choice(tuple(itertoolschain(*((i,)*i[0] for i in self.objectdefinitions["roomtypes"]))))
            #print roomtype
            walltype=self.objectdefinitions["walltypes"][random.choice(roomtype[1])]
            floortype=self.objectdefinitions["floortypes"][random.choice(roomtype[2])]
            doortype=roomtype[4]
            room=Room(floortype=floortype,walltype=walltype,doortype=doortype, special=roomtype[5])
            itworks=False
            tries=0
            while tries<=MAXTRIES and not itworks:
                tries+=1
                rectangle=[random.randint(1,self.size[0]/2-(self.atributes["roomsizex"][1]+1))*2,
                          random.randint(1,self.size[1]/2-(self.atributes["roomsizey"][1]+1))*2,
                          random.randint(*self.atributes["roomsizex"])*2,
                          random.randint(*self.atributes["roomsizey"])*2]
                itworks=True
                
                room.bounds=rectangle
                for room2 in self.rooms:
                    if room2.instersects(rectangle):
                        itworks=False
                        #print "3} ITWORKS SET TO FALSE, line 161"
                for point in self.allpaths:
                    if point is not None:
                        #print self.allpaths
                        #print point
                        if room.instersects(point):
                            itworks=False
                    else:
                        print self.allpaths
            if len(roomtype[2]) and random.randint(0,4)==0:
                position=random.randint(room.bounds[0]+1,room.bounds[0]+room.bounds[2]-1), \
                         random.randint(room.bounds[1]+1,room.bounds[1]+room.bounds[3]-1)
                _type=random.choice(roomtype[2])
                self[position]=_type
                room.specialobjects.append((position,_type))
                #print "PLACED A SPECIAL OBJECT"
            if tries>MAXTRIES:
                #print "3}FAILED GENERATING MORE ROOMS"
                #print "FILLING ROOMS..."
                return False

            thispath=[]
            if len(self.rooms)>0:
                minroom=min(self.rooms,key=lambda r2: room.distance(r2))
                #print "FINDING PATH (OUTSIDE)"
                thispath=self.findpath(room.center(),minroom.center(),(room,minroom))
                #print "2}FOUND A PATH"
            if isinstance(thispath,list):
                self.rooms.append(room)
                self.allpaths.extend(thispath)
            return True
    def finish(self):
        for i in self.allpaths:
            self[i]=random.choice(self.objectdefinitions["paths"])
        for room in self.rooms:
            
            for x in range(room.bounds[0],room.bounds[0]+room.bounds[2]+1):
                for y in range(room.bounds[1],room.bounds[1]+room.bounds[3]+1):
                    if x==room.bounds[0] or x==room.bounds[0]+room.bounds[2] or \
                       y==room.bounds[1] or y==room.bounds[1]+room.bounds[3]:
                        if self[x,y]==0 or ((((self[x,y+1] in tuple(itertoolschain(*room.doortype)) and (
                                self[x-1,y+1] in self.objectdefinitions["paths"] or
                                self[x+1,y+1] in self.objectdefinitions["paths"])) or
                                (self[x,y-1] in tuple(itertoolschain(*room.doortype)) and (
                                self[x-1,y-1] in self.objectdefinitions["paths"] or
                                self[x+1,y-1] in self.objectdefinitions["paths"])) or
                                (self[x-1,y] in tuple(itertoolschain(*room.doortype)) and (
                                self[x-1,y+1] in self.objectdefinitions["paths"] or
                                self[x-1,y-1] in self.objectdefinitions["paths"])) or
                                (self[x+1,y] in tuple(itertoolschain(*room.doortype)) and (
                                self[x+1,y+1] in self.objectdefinitions["paths"] or
                                self[x+1,y-1] in self.objectdefinitions["paths"]))))):
                            if len(room.walltype)==1:
                                self [x,y]=random.choice(room.walltype[0])
                            elif len(room.walltype)==4:
                                inx=0
                                if (room.bounds[0]==x) or (x==room.bounds[0]+room.bounds[2] and room.bounds[1]+room.bounds[3]!=y):
                                    inx|=1
                                if (room.bounds[1]==y and room.bounds[0]!=x) or (y==room.bounds[1]+room.bounds[3]):
                                    inx|=2
                                if (room.bounds[1]+room.bounds[3]==y and room.bounds[0]==x):
                                    inx=0
                                self [x,y]=random.choice(room.walltype[inx])
                        
                        else:
                            if x==room.bounds[0] or x==room.bounds[0]+room.bounds[2]:
                                self [x,y]=random.choice(room.doortype[0])
                            elif y==room.bounds[1] or y==room.bounds[1]+room.bounds[3]:
                                self[x,y]=random.choice(room.doortype[1])
                            room.doors.append((x,y))
                    else:
                        
                        self [x,y]=random.choice(room.floortype)
            for i in room.specialobjects:
                if room.instersects(i[0]):
                    self[i[0]]=i[1]
                else:
                    #print "2} ERROR, failed to place a object ",i[1]
                        
                    pass 
                    #print "FOUND FLOORTYPE"
        for room in self.rooms:
            for door in room.doors:
                remove=True
                for o in getadjacent(door,self.size):
                    if self[o] in self.objectdefinitions["paths"]:
                        remove=False
                if remove:
                    
                    self[door]=random.choice(room.walltype[0]) #----------------------------------------------------------<<<<<<MAKES GPAHICS BUG
                    #print "FAUlTY DOOR FOUND, FIXING... ",door,"STATE II"
        for coords in self.allpaths:
            fix=True
            for j in getadjacent(coords, self.size, False, True, True):
                if not j in self.allpaths:
                    fix=False
            if fix and self[coords] in self.objectdefinitions["paths"]:
                self[coords]=0
        objects=[]
        for i in self.objectdefinitions["1perdungeon"]:
            room=random.choice(tuple(i for i in self.rooms if not i.special))
            position=(random.randint(room.bounds[0]+1,room.bounds[0]+room.bounds[2]-1),
                      random.randint(room.bounds[1]+1,room.bounds[1]+room.bounds[3]-1),
                      self.dlevel)
            if i[1]=="TILE":
                self[position[:-1]]=i[0]
            elif i[1]=="OBJ":
                objects.append((position,i[0]))
                assert len(position)==3
                #self[position]=5
            else:
                raise ValueError("member 1perdungeon in objectdefinitions has a invalid value: ",str(i[1])," should be TILE or OBJ")
            #print "GENERATED SPECIAL OBECT",i[0]
        #print "FINISHED GENERATING ROOM!"
        print "THE OBJECTS ARE",objects
        return objects
                    
    def findpath(self,pointa,pointb,ignorerooms=[],cleanup=True):
        amountbacktracked=0
        didbacktracking=False
        #print "FINDING PATH FROM",pointa,pointb
        walkposition=tuple(pointa[:])
        points=[]
        pointstoavoid=[]
        pointb=tuple(pointb)
        reasons=[None,None,None,None]
        while walkposition!=pointb:
            direction=[0,0]
            if walkposition[0]<pointb[0]:
                direction[0]=1
            elif walkposition[0]>pointb[0]:
                direction[0]=-1
            else:
                direction[0]=0
                #print "DIRECTION 0 EQUALS 0"
            if walkposition[1]<pointb[1]:
                direction[1]=1
            elif walkposition[1]>pointb[1]:
                direction[1]=-1
            else:
                #print "DIRECTION 1 EQUALS 0"
                direction[1]=0
            for i in (direction[0],0),(0,direction[1]):
                nwalk=(walkposition[0]+i[0],walkposition[1]+i[1])
                if self[nwalk] in self.objectdefinitions["paths"]:
                    self.walkposition=nwalk
                    points.append(walkposition)
                    #print "alternated"
            relpts=[(direction[0],0),(0,direction[1])]
            if random.randint(0,10)==1:
                random.shuffle(relpts)
            for i in (relpts+[(-direction[1],0),(0,-direction[0]),
                      (0,direction[0]),(direction[1],0)]):
                nwalk=(walkposition[0]+i[0],walkposition[1]+i[1])
                #if i!=(direction[0],0):
                    #print "i==",i
                #print "",
                ok=True
                #for r in self.rooms:
                #    if (r not in ignorerooms) and r.instersects(nwalk):
                #        ok=False
                #        reasons.pop(0)
                #        reasons.append("INTERSECTS WITH ROOM")
                for r in self.rooms:
                    if r.iscorner(nwalk):
                        ok=False
                        reasons.pop(0)
                        reasons.append("Is a corner") 
                if nwalk in points:
                    reasons.pop(0)
                    reasons.append("INTERSECTS WITH TAIL")
                    ok=False
                elif nwalk in pointstoavoid:
                    reasons.pop(0)
                    reasons.append("THIS POINT IS MARKED: AVOID")
                    ok=False
                if i==(0,0):
                    reasons.pop(0)
                    reasons.append("ZERO, ZERO")
                    ok=False
                if ok:
                    amountbacktracked=0
                    walkposition=nwalk
                    if nwalk[0]==pointb[0]:
                        #print "REACHED X"
                        pass
                    if nwalk[1]==pointb[1]:
                        #print "REACHED Y"
                        pass
                    break
                else:
                    #print '2}not ok'
                    pass
                if not (0<walkposition[0]<self.size[0]) or \
                   not (0<walkposition[1]<self.size[1]):
                    #print "2} RAN OUTSIDE"
                    return False
            if not ok:
                #print "not ok"
                
                amountbacktracked+=1
                #if not didbacktracking:
                    
                #    print "3} ERROR, BACKTRACKING", reasons
                didbacktracking=True
                
                if amountbacktracked>100:
                    return False
                pointstoavoid.append(walkposition)
                if walkposition in points:
                    points.remove(walkposition)
                walkposition=points[-1]
                #points.remove(points[-1])
            else:    
                points.append(walkposition)
            self.walkposition=walkposition
            self.points=points
        if didbacktracking and cleanup:
            otherpoints=reversed(points)
            oldpoints=points
            points=[]
            index=0
            while len(points)>0 and points[-1]!=pointb:
                point=oldpoints[index]
                index=-1
                for i in getadjacent(point,random=False):
                    if i in oldpoints and not i in points:
                        reversedindex=otherpoints.index(i)
                        index=len(oldpoints)-reversedindex
                if index:
                    points.append(oldpoints[index])
                else:
                    #print "1} FALED TO OPTIMiZE"
                    return oldpoints
                
                index+=1
        if (not points) or points[-1]!=pointb:
            return False
        else:
            pass
            #for i in points:
                
                #self[i]=self.objectdefinitions["paths"][0]
        return points
            #print "finished a room"
