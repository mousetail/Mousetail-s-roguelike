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
def BasicitemFuncMaker(itemCls=items.Item,*extrastatslist):
    """for StaticObject and Item
    attrs used:
    "image name",
    "pname",
    "range"
    "weight"
    
    basic types=(("weight",TYPE_INT),("fake name",TYPE_STRING),("fake pname",TYPE_STRING),("range",TYPE_INT))
    """
    if len(extrastatslist)==0:
        extrastatslist=(RE_NORMAL_ARGS,)
    extrastats=[]
    for i in extrastatslist:
        if i==RE_NORMAL_ARGS:
            extrastats.extend((("weight",TYPE_INT),("fake name",TYPE_STRING),("fake pname",TYPE_STRING),("range",TYPE_INT)))
        else:
            extrastats.extend(i)
    
    def internal1(name, stats):
        def internal2(position,world,cage,safemode=False,returnbody=False):
            if returnbody:
                raise ValueError("returnbody argument only for monsters, "
                "\""+name+"\" is not a monster")
            args=[]
            kwargs={}
            for i in extrastats:
                itm=None
                if i[1]==TYPE_STRING:
                    itm=stats[i[0]]
                elif i[1]==TYPE_INT:
                    itm=int(stats[i[0]])
                elif i[1]==TYPE_FLOAT:
                    itm=float(stats[i[0]])
                elif i[1]==TYPE_TUPLE_INT:
                    itm=tuple(int(i) for i in stats[i[0]].split(","))
                elif i[1]==TYPE_TUPLE_FLOAT:
                    itm=tuple(float(i) for i in stats[i[0]].split(","))
                elif i[1]==TYPE_TUPLE_STRING:
                    itm=tuple(i for i in stats[i[0]].split(","))
                else:
                    raise ValueError(i[1])
                if len(i)==2:
                    args.append(itm)
                else:
                    kwargs[i[2]]=itm
                    #print "added argument: "+i[2]
            obj= itemCls(position,cage.lookup(stats["image_name"]),cage,world,name,stats["pname"],*args, **kwargs)
            return obj
        return internal2
    return internal1