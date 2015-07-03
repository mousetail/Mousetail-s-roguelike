
import items
from itemloaderutilmethods import *
import weapons, potions, food, identifyer, containers
from constants import *

defs={"item":BasicitemFuncMaker(items.Item),
      "basic":BasicitemFuncMaker(items.StaticObject,()),
      "healing potion":BasicitemFuncMaker(potions.HealingPotion),
      "speed potion":BasicitemFuncMaker(potions.SpeedPotion),
      "weapon":BasicitemFuncMaker(weapons.Weapon,(("weight",TYPE_INT),("fake name",TYPE_STRING),("fake pname",TYPE_STRING),("range",TYPE_INT),("damage",TYPE_TUPLE_FLOAT))),
      "food":BasicitemFuncMaker(food.Food,(("weight",TYPE_INT),("fake name",TYPE_STRING),("fake pname",TYPE_STRING),("range",TYPE_INT),("nutrition",TYPE_INT))),
      "identifier":BasicitemFuncMaker(identifyer.Identifier)
      }

placestoloadfrom=[]