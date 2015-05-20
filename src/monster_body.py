'''
Created on 31 dec. 2014

@author: Maurits
'''

#EXPLANATION OF COMBAT RESISTANCE:
#Resistance is usually a tuple like this:
#(phisical, Ellectrical, Laser, heat, cold, radioactive, bio/poison, gas)
import random, math, itertools
import items
import getitembyname, generator
from constants import *

class HumanBody(object):
    '''
    A base body that should be inherited from by all monster bodies
    '''
    speed=100
    image_name="hero.png"
    #Basic pattern: bodypart:distance from floor,left,width,height,damage_ratio,
    #damage ration is #(phisical, Ellectrical, Laser, heat, radioactive, bio/poison, gas)
                                                #ph  ele  l   h   c   rad   po  g,  Armor slot
    
    attack_zones={"hair":          [30,96,20,4 ,(0,  0.5, 0,  0,  0,  0.25, 0,  0 ),"head"],
                  "head":          [30,79,20,16,(2,  1,   2,  1,  1,  1,    1,  1 ),"head"],
                  "neck":          [37,70,7, 8, (2,  1,   2,  1,  1,  1,    0.1,0 ),"head"],
                  "ribs":          [31,53,18,16,(1,  1,   1,  1,  1,  1,    0.1,0 ),"body"],
                  "heart":         [44,49, 5, 5,(2,  3,   2,  1,  1,  1.5,  0,  0 ),"body"],
                  "stomach":       [31,35,18,14,(1,  1,   1,  1,  1,  1,    0.1,0 ),"body"],
                  "right shoulder":[28,68, 4, 3,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"body"],
                  "left shoulder": [50,68, 4, 3,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"body"],
                  "left arm":      [27,40, 4,27,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"body"],
                  "right arm":     [50,40, 4,27,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"body"],
                  "left hand":     [27,35, 4, 5,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"hands"],
                  "right hand":    [50,35, 4, 5,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"hands"],
                  "right foot":    [29, 0,10, 4,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"feet"],
                  "left foot":     [43, 0,10, 4,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"feet"],
                  "left leg":      [47, 5, 4,31,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"legs"],
                  "right leg":     [34, 5, 4,31,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),"legs"],
                  }
    armor_slots=["head","body","legs","hands","feet"]
    weapon_slots=["left hand","right hand"]
    def updatemaxhealth(self):
        
        self.maxhealth=(self.getstat("constitution")+2)**2
    
    drops=[(1,"meat")]
    def drop(self):
        itms=list(itertools.chain(*self.mind.inventory.values()))
        
        for q in self.mind.equipment:
            if self.mind.equipment[q]:
                itms.append(self.mind.equipment[q])
        #print itms
        for itm in itms:
            itm.position=self.mind.position[:]
            
        itms.extend(getitembyname.itemRandomizer.fastitembyname(i[1], self.mind.position[:], self.world, self.mind.cage) for i in self.drops if i[0]>random.random())
        self.world.objects.extend(itms)
    def __init__(self, mind, world):
        '''
        Constructor
        '''
        self.mind=mind
        self.world=world
        self.target="ribs"
        self.maxhealth=(self.mind.stats["constitution"]*self.ratios["constitution"]+2)**2 #I can't access the findmaxhealth method directly
        
        self.health=self.maxhealth #I can't use the other method yet
    ratios={"level":1,"accuracy":1,"constitution":1,"strength":1}
    size=100
    name="human"
    max_attack_height_ratio=1.25
    advanced_visibility_check=True
    def get_visible(self):
        if self.advanced_visibility_check:
            for i in self.mind.visible:
                if self.mind.visible[i]==2:
                    self.mind.visible[i]=1
        for room in self.world.grid.rooms:
            if room.instersects(self.mind.position):
                for x in range(room.bounds[0],room.bounds[0]+room.bounds[2]+1):
                    for y in range(room.bounds[1],room.bounds[1]+room.bounds[3]+1):
                        self.mind.visible[x,y]=2
        
        for i in generator.getadjacent(self.mind.position,self.world.grid_size,0,0,1):
            if self.world.grid[i] not in WALLS:# or self.world.grid[i] in DOORS:
                for j in generator.getadjacent(i,self.world.grid_size,0, 0, 1):
                    if self.world.grid[j] not in WALLS or self.world.grid[j] in DOORS:
                        self.mind.visible[j]=2
                self.mind.visible[i]=2
        
    def updatemaxweight(self):
        self.maxweight=17+(3**self.getstat("strength"))
    def update(self):
        self.health+=0.01
        if self.health>self.maxhealth:
            self.health=self.maxhealth
    def getstat(self, stat):
        return self.mind.getstat(stat)
    
    def dodamage(self, region, damage, damagetype, message, countarmor=True):
        if self.health>0:
            d=damage*self.attack_zones[region][4][damagetype]
            if countarmor and self.attack_zones[region][5] and self.mind.equipment[self.attack_zones[region][5]]:
                bl=self.mind.equipment[self.attack_zones[region][5]].defence[damagetype]
                
                #print "blocked "+str(bl)
                
                d*=bl
        
            self.health-=d
            if self.health<0:
                self.mind.kill(message)
                #kilowicking
        else:
            pass
    
    def attack(self, other, weapon=None):
        
        #TODO: find a inheritence safe-way to call this method when one member isn't a instance of the class
        #WONT RUN RIGHT NOW
        
        otherbody=other.body
        max_height=self.size*self.max_attack_height_ratio
        if self.target in otherbody.attack_zones and otherbody.attack_zones[self.target][1]<=max_height:
            target=self.target
        else:
            target=random.choice(otherbody.attack_zones.keys())
        target_center=[otherbody.attack_zones[target][0]+(otherbody.attack_zones[target][2]//2),
                       otherbody.attack_zones[target][1]+(otherbody.attack_zones[target][3]//2)]
        
        if target_center[1]>=max_height-3:
            target_center[1]=max_height-3
        rotation=random.random()*2*math.pi
        distance=(random.random()**2)*(100.0/(self.getstat("accuracy")))
        position=[target_center[0]+distance*math.cos(rotation),target_center[1]+distance*math.sin(rotation)]
        #REMOVE LATER
        otherbody.lastattackspot=position
        otherbody.lastdebspot=target_center
        otherbody.lasttarget=target
        #-------------
        hit=None
        for bodypart in otherbody.attack_zones:
            if otherbody.attack_zones[bodypart][0]<position[0]<(otherbody.attack_zones[bodypart][0]+otherbody.attack_zones[bodypart][2]) \
             and otherbody.attack_zones[bodypart][1]<position[1]<(otherbody.attack_zones[bodypart][1]+otherbody.attack_zones[bodypart][3]):
                hit=bodypart
        if hit:
            damage=[((self.getstat("level")+random.random()
                    *self.getstat("level"))),0,0,0,0,0,0,0]
            if self.mind.equipment[self.weapon_slots[0]]:
                if weapon==None:
                    sword=self.mind.equipment[self.weapon_slots[0]]
                else:
                    sword=weapon
                if isinstance(sword.damage,int) or isinstance(sword.damage,float):
                    damage[0]+=sword.damage*self.getstat("level")*random.random()
                else:
                    for i in range(len(sword.damage)):
                        damage[i]+=sword.damage[i]*self.getstat("level")*random.random()
            for i in range(len(damage)):
                other.body.dodamage(hit,damage[i],i,self.name)
            self.mind.say("you hit the "+other.name+"'s "+hit)
            other.say("the "+self.mind.name+" hits your "+hit)
            if otherbody.health<0:
                self.mind.say("you kill the "+other.name)
                self.mind.add_xp("level",other.getstat("level"))
            self.mind.add_xp("accuracy",1)
        else:
            self.mind.say("you miss the "+other.name)
            other.say("the "+self.mind.name+" misses")
            other.add_xp("constitution",1)
class lizard(HumanBody):
    name="lizard"
    image_name="lizzard.png"
    advanced_visibility_check=False
    attack_zones={"left foot":     [0,0,  13,9,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ), None],
                  "right foot":    [86,0, 13,9,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ), None],
                  "left leg":      [13,7, 28,17,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "right leg":     [71,7, 28,17,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "left shoulder": [25,15,9, 12,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "right shoulder":[66,15,9, 12,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "head":          [33,9, 33,25,(3,  1,   2,  1,  1,  1,    1,  1 ),None],
                  "tail":          [39,35,23,31,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None]
                  }
    size=56
    max_attack_height_ratio=1.0
@getitembyname.itemRandomizer.fast_register_monster("CPP agent", 1, 0, 5, starting_inventory=("iron helmet",))
class Agent(HumanBody):
    name="CPP agent"
    image_name="agent.png"
    advanced_visibility_check=False
    drops=[(0.5,"time book"),(0.5,"key")]+HumanBody.drops
    ratios=HumanBody.ratios.copy()
    ratios["constitution"]=3
