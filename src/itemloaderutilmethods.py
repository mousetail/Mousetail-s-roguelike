'''
Created on 25 jun. 2015

@author: Maurits
'''

import player_input
import items
import itertools
from constants import *



def monsterMaker(pobj, *args):
    bholder=Holder(None)
    bodyfunc=BasicitemFuncMaker(pobj,(("world",TYPE_VAR_WORLD),("image_name",TYPE_STRING),
                                      ("name",TYPE_VAR_NAME),("speed",TYPE_INT),("attack_zones",TYPE_COMBAT_MAP),("drops",TYPE_ITEM_PROB)),*args)
    mindfunc=BasicitemFuncMaker(player_input.MonsterObject,(("position",TYPE_VAR_POSITION),(bholder,TYPE_ATTRNAME_AS_HOLDER),("cage",TYPE_VAR_CAGE),("world",TYPE_VAR_WORLD),
                                                            ("advanced visibility check",TYPE_BOOL),("starting inventory",TYPE_ITEM_PROB)))
    def internal1(name,stats):
        bodyfuncint1=bodyfunc(name,stats)
        mindfuncint1=mindfunc(name,stats)
        def internal2(position,world,cage,safemode=False,returnbody=False):
            body=bodyfuncint1(position,world,cage,safemode)
            if returnbody:
                return body
            else:
                bholder.x=body
                mind=mindfuncint1(position,world,cage,safemode)
                return mind
        return internal2
    return internal1
"""
                        if slot not in bdy.armor_slots:
                            bdy.armor_slots.append(slot[0])
"""
            
def BasicitemFuncMaker(itemCls=items.Item,*extrastatslist):
    """for StaticObject and Item
    attrs used:
    "image name",
    "pname",
    "range"
    "weight"
    static types=(("position",TYPE_VAR_POSITION),("image_name",TYPE_IMAGE),("cage",TYPE_VAR_CAGE),("world",TYPE_VAR_WORLD))
    basic types=(("name",TYPE_VAR_NAME),("pname",TYPE_STRING),("weight",TYPE_INT),("fake name",TYPE_STRING),("fake pname",TYPE_STRING),
                               ("range",TYPE_INT))
    """
    if len(extrastatslist)==0:
        #print itemCls,extrastatslist,len(extrastatslist)
        extrastatslist=(RE_STATIC_ARGS,RE_NORMAL_ARGS,)
    elif len(extrastatslist)==1:
        print extrastatslist
    extrastats=[]
    for i in extrastatslist:
        if i==RE_NORMAL_ARGS:
            extrastats.extend((("name",TYPE_VAR_NAME),("pname",TYPE_STRING),("weight",TYPE_INT),("fake name",TYPE_STRING),("fake pname",TYPE_STRING),
                               ("range",TYPE_INT)))
        elif i==RE_STATIC_ARGS:
            extrastats.extend((("position",TYPE_VAR_POSITION),("image_name",TYPE_IMAGE),("cage",TYPE_VAR_CAGE),("world",TYPE_VAR_WORLD)))
        else:
            #print itemCls,i,len(extrastatslist)
            extrastats.extend(i)
    
    def internal1(name, stats):
        def internal2(position,world,cage,safemode=False,returnbody=False):
            if returnbody:
                raise ValueError("returnbody argument only for monsters, "
                "\""+name+"\" is not a monster")
            args=[]
            kwargs={}
            try:
                for i in extrastats:
                    itm=None
                    if i[1]==TYPE_STRING:
                        itm=stats[i[0]]
                    elif i[1]==TYPE_INT:
                        itm=int(stats[i[0]])
                    elif i[1]==TYPE_FLOAT:
                        itm=float(stats[i[0]])
                    elif i[1]==TYPE_BOOL:
                        itm=stats[i[0]].upper()=="TRUE"
                    elif i[1]==TYPE_TUPLE_INT:
                        itm=tuple(int(i) for i in stats[i[0]].split(","))
                    elif i[1]==TYPE_TUPLE_FLOAT:
                        itm=tuple(float(i) for i in stats[i[0]].split(","))
                    elif i[1]==TYPE_TUPLE_STRING:
                        itm=tuple(i for i in stats[i[0]].split(","))
                    elif i[1]==TYPE_COMBAT_MAP:
                        itm={}
                        for rect in stats[i[0]]:
                            key=rect.attrib["name"]
                            dimentionstag=rect.find("dimentions")
                            dimentions=(int(dimentionstag.find(i).text) for i in ("left","top","width","height"))
                            damagetag=rect.find("damage")
                            damage=(tuple(float(damagetag.find(i).text) for i in ("phis","ele","las","hea","ice","rad","bio","gas")),)
                            slot=(rect.find("slot").text,)
                            itm[key]=tuple(itertools.chain(dimentions,damage,slot))
                    elif i[1]==TYPE_VAR_NAME:
                        itm=name
                    elif i[1]==TYPE_VAR_WORLD:
                        itm=world
                    elif i[1]==TYPE_VAR_CAGE:
                        itm=cage
                    elif i[1]==TYPE_VAR_POSITION:
                        itm=position
                    elif i[1]==TYPE_IMAGE:
                        itm=cage.lookup(stats[i[0]])
                    elif i[1]==TYPE_ATTRNAME_AS_HOLDER:
                        itm=i[0].x
                    elif i[1]==TYPE_ITEM_PROB:
                        itm=[]
                        for ellement in stats[i[0]].findall("itm"):
                                
                            prob=float(ellement.attrib["prob"])
                            amount=int(ellement.attrib["amount"])
                            tags=ellement.findall("tag")
                            if len(tags)>0:
                                itmname=[]
                                for tag in tags:
                                    itmname.append(itm_name_to_number[tag.text.strip()])
                            else:
                                itmname=ellement.text
                            itm.append((prob,amount,itmname))
                    else:
                        raise ValueError(i[1],type(i[1]))
                    if len(i)==2:
                        args.append(itm)
                    elif len(i)==3:
                        kwargs[i[2]]=itm
                        #print "added argument: "+i[2]
            #except KeyError as ex:
            #    raise ValueError("cant find attr "+repr(ex)+" in object "+name)
            finally:
                pass
            obj= itemCls(*args, **kwargs)
            return obj
        return internal2
    return internal1