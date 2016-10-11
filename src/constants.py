'''
Created on 26 jan. 2015

@author: Maurits
'''

from pygame.locals import *

TS_EMPTY = 0  # BLANK
TS_WALL_BOTTOM = TS_EMPTY + 1  # 1
TS_WALL_LEFT = TS_WALL_BOTTOM + 1  # 2
TS_WALL_RIGHT = TS_WALL_LEFT + 1  # 3
TS_WALL_TOP = TS_WALL_RIGHT + 1  # 4
TS_FLOOR_NORMAL = TS_WALL_TOP + 1  # 5
TS_FLOOR_SPECIAL = TS_FLOOR_NORMAL + 1  # 6
TS_DOOR_OPEN_LEFT = TS_FLOOR_SPECIAL + 1  # 7
TS_DOOR_OPEN_RIGHT = TS_DOOR_OPEN_LEFT + 1  # 8
TS_DOOR_LEFT = TS_DOOR_OPEN_RIGHT + 1  # 9
TS_DOOR_RIGHT = TS_DOOR_LEFT + 1  # 10
TS_PATH_1 = TS_DOOR_RIGHT + 1  # 11
TS_PATH_2 = TS_PATH_1 + 1  # 12
TS_PATH_3 = TS_PATH_2 + 1  # 13
TS_PAPRI = TS_PATH_3 + 1  # 14
TS_GREEN_FLOOR_1 = TS_PAPRI + 1  # 15
TS_GREEN_FLOOR_2 = TS_GREEN_FLOOR_1 + 1  # 16
TS_GREEN_FLOOR_3 = TS_GREEN_FLOOR_2 + 1  # 17
TS_GREEN_WALL_1 = TS_GREEN_FLOOR_3 + 1  # 18
TS_GREEN_WALL_2 = TS_GREEN_WALL_1 + 1
TS_LOCKED_DOOR_LEFT = TS_GREEN_WALL_2 + 1  # 20
TS_LOCKED_DOOR_RIGHT = TS_LOCKED_DOOR_LEFT + 1
TS_WATER_POOL = TS_LOCKED_DOOR_RIGHT + 1
TS_STAIRS_UP = TS_WATER_POOL + 1  # 21
TS_STAIRS_DOWN = TS_STAIRS_UP + 1  # 23

door_pairs = {TS_DOOR_OPEN_LEFT: TS_DOOR_LEFT, TS_DOOR_OPEN_RIGHT: TS_DOOR_RIGHT}
door_pair_reverse = {v: k for k, v in door_pairs.iteritems()}
door_pair_lock = {TS_LOCKED_DOOR_RIGHT: TS_DOOR_RIGHT, TS_LOCKED_DOOR_LEFT: TS_DOOR_LEFT}
WALLS = [TS_EMPTY, TS_WALL_BOTTOM, TS_WALL_RIGHT, TS_WALL_LEFT, TS_WALL_TOP, TS_DOOR_LEFT,
         TS_DOOR_RIGHT, TS_GREEN_WALL_1, TS_GREEN_WALL_2, TS_LOCKED_DOOR_LEFT, TS_LOCKED_DOOR_RIGHT]

STAIRS = {TS_STAIRS_UP: (-1, "UP"), TS_STAIRS_DOWN: (1, "DOWN")}

DOORS = [TS_DOOR_LEFT, TS_DOOR_RIGHT, TS_LOCKED_DOOR_LEFT, TS_LOCKED_DOOR_RIGHT]
# GENERAL
ITM_MONSTER = 0
ITM_ITEM = 1
# ITEM BASIC TYPES
ITM_FOOD = 2
ITM_WEAPON = 3
ITM_ARMOR = 4
ITM_POTION = 5
ITM_CONTAINER = 6
ITM_UTIL = 7
# MONSTER BASIC TYPES
ITM_HUMANOID = 8

itm_name_to_number = {"ITM_MONSTER": ITM_MONSTER, "ITM_ITEM": ITM_ITEM, "ITM_FOOD": ITM_FOOD, "ITM_WEAPON": ITM_WEAPON,
                      "ITM_ARMOR": ITM_ARMOR, "ITM_POTION": ITM_POTION,
                      "ITM_CONTAINER": ITM_CONTAINER, "ITM_UTIL": ITM_UTIL, "ITM_HUMANOID": ITM_HUMANOID}

# REMEMBER TO ADD TO REVERSE DICTONARY
FLAG_BURDENED = 0
FLAG_FULL = 1
FLAG_FULL_2 = 2
FLAG_HUNGRY = 3
FLAG_HUNGRY_2 = 4
FLAG_FAST = 5
FLAG_FAST_2 = 6

flag_uncode = {0: "burdened", 1: "full", 2: "very full", 3: "hungry", 4: "very hungry", 5: "fast", 6: "very fast"}

# Types------------------------+
TYPE_INT = 0  # |
TYPE_STRING = 1  # |
TYPE_FLOAT = 2  # |
TYPE_BOOL = 3  # |
TYPE_TUPLE_INT = 4  # |
TYPE_TUPLE_STRING = 5  # |
TYPE_TUPLE_FLOAT = 6  # |
TYPE_COMBAT_MAP = 7  # |
TYPE_VAR_NAME = 8  # |
TYPE_VAR_WORLD = 9  # |
TYPE_VAR_CAGE = 10  # |
TYPE_VAR_POSITION = 11  # |
TYPE_IMAGE = 12  # |
TYPE_ATTRNAME_AS_HOLDER = 13  # |
TYPE_ITEM_PROB = 14  # |
TYPE_DICT_POSITION = 15
# ------------------------------+



# SETTINGS
MAXTRIES = 100
GRIDSIZE_X = 100
GRIDSIZE_Y = 100

# Random Flags
RE_NORMAL_ARGS = 1
RE_STATIC_ARGS = 2


def emergencyReturn(function, r):
    def subfunc(*args):
        o = function(*args)
        if o:
            return o
        else:
            return r

    return subfunc


class RandomError(ValueError):
    pass


class Holder(object):
    def __init__(self, what):
        self.what = what

    def __getattribute__(self, attr):
        return object.__getattribute__(self, "what")

    def __setattr__(self, attr, value):
        object.__setattr__(self, "what", value)

    def __str__(self):
        return str(self.what)
