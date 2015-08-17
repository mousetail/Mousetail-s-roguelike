'''
Created on 17 jun. 2015

@author: Maurits
'''
from xml.etree import ElementTree as et
import monster_body, constants

import os

#places to load types from
#-------------------------
placestoloadfrom=[
    "itemClassRegistration"
                  ]
#-------------------------------/
from itemloaderutilmethods import *
import random
import sys


class XMLloader(object):
    '''
    classdocs
    '''


    def __init__(self,):
        '''
        Constructor
        '''
        self.objdefs={}
        self.clstypes={"Human":monsterMaker(monster_body.HumanBody)}
        sys.path.append(os.path.join("..","srcplug"))
        for i in placestoloadfrom:
            mod=__import__(i)
            defdict=mod.defs
            for key, value in defdict.items():
                self.clstypes[key]=value
            placestoloadfrom.extend(mod.placestoloadfrom)
        self.randomcats={} #categories which will be randomized into
        print self.clstypes
    def loadFile(self, filename=os.path.join("..","data","human.xml")):
        o=et.parse(filename)
        for itemdef in o.findall("item"):
            basedata=itemdef.find("basedata")
            if True: #This is just a section, used to differentiate from the other part
                name=basedata.find("name").text
                frequency=int(basedata.find("frequency").text.strip())
                assert 0<=frequency<=5, "frequency not within the range 0 (imposbile) to 5 (common)"
                tags=tuple(constants.itm_name_to_number[i.text.strip()] for i in basedata.find("tags"))
                typ=basedata.find("class").text.strip()
                if basedata.findall("maxnum"):
                    maxnum=int(basedata.find("maxnum").text)
                    #print "found maxnum"
                else:
                    maxnum=-1
            classdata=itemdef.find("classdata")
            clsdatadict={}
            if "base" in classdata.keys():
                for key, value in self.objdefs[classdata.attrib["base"]][3].items():
                    clsdatadict[key]=value
            for i in classdata.findall("attr"):
                
                attrname=i.attrib["name"]
                if "base" in i.keys():
                    basename=i.attrib["base"]
                    value=self.objdefs[basename][3][attrname]
                else:
                    if len(i)==0:
                        value=i.text.strip()
                    else:
                        value=i
                clsdatadict[attrname]=value
                if "randomcat" in i.keys():
                    print "item: "+name+" randomcat "+i.attrib["randomcat"]+" keys "+str(self.randomcats.keys())
                    
                    if i.attrib["randomcat"] in self.randomcats.keys():
                        if name in self.randomcats[i.attrib["randomcat"]].keys():
                            self.randomcats[i.attrib["randomcat"]][name][attrname]=value
                            print "category exists, item exists"
                        else:
                            self.randomcats[i.attrib["randomcat"]][name]={attrname:value}
                            print "category exists, item dousn't exist"
                    else:
                        self.randomcats[i.attrib["randomcat"]]={name:{attrname:value}}
                        print "category dousn't exist, item dousn't exits"
            self.objdefs[name]=(frequency, tags, typ, clsdatadict, constants.Holder(maxnum))
    def toDictRecursive(self, ellement):
        tmp={}
        for child in ellement:
            if "name" in child.attrib.keys():
                tag=child.attrib["name"]
            else:
                tag=child.tag
            if len(child)==0:
                value=child.text
            else:
                value=self.toDictRecursive(child)
            if tag not in tmp.keys():
                tmp[tag]=value
            elif isinstance(tmp[tag],list):
                tmp[tag].append(value)
            else:
                tmp[tag]=[tmp[tag],value]
        return tmp
    def findObj(self, name):
        itm=self.objdefs[name]
        cls=itm[2]
        ctype=self.clstypes[cls]
        return ctype(name,itm[3])
    def randomItem(self, dlevel, tags):
        tmplist=[]
        for k,i in self.objdefs.items():
            alltags=True
            for tag in tags:
                if tag not in i[1]:
                    alltags=False
            if i[4].x==0:
                alltags=False
                #print "TO MANY "+k+"'s"
            if alltags:
                for s in range(i[0]):
                    tmplist.append(k)
        try:
            itm= random.choice(tmplist)
            if self.objdefs[itm][4].x>0:
                self.objdefs[itm][4].x=self.objdefs[itm][4].x-1
            #    print "GENERATED "+itm+" "+str(self.objdefs[itm][4].x)
            else:
                pass
                #print self.objdefs[itm][4].x
            return itm
        except IndexError:
            raise IndexError("No item found with tags "+",".join(str(i) for i in tags))
    def flush(self):
        """
        Should be called at the end of loading the items so the list can be reformatted in a way better suited for loading
        """
        print "RANDOMCATS:"
        print self.randomcats
        print "------------"
        
        for shufcat in self.randomcats.values():
            items=list(shufcat.values())
            random.shuffle(items)
            i=0
            for itmname in shufcat.keys():
                for j in items[i].items():
                    self.objdefs[itmname][3][j[0]]=j[1]
                i+=1
    def fastRandomItem(self, position, world, cage, dlevel, tags,safemode=False,returnbody=False):
        return self.findObj(self.randomItem(dlevel, tags))(position,world,cage,safemode=safemode,returnbody=returnbody)
    def fastItemByName(self, name, position, world, cage,returnbody=False):
        return self.findObj(name)(position,world,cage,returnbody=returnbody)
if __name__=="__main__":
    bj=XMLloader()
    bj.loadFile()
    print "\n".join(str(i) for i in bj.objdefs.items())
    obj=bj.fastRandomItem([7,12],None,None,12,(constants.ITM_HUMANOID,),safemode=True)
    print "-----"+obj.name+"------"
    print "attack zones: ",obj.body.attack_zones
    print "speed:", obj.getspeed()
            
