'''
Created on 29 dec. 2014

@author: Maurits
'''
import pygame, textwrap, itertools, random
from constants import *

class BaseWindow(object):
    def addevent(self, event):
        pass
class RenderWindow(BaseWindow):
    '''
    A window that renders the scene
    '''


    def __init__(self, world, size, position, sprites, greysprites=None, focus=None, **otherdatatostore):
        '''
        world=the world to render, size=size of the frame, otherdatatostore:if you need to store something like the position
        '''
        self.world=world
        self.size=size
        self.data=otherdatatostore
        self.position=position
        self.dynamicobjectsstore=tuple([] for i in range(world.grid_size[1]+world.grid_size[0]))
        self.drawsurface=None
        self.focus=focus
        self.sprites=sprites
        if greysprites:
            self.greysprites=greysprites
        else:
            self.greysprites=sprites
        self.draw_offset=[98,37]
    def redraw(self):#print "SOMETHING IS MOVING"
        for i in self.dynamicobjectsstore:
            i[:]=[]
        
        #print len(tuple(j for j in self.dynamicobjectsstore if len(j)==0)),len(self.objects)
        for x in self.world.objects:
            if hasattr(x,"position"):
                try:
                    self.dynamicobjectsstore[(x.position[1])-x.position[0]+self.world.grid_size[0]+1].append(x)
                except IndexError:
                    pass
            #print (x.position[1])-x.position[0]+self.grid_size[0]+1
            #HAS A BUG WHEN NEGATIVE
             
        if self.focus:
            self.draw_offset[0]=(self.focus.position[0]+self.focus.position[1])*32-500
            self.draw_offset[1]=(self.focus.position[1]-self.focus.position[0])*16-300
            #print self.focus
        else:
            pass
            #print self.focus
        #print len(tuple(j for j in self.dynamicobjectsstore if len(j)==0))
        if self.drawsurface==None:
            self.drawsurface=pygame.Surface(self.size)
        self.drawsurface.fill([0,0,0])
        #print "drawing"
        
        
        
        for y in range(self.draw_offset[1]//16-4,self.size[1]//16+self.draw_offset[1]//16):
            for x in range(self.draw_offset[0]//64-4,(self.size[0]//64)+(self.draw_offset[0])//64+2):
                if y%2:
                    pos=[(x-y//2),(x+y//2)]
                    ad=0
                else:
                    pos=[(x-y//2+1),(x+y//2)]
                    ad=32
                #if x%2==0:
                    #ad=-16
                #    pass
                if pos[0]>0 and pos[1]>0 and pos[0]<self.world.grid_size[0] and pos[1]<self.world.grid_size[1]:
                    #try:
                        if self.world.grid[pos] and (not self.focus or self.focus.visible[pos]):
                            #print "drawing"
                            if not self.focus or self.focus.visible[pos]==2:
                                self.drawsurface.blit(self.sprites[self.world.grid[pos]],
                                                  ((x*64-self.draw_offset[0])+(ad),(y*16-self.draw_offset[1])))
                            else:
                                
                                self.drawsurface.blit(self.greysprites[self.world.grid[pos]],
                                                  ((x*64-self.draw_offset[0])+(ad),(y*16-self.draw_offset[1])))
                    #except TypeError as ex:
                    #    print self.world.grid[pos]
                    #    raise ex
            if 0<(y+self.world.grid_size[0])<len(self.dynamicobjectsstore):
        
                for x in self.dynamicobjectsstore[y+self.world.grid_size[0]]:
                    if (not self.focus or self.focus.visible[x.position]==2):
                        x.draw(self.drawsurface,((x.position[0]+x.position[1])*32-self.draw_offset[0],
                                            y*16-self.draw_offset[1]))#(x.position[0]-x.position[1])*16-self.draw_offset[1]))
                    
                    #DEBUG INFORMATION, UNCOMMENT TO PRINT
                    #pygame.draw.line(self.screen,(255,0,0),(0,y*16-self.draw_offset[1]),(1000,y*16-self.draw_offset[1]))
                    #print y
                    #print [(x.position[0]-x.position[1])*32-self.draw_offset[0],y*16-self.draw_offset[1]]
        pygame.display.flip()
class LogWindow(BaseWindow):
    def __init__(self, size, position, font, autorender=False, **other):
        self.data=other
        self.size=size
        self.lines=[]
        self.font=font
        self.autorender=autorender
        self.numlines=self.size[1]/18
        self.drawsurface=pygame.Surface(self.size)
        self.position=position
        self.wrapper=textwrap.TextWrapper(width=self.size[0]/8)
        if "stdout" not in self.data:
            self.data["stdout"]=None
        else:
            #print >>self.data["stdout"], self.data["stdout"]
            pass
        if "antialias" not in self.data:
            self.data["antialias"]=True
    def redraw(self):
        self.drawsurface.fill([0,0,0])
        linenum=0
        for line in self.lines[-self.numlines:]:
            linenum+=1
            clr=line[:3]
            
            color=[255,255,255]
            if len(clr)==3 and clr[1]=="}":
                line=line[2:]
                if   clr[0]=="0" or clr[0]=="g":
                    color=[200,200,200]
                elif clr[0]=="1" or clr[0]=="R":
                    color=[255,0,0]
                elif clr[0]=="2" or clr[0]=="W":
                    color=[255,255,255]
                elif clr[0]=="3" or clr[0]=="G":
                    color=[0,255,0]
                elif clr[0]=="4" or clr[0]=="Y":
                    color=[0,255,255]
                elif clr[0]=="5" or clr[0]=="B":
                    color=[0X2b,0Xa3,0Xab]
            self.drawsurface.blit(self.font.render(line.strip(),self.data["antialias"],color),
                        [0,16*linenum])
        
    def write(self, text):
        line=None
        if len(self.lines)==0 or self.lines[-1].endswith("\n"):
            line=text
        else:
            line=self.lines.pop()+text
        if len(line)>=2 and line[1]=="}":
            splitlines=self.wrapper.wrap(line[2:])
            color=line[0]
        else:
            splitlines=self.wrapper.wrap(line)
            color="W"
        for i in splitlines:
            self.lines.append(color+"}"+i)
        if text.endswith("\n"):
            self.lines[-1]+="\n"
#         if len(self.lines)==0 or self.lines[-1].endswith("\n"):
#             if len(line)>=2 and line[1]=="}":
#                 self.lines.extend(line[:2]+i+"\n" for i in self.wrapper.wrap(line[2:]))
#             else:
#                 self.lines.extend(i+"\n" for i in self.wrapper.wrap(line))
#             if line.endswith("\n"):
#                 self.lines[-1]=self.lines[-1]+"\n"
#         else:
#             oldline=self.lines[-1]
#             del self.lines[-1]
#             if oldline[1]=="}":
#                 self.lines.extend(oldline[:2]+i for i in self.wrapper.wrap(oldline+line))
#             else:
#                 self.lines.extend(self.wrapper.wrap(oldline+line))
        if self.autorender:
            self.redraw()
            self.autorender.blit(self.drawsurface,self.position)
            pygame.display.flip()
            pygame.event.poll()
        self.data["stdout"].write(text)
class StatWindow(BaseWindow):
    def __init__(self, size, position, font, trackmonster):
        self.size=size
        self.position=position
        self.drawsurface=pygame.Surface(self.size)
        self.trackmonster=trackmonster
        self.font=font
    def redraw(self):
        self.drawsurface.fill([0,0,0])
        strings=[]
        for i in self.trackmonster.stats:
            strings.append(str(i)+":"+str(self.trackmonster.stats[i]))
        if hasattr(self.trackmonster,"body"):
            strings.append("HP:{0:.1f}/{1}".format(self.trackmonster.body.health,self.trackmonster.body.maxhealth))
        strings.extend(flag_uncode[i] for i in self.trackmonster.status_messages if i in flag_uncode.keys())
        sperstring=self.size[0]/len(strings)
        for i in range(len(strings)):
            self.drawsurface.blit(self.font.render(strings[i],1,[255,255,255]),
                                  [10+sperstring*i,5])
class InventoryWindow(StatWindow):
    def __init__(self, *args, **kwargs):
        StatWindow.__init__(self, *args, **kwargs)
        self.scroll=0
        self.selected=None
        self.tab="inv"
    def redraw(self):
        
        self.drawsurface.fill((0,0,0))
        tm=self.trackmonster
        
        ypos=-self.scroll
        if self.tab=="inv":
            for item in self.trackmonster.inventory:
                if tm.inventory[item][0].image.get_height()==64:
                    self.drawsurface.blit(tm.inventory[item][0].image,[5,ypos])
                else:
                    self.drawsurface.blit(tm.inventory[item][0].image,[5,ypos-32])
                if len(tm.inventory[item])==1:
                    nm=tm.inventory[item][0].name
                else:
                    nm=tm.inventory[item][0].pname
                weight=tm.inventory[item][0].getWeight()*len(tm.inventory[item])
                self.drawsurface.blit(self.font.render(item+": "+str(len(tm.inventory[item]))+" "+str(nm)+" ("+str(weight)+"g)",1,[255,255,255]),
                                      [74, ypos])
                
                ypos+=65
        elif self.tab=="arm":
            ypos+=30
            self.drawsurface.blit(self.font.render("Active slots: ",1,[255,255,255]),(74,ypos))
            ypos+=60
            for letter in self.trackmonster.equipment_letters:
                item=self.trackmonster.equipment_letters[letter]
                self.drawsurface.blit(tm.equipment[item].image, [5,ypos])
                nm=tm.equipment[item].name
                self.drawsurface.blit(self.font.render(item+": ("+letter+") "+str(nm),1,[255,255,255]),(74,ypos))
                ypos+=65
            ypos+=30
            self.drawsurface.blit(self.font.render("all slots: ",1,[255,255,255]),(74,ypos))
            ypos+=60
            for item in self.trackmonster.equipment:
                if not self.trackmonster.equipment[item]:
                    
                    self.drawsurface.blit(self.font.render(item+": Nothing",1,[255,255,255]),(74,ypos))
                    ypos+=65
    def addevent(self, event):
        if event.type==pygame.MOUSEMOTION:
            eventpos=[event.pos[0]-self.position[0],event.pos[1]-self.position[1]]
            if (eventpos[0])>(self.size[0]-50):
                if self.tab=="inv":
                    totaldist=len(self.trackmonster.inventory)*64-self.size[1]
                else:
                    totaldist=len(self.trackmonster.equipment)*64-self.size[1]+90
                if totaldist>0:
                    #self.scroll/totaldist=self.height[1]/event.pos[1]
                    self.scroll=int(eventpos[1]/float(self.size[1])*totaldist)
                    #print "scroll: "+str(self.scroll)
                    return True
            return False
        elif event.type==pygame.MOUSEBUTTONUP:
            
            eventpos=[event.pos[0]-self.position[0],event.pos[1]-self.position[1]]
            if self.size[1]-eventpos[1]>20:
                if eventpos[0]>(self.size[0]/2):
                    self.tab="inv"
                    self.scroll=0
                else:
                    self.tab="arm"
                    self.scroll=0
                    
                return True
            else:
                return False
        else:
            return False
class CombatDebugWindow(BaseWindow):
    def __init__(self, size, position, font, trackmonster):
        self.position=position
        self.font=font
        self.size=size
        self.position=position
        self.font=font
        self.trackmonster=trackmonster
        self.drawsurface=pygame.Surface(self.size)
        self.drawsurface.fill((0,0,0))
    def redraw(self):
        body=self.trackmonster.body
        self.drawsurface.fill((0,0,0))
        j=0
        for i in body.attack_zones.values():
            #print i[:4]
            
            
            self.drawsurface.fill([random.choice(pygame.color.THECOLORS.values()),[100,100,100],[200,200,200],[100,100,200]][j], i[:4])
            j+=1
            j%=4
        if hasattr(body, "lastattackspot"):
            self.drawsurface.fill([255,0,0],body.lastattackspot+[2,2])
            self.drawsurface.fill([0,0,255],body.lastdebspot+[2,2])
            self.drawsurface.blit(self.font.render(body.lasttarget, 1, (255,255,255)), [5,100])