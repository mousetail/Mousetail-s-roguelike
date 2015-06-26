'''
Created on 17 jun. 2015

@author: Maurits
'''
from xml.etree import ElementTree as et
import monster_body, constants
from itemloaderutilmethods import *
import random

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
    def loadFile(self, filename="..\data\human.xml"):
        o=et.parse(filename)
        for itemdef in o.findall("item"):
            basedata=itemdef.find("basedata")
            if True: #This is just a section, used to differentiate from the other part
                name=basedata.find("name").text
                frequency=int(basedata.find("frequency").text.strip())
                assert 0<=frequency<=5, "frequency not within the range 0 (imposbile) to 5 (common)"
                tags=tuple(constants.itm_name_to_number[i.text.strip()] for i in basedata.find("tags"))
                typ=basedata.find("class").text.strip()
            classdata=itemdef.find("classdata")
            clsdatadict={}
            if "base" in classdata.keys():
                for key, value in self.objdefs[classdata.attrib["base"]][3].items():
                    clsdatadict[key]=value
            for i in classdata.findall("attr"):
                if "base" in i.keys():
                    attrname=i.attrib["name"]
                    basename=i.attrib["base"]
                    clsdatadict[attrname]=self.objdefs[basename][3][attrname]
                else:
                    if len(i)==0:
                        clsdatadict[i.attrib["name"]]=i.text.strip()
                    else:
                        clsdatadict[i.attrib["name"]]=self.toDictRecursive(i)
            self.objdefs[name]=(frequency, tags, typ, clsdatadict)
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
            if alltags:
                for s in range(i[0]):
                    tmplist.append(k)
        try:
            return random.choice(tmplist)
        except IndexError:
            raise IndexError("No item found with tags "+",".join(str(i) for i in tags))
    def fastRandomItem(self, position, world, cage, dlevel, tags,safemode=False):
        return self.findObj(self.randomItem(dlevel, tags))(position,world,cage,safemode=safemode)
        
if __name__=="__main__":
    bj=XMLloader()
    bj.loadFile()
    print "\n".join(str(i) for i in bj.objdefs.items())
    obj=bj.fastRandomItem([7,12],None,None,12,(constants.ITM_HUMANOID,),safemode=True)
    print "-----"+obj.name+"------"
    print "attack zones: ",obj.body.attack_zones
    print "speed:", obj.getspeed()
            