'''
Created on 8 okt. 2014

@author: Maurits
'''
import datetime
from itertools import product as itertoolsproduct

adjacent=[(-1,0),(0,-1),(1,0),(0,1)]



def getadjacent(coords, gridsize=(100,100), randomorder=False):
    if randomorder:
        random.shuffle(adjacent)
    for i in adjacent:
        n=coords[0]+i[0],coords[1]+i[1]
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
    def __getitem__(self,item):
        if item[0]<0 or item[0]>self.rowsize or item[1]<0:
            raise IndexError(item)
        try:
            item=self.data[item[1]*self.rowsize+item[0]]
        except IndexError:
            raise IndexError(item)
        return item
    def __setitem__(self,item,setto):
        try:
            self.data[item[1]*self.rowsize+item[0]]=setto
        except IndexError:
            raise IndexError(item)
        #print self[item]
    def __iter__(self):
        for i in range(self.rowsize):
            for j in range(self.size[1]):
                yield i,j
                
class Generator(Grid):
    '''
    a generator
    '''
    def __init__(self, size, objectdefinitions=None):
        if objectdefinitions is None:
            self.objectdefinitions={"empty":0,
                               "roomtypes":((1,1,(12,),8),(1,2,(),8),(2,3,(),8)),
                               "walltypes":{1:(1,2),2:(16,17)},
                               "floortypes":{1:(3,4),2:(5,6),3:(15,14,13)},
                               "specialobjectclasses":{1:12},
                               
                               }
            
            #print self.objectdefinitions
        else:
            
            self.objectdefinitions=objectdefinitions
            print self.objectdefinitions,"2"
        print self.objectdefinitions
        Grid.__init__(self, size, self.objectdefinitions["empty"])

    def generate(self):
        numrooms=len(self.data)//256
        rooms=[]
        print "0}GENERATING ROOMS"
        for i in range(numrooms):
            ok=False
            tries=0
            while not ok:
                x=random.randint(1,self.rowsize-1)
                y=random.randint(1,self.size[1]-1)
                width=random.randint(8,32)
                height=random.randint(8,32)
                roomtype=random.choice(self.objectdefinitions["roomtypes"])
                walltype=self.objectdefinitions["walltypes"][roomtype[0]]
                floortype=self.objectdefinitions["floortypes"][roomtype[1]]
                doortype=roomtype[3]
                specialobjects=roomtype[2]
                #print specialobjects
                #print floortype
                room=[x,y,width,height,floortype,walltype,specialobjects,doortype]
                ok=True
                if (room[0]+room[2]+4)>self.rowsize or (room[1]+room[3]+4)>(len(self.data)//self.rowsize):
                    ok=False
                for room2 in rooms:
                    if ((room[0]<room2[0]+room2[2]+3) and #room.right>room2.x and room.x<room2.right
                        (room2[0]<room[0]+room[2]+3) and
                        (room[1]<room2[1]+room2[3]+3) and
                        (room2[1]<room[1]+room[3]+3)):
                        #print room,room2
                        ok=False
                if not ok:
                    tries+=1
                    #print "tries: ",tries
                if tries>1000:
                    print "1}FAILED TO POSITION AFTER",tries,"TRIES"
                    print "2}reached max capacity for rooms"
                    print "2}for this grid size"
                    break
            if tries<=1000:
                print "generating room {0}/{1}".format(i+1,numrooms)
                rooms.append(room)
                
                dooroptions=[]
                for i in range(room[0],room[0]+room[2]+2):
                
                    
                    for j in range(room[1],room[1]+room[3]+2):
                        ok=False
                        if (i==room[0] or i==room[0]+room[2]+1 and #x position
                            j==room[1] or j==room[1]+room[3]+1):
                            self[i,j]=random.choice(room[5])
                        elif (i==room[0] or i==room[0]+room[2]+1 or #x position
                            j==room[1] or j==room[1]+room[3]+1):
                            self[i,j]=random.choice(room[5])
                            dooroptions.append((i,j))
                        else:
                            self[i,j]=random.choice(room[4])
                self[random.choice(dooroptions)]=8
                if (random.randint(0,4)==0) and len(room[6])>0:
                    place=tuple(random.randint(room[i]+1,room[i]+room[i+2]-1) for i in range(2))
                    print "1}placed a special object!"
                    self[place]=random.choice(room[6])
            else:
                break
        
        print "Len(rooms)=",len(rooms)           
            #print [x,y,width,height,floormats]
        print "0}Connecting rooms!"
        lasttime=datetime.datetime.now()
        isolations=[]
        toconnects=[]
        for room in rooms:
            isolations.append([room])
        while len(isolations)!=1:
            iso1=random.choice(isolations)
            iso2=random.choice(isolations)
            combination=min(itertoolsproduct(iso1,iso2),key=distance)
            toconnects.append(combination)
            isolations.remove(iso2)
            for i in iso2:
                iso1.append(i)
        print toconnects
        j=0
        for i in toconnects:
            print "Running A* ",j,"/",len(toconnects)
            j+=1
            self.astar([(i[0][0]+1),i[0][1]+1], 
                       [(i[1][0]+1),i[1][1]+1])
            
            
                    
                    
    def upgrade_point(self,coords):
        x,y=coords
        if self[x,y] in (1,2,16,17):
            self[x,y]=8 #turn wall into door
        elif self[x,y]==0:
            self[x,y]=random.choice((9,10,11))
        elif self[x,y]==9 or self[x,y]==10 or self[x,y]==11:
            self[x,y]=random.choice((9,10,11))
        elif self[x,y] in (3,4,5,6,13,14,15):
            #self[x,y]=9
            pass
        elif self[x,y]==8:
            self[x,y]=8
        else:
            print "3} passing threw room",self[x,y]
    def upgrade_line(self,x,y,xsl,ysl,length):
        self.lastpoint=self[x,y]
        for i in range(length):
            if self.lastpoint==8 and (self[x,y]==1 or self[x,y]==2 or self[x,y]==8):
                self[x,y]=1
                x-=xsl
                y+=ysl
                break
            self.upgrade_point([x, y])
            
            self.lastpoint=self[x,y]
            if (self[x+ysl,y+xsl]==9 or self[x+ysl,y+xsl]==10) and i>2:
                x=x+ysl
                y=y+xsl
            elif (self[x-ysl,y-xsl]==9 or self[x-ysl,y-xsl]==10) and i>2:
                x=x-ysl
                y=y-xsl
            else:
                x+=xsl
                y+=ysl
        return x,y
    def astar(self, pointa, pointb, weights=None,function="DEFAULTS TO  UPGRADE POINT"):
        starttime=datetime.datetime.now()
        if function=="DEFAULTS TO  UPGRADE POINT":
            function=self.upgrade_point
        if weights==None:
            allowed=[0,5,3,4,5,6,8,
                     9,10,11,15,14,13]
            not_allowed=[1,2,16,17,7]
                    #{0:5, #empty square
                    # 1:80,2:77,16:80,17:80,#walls
                    # 3:2,4:2,5:3,6:3, #floor
                    # 7:512,#corner
                    # 8:1,#door
                    # 9:1,10:1,11:1,#pathway
                    # 12:5,
                    # 13:1,
                    # 14:1,
                    # 15:1
                    # }
        weightsgrid=Grid([self.rowsize, self.size[1]],-1)
        weightsgrid[pointa]=1
        tries=0
        allreadydone=[]
        edge=[pointa]
        nedge=[]
        while weightsgrid[pointb]==-1 and tries<=1000:
            tries+=1
            nedge[:]=[]
            for i in edge:
                for j in getadjacent(i):
                    if not j in allreadydone and not j in edge and not j in nedge and self[j] in allowed:
                        weightsgrid[j]=weightsgrid[i]+1
                        nedge.append(j)
                        #print "Didn't run into wall"
                    elif not(self[i] in allowed):# and self[i] in allowed):
                        print "1}Ran into wall! ",self[i]
                
                    allreadydone.append(i)
            edge[:]=nedge
            if tries%80==0:
                print tries
                #for i in edge:
                #    if i in allreadydone:
                #        print i
        if tries>=len(self.data):
            print "1}Failed finding end point after",tries,"tries"
            return []
        print "Finished height grid! took {0:0>2}s, {1:0>3}ms".format((datetime.datetime.now()-starttime).seconds,(datetime.datetime.now()-starttime).microseconds//1000)
        
        walkposition=tuple(pointb)
        l=None
        tries=0
        if not function:
            l=[]
            function=l.append
        while walkposition!=tuple(pointa) and tries<len(self.data):
            try:
                walkposition=min(getadjacent(walkposition,randomorder=True,gridsize=self.size),
                             key=lambda x: weightsgrid[x] if weightsgrid[x]!=-1 else 8388608)
                #weightsgrid[walkposition]=8388608
                if weightsgrid[walkposition]==-1:
                    print "1} Ran into unexplored teritory!", walkposition
                    break
            except IndexError:
                print "1} Index Error: ",walkposition
                
            #weightsgrid[walkposition]=8388608
            function(walkposition)
            weightsgrid[walkposition]*=2
            tries+=1
            #print tries
        if tries>=len(self.data):
            print "1} FAILED, took to long to walk"
        self.weightsgrid=weightsgrid
        return l
        #notallconnected=True
        #while notallconnected:
           
                    
                    
                    
            #print "finished a room"
                    
        