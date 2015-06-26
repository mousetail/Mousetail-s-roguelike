'''
Created on 25 jun. 2015

@author: Maurits
'''

import player_input
import itertools

def monsterMaker(body, pobj=player_input.MonsterObject):
    def internal1(name,stats):
        def internal2(position,world,cage,safemode=False):
            obj=pobj(position,body,cage,world,int(stats["speed"]),name,safemode=safemode) #TODO: disable safemode
            obj.body.image_name=stats["image_name"]
            obj.body.speed=stats["speed"]
            obj.body.attack_zones={}
            obj.body.armor_slots=[]
            obj.body.advanced_visibility_check=stats["advanced visibility check"]=="True"
            for key, value in stats["attack_zones"].items():
                pass
                dimentions=(int(value["dimentions"][i]) for i in ("left","top","width","height"))
                damage=(tuple(float(value["damage"][i]) for i in ("phis","ele","las","hea","ice","rad","bio","gas")),)
                slot=(value["slot"],)
                obj.body.attack_zones[key]=tuple(itertools.chain(dimentions,damage,slot))
                if slot not in obj.body.armor_slots:
                    obj.body.armor_slots.append(slot[0])
            obj.clearAndRefreshEquipment()
            return obj
        return internal2
    return internal1