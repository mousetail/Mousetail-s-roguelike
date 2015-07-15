
import items
from itemloaderutilmethods import *
import weapons, potions, food, identifyer, containers
from constants import *

defs={"item":BasicitemFuncMaker(items.Item),
      "basic":BasicitemFuncMaker(items.StaticObject,()),
      "healing potion":BasicitemFuncMaker(potions.HealingPotion),
      "speed potion":BasicitemFuncMaker(potions.SpeedPotion),
      "weapon":BasicitemFuncMaker(weapons.Weapon,RE_STATIC_ARGS,RE_NORMAL_ARGS,(("damage",TYPE_TUPLE_FLOAT),)),
      "food":BasicitemFuncMaker(food.Food,RE_STATIC_ARGS,RE_NORMAL_ARGS,(("nutrition",TYPE_INT,"nutrition"),)),
      "identifier":BasicitemFuncMaker(identifyer.Identifier),
      "container":BasicitemFuncMaker(containers.Container,RE_STATIC_ARGS,RE_NORMAL_ARGS,(("item capacity",TYPE_INT,"item_capacity"),("weight capacity",TYPE_INT,"weight_capacity"),
                                                                                         ("starting items",TYPE_ITEM_PROB,"startinginv")))
      }

placestoloadfrom=[]