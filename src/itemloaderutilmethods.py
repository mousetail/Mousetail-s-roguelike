'''
Created on 25 jun. 2015

@author: Maurits
'''

import player_input
import items
import itertools
from constants import *



def monsterMaker(body, pobj=player_input.MonsterObject):
    def internal1(name,stats):
        def internal2(position,world,cage,safemode=False,returnbody=False):
            
            bdy=body(world, stats["image_name"],name,int(stats["speed"]))
            bdy.attack_zones={}
            bdy.armor_slots=[]
            bdy.advanced_visibility_check=stats["advanced visibility check"]=="True"
            for key, value in stats["attack_zones"].items():
                pass
                dimentions=(int(value["dimentions"][i]) for i in ("left","top","width","height"))
                damage=(tuple(float(value["damage"][i]) for i in ("phis","ele","las","hea","ice","rad","bio","gas")),)
                slot=(value["slot"],)
                bdy.attack_zones[key]=tuple(itertools.chain(dimentions,damage,slot))
                if slot not in bdy.armor_slots:
                    bdy.armor_slots.append(slot[0])
            if not returnbody:
                obj=pobj(position,bdy,cage,world)
                obj.clearAndRefreshEquipment()
            
                return obj
            else:
                return bdy
        return internal2
    return internal1
def BasicitemFuncMaker(itemCls=items.Item,extrastats=(("weight",TYPE_INT),("fake name",TYPE_STRING),("fake pname",TYPE_STRING),("range",TYPE_INT))):
    """for StaticObject and Item
    attrs used:
    "image name",
    "pname",
    "range"
    "weight"
    """
    def internal1(name, stats):
        def internal2(position,world,cage,safemode=False,returnbody=False):
            if returnbody:
                raise ValueError("returnbody argument only for monsters, "
                "\""+name+"\" is not a monster")
            args=[]
            for i in extrastats:
                
                if i[1]==TYPE_STRING:
                    args.append(stats[i[0]])
                elif i[1]==TYPE_INT:
                    args.append(int(stats[i[0]]))
                elif i[1]==TYPE_FLOAT:
                    args.append(float(stats[i[0]]))
                elif i[1]==TYPE_TUPLE_INT:
                    args.append(tuple(int(i) for i in stats[i[0]].split(",")))
                elif i[1]==TYPE_TUPLE_FLOAT:
                    args.append(tuple(float(i) for i in stats[i[0]].split(",")))
                elif i[1]==TYPE_TUPLE_STRING:
                    args.append(tuple(i for i in stats[i[0]].split(",")))
                else:
                    raise ValueError(i[1])
            obj= itemCls(position,cage.lookup(stats["image_name"]),cage,world,name,stats["pname"],*args)
            return obj
        return internal2
    return internal1