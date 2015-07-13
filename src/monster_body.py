'''
Created on 31 dec. 2014

@author: Maurits
'''

#EXPLANATION OF COMBAT RESISTANCE:
#Resistance is usually a tuple like this:
#(phisical, Ellectrical, Laser, heat, cold, radioactive, bio/poison, gas)
import random, math, itertools
import items
import generator
from constants import *

class CombatOnlyBody(object):
    #VARIABLES NEEDED:
    """
    This is a partial class that can be inherited from to get accsess to the default "Attack" method
    self
    self.size
    self.max_attack_height_ratio
    self.target
    self.getstat
    self.mind
    self.weapon_slots
    self.name
    self.mind.name
    """
    def attack(self, other, weapon=None, personal_pron=True):
        
        
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
            if weapon or self.mind.equipment[self.weapon_slots[0]]:
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
                if damage[i]!=0:
                    other.body.dodamage(hit,damage[i],i,self.name)
            if personal_pron:
                self.mind.say("you hit the "+other.name+"'s "+hit)
                other.say("the "+self.getname()+" hits your "+hit)
            else:
                string="the "+self.getname()+" hits the "+other.name+"'s "+hit
                self.mind.say(string)
                other.say(string)
            if otherbody.health<0:
                if personal_pron:
                    self.mind.say("you kill the "+other.name)
                    self.mind.add_xp("level",other.getstat("level"))
                else:
                    self.mind.say("the "+self.getname()+" kills the "+self.body.name)
            self.mind.add_xp("accuracy",1)
        else:
            if personal_pron:
                self.mind.say("you miss the "+other.name)
                other.say("the "+self.getname()+" misses")
            else:
                string=("the "+self.getname()+" misses the "+other.name)
                self.mind.say(string)
                other.say(string)
            other.add_xp("constitution",1)
            
    
    def getname(self):
        return self.mind.name
class HumanBody(CombatOnlyBody):
    '''
    A base body that should be inherited from by all monster bodies
    '''
    
    def updatemaxhealth(self):
        
        self.maxhealth=(self.getstat("constitution")+2)**2
    
    drops=[(1,"meat")]
    weapon_slots=["right hand"]
    
    def drop(self):
        itms=list(itertools.chain(*self.mind.inventory.values()))
        
        for q in self.mind.equipment:
            if self.mind.equipment[q]:
                itms.append(self.mind.equipment[q])
        #print itms
        for itm in itms:
            itm.position=self.mind.position[:]
            
        itms.extend(self.world.itemPicker.fastItemByName(i[1], self.mind.position[:], self.world, self.mind.cage) for i in self.drops if i[0]>random.random())
        self.world.objects.extend(itms)
    def __init__(self, world, imagename="hero.png", name="human", speed=100, combatMap={}
                 ):
        '''
        Constructor
        '''
        self.world=world
        self.target="ribs"
        self.maxhealth=10
        self.attack_zones=combatMap
        self.armor_slots=set()
        for i in self.attack_zones.values():
            self.armor_slots.add(i[5])
        
        #print "self.armor_slots",self.armor_slots
        self.health=self.maxhealth #I can't use the other method yet
        self.speed=speed
        self.imagename=imagename
        self.name=name
    def recalculateEverything(self):
        self.updatemaxhealth()
        self.updatemaxweight()
    
    ratios={"level":1,"accuracy":1,"constitution":1,"strength":1}
    size=100
    name="human"
    max_attack_height_ratio=1.25
    def get_visible(self):
        if self.mind.advanced_visibility_check:
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
            try:
                d=damage*self.attack_zones[region][4][damagetype]
            except IndexError:
                raise IndexError(self.attack_zones[region],damagetype)
            try:
                if countarmor and self.attack_zones[region][5] and self.mind.equipment[self.attack_zones[region][5]]:
                    bl=self.mind.equipment[self.attack_zones[region][5]].defence[damagetype]
                    
                    #print "blocked "+str(bl)
                    
                    d*=bl
            except ImportError as ex:
                raise ex
            except KeyError as ex:
                print region,damage,damagetype,message,countarmor
                raise KeyError("Found \'"+str(ex.args[0])+"\' expected one of "+str(self.mind.equipment.keys()))
            self.health-=d
            if self.health<0:
                self.mind.kill(message)
                #kilowicking
        else:
            pass
    
    
class lizard(HumanBody):
    name="lizard"
    image_name="lizzard.png"
    advanced_visibility_check=False
    attack_zones={"left foot":     [0,0,  13,9,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0  ),None],
                  "right foot":    [86,0, 13,9,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0  ),None],
                  "left leg":      [13,7, 28,17,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "right leg":     [71,7, 28,17,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "left shoulder": [25,15,9, 12,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "right shoulder":[66,15,9, 12,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None],
                  "head":          [33,9, 33,25,(3,  1,   2,  1,  1,  1,    1,  1 ),None],
                  "tail":          [39,35,23,31,(0.5,0.5, 0.5,0.5,0.5,0.5,  0,  0 ),None]
                  }
    size=56
    max_attack_height_ratio=1.0
##@getitembyname.itemRandomizer.fast_register_monster("CPP agent", 1, 0, 5, starting_inventory=("iron helmet",))
##class Agent(HumanBody):
##    name="CPP agent"
##    image_name="agent.png"
##    advanced_visibility_check=False
##    drops=[(0.5,"time book"),(0.5,"key")]+HumanBody.drops
##    ratios=HumanBody.ratios.copy()
##    ratios["constitution"]=3
##@getitembyname.itemRandomizer.fast_register_monster("archer", 5, 0, 5, starting_inventory=("iron helmet",))
##class Archer(HumanBody):
##    name="archer"
##    image_name="archer.png"
##    advanced_visibility_check=False