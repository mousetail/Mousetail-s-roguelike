'''
Created on 26 jan. 2015

@author: Maurits
'''
TS_EMPTY=0 #BLANK
TS_WALL_BOTTOM=TS_EMPTY+1
TS_WALL_LEFT=TS_WALL_BOTTOM+1
TS_WALL_RIGHT=TS_WALL_LEFT+1
TS_WALL_TOP=TS_WALL_RIGHT+1
TS_FLOOR_NORMAL=TS_WALL_TOP+1
TS_FLOOR_SPECIAL=TS_FLOOR_NORMAL+1
TS_DOOR_OPEN_LEFT=TS_FLOOR_SPECIAL+1
TS_DOOR_OPEN_RIGHT=TS_DOOR_OPEN_LEFT+1
TS_DOOR_LEFT=TS_DOOR_OPEN_RIGHT+1
TS_DOOR_RIGHT=TS_DOOR_LEFT+1
TS_PATH_1=TS_DOOR_RIGHT+1
TS_PATH_2=TS_PATH_1+1
TS_PATH_3=TS_PATH_2+1
TS_PAPRI=TS_PATH_3+1
TS_GREEN_FLOOR_1=TS_PAPRI+1
TS_GREEN_FLOOR_2=TS_GREEN_FLOOR_1+1
TS_GREEN_FLOOR_3=TS_GREEN_FLOOR_2+1
TS_GREEN_WALL_1=TS_GREEN_FLOOR_3+1
TS_GREEN_WALL_2=TS_GREEN_WALL_1+1
TS_LOCKED_DOOR_LEFT=TS_GREEN_WALL_2+1
TS_LOCKED_DOOR_RIGHT=TS_LOCKED_DOOR_LEFT+1
door_pairs={TS_DOOR_OPEN_LEFT:TS_DOOR_LEFT,TS_DOOR_OPEN_RIGHT:TS_DOOR_RIGHT}
door_pair_reverse={v:k for k,v in door_pairs.iteritems()}
door_pair_lock={TS_LOCKED_DOOR_RIGHT:TS_DOOR_RIGHT,TS_LOCKED_DOOR_LEFT:TS_DOOR_LEFT}
WALLS=[TS_EMPTY,TS_WALL_BOTTOM,TS_WALL_RIGHT,TS_WALL_LEFT,TS_WALL_TOP,TS_DOOR_LEFT,
       TS_DOOR_RIGHT,TS_GREEN_WALL_1,TS_GREEN_WALL_2,TS_LOCKED_DOOR_LEFT,TS_LOCKED_DOOR_RIGHT]


DOORS=[TS_DOOR_LEFT,TS_DOOR_RIGHT,TS_LOCKED_DOOR_LEFT,TS_LOCKED_DOOR_RIGHT]

ITM_MONSTER=0
ITM_ITEM=1
ITM_FOOD=2
ITM_WEAPON=3
ITM_ARMOR=4
ITM_POTION=5
ITM_CONTAINER=6
ITM_UTIL=7


#REMEMBER TO ADD TO REVERSE DICTONARY
FLAG_BURDENED=0
FLAG_FULL=1
FLAG_FULL_2=2
FLAG_HUNGRY=3
FLAG_HUNGRY_2=4
FLAG_FAST=5
FLAG_FAST_2=6

from pygame.locals import *

flag_uncode={0:"burdened",1:"full",2:"very full", 3:"hungry", 4:"very hungry", 5:"fast", 6: "very fast"}

#SETTINGS
MAXTRIES=100
GRIDSIZE_X=150
GRIDSIZE_Y=150

def emergencyReturn(function, r):
    def subfunc(*args):
        o=function(*args)
        if o:
            return o
        else:
            return r
    return subfunc

class RandomError (ValueError):
    pass