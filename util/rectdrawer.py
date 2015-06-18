import pygame
from xml.etree import ElementTree as et
pygame.init()

class Rectangle(object):
    def __init__(self, rect, damage, slotname, font, name=None, position=0):
        self.rect=rect
        self.damage=damage
        self.slotname=slotname
        self.guis=[]
        
        self.name=name
        if self.name is None:
            self.name=Holder("")
        ypos=0
        for i in damage:
            self.guis.append(TextBox(i,[area_scale*100+32+ypos,position*32+32],(48,32),font,"text"))
            ypos+=50
        self.guis.append(TextBox(self.slotname,[area_scale*100+32+ypos,position*32+32],(100,32),font,"text"))
        ypos+=100
        self.guis.append(TextBox(self.name,[area_scale*100+32+ypos,position*32+32],(100,32),font,"text"))
    def draw(self, screen):
        #print (self.rect)
        color=(255,255,255)
        for i in self.guis:
            if i.selected:
                color=(255,255,0)
                break
        
        pygame.draw.rect(screen,color,tuple(i * area_scale for i in self.rect),2)
    def reorder(self, position):
        for i in self.guis:
            i.position[1]=position*32+32
class Holder(object):
    def __init__(self, what):
        self.what=what
    def __getattribute__(self, attr):
        return object.__getattribute__(self,"what")
    def __setattr__(self, attr, value):
        object.__setattr__(self,"what",value)
    def __str__(self):
        return str(self.what)
class TextBox(object):
    def __init__(self, holder, position, size, font, typ="text"):
        self.holder=holder
        self.typ=typ
        self.selected=False
        self.position=position
        self.size=size
        self.font=font
    def event(self, event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            pos=event.pos
            if (self.position[0]<pos[0]<self.position[0]+self.size[0] and
                self.position[1]<pos[1]<self.position[1]+self.size[1]):
                self.selected=True
            else:
                self.selected=False
        elif event.type==pygame.KEYDOWN:
            if self.selected:
                if event.key==pygame.K_BACKSPACE:
                    if self.typ=="text":
                        self.holder.x=self.holder.x[:-1]
                    elif self.typ=="float":
                        if len(str(self.holder.x))>1:
                            o=str(self.holder.x)
                            if o.endswith(".0"):
                                o=o[:-2]
                            if len(o)>1:
                                self.holder.o=float(o[:-1])
                            else:
                                self.holder.o=0.0
                        else:
                            self.holder.x=0
                else:
                    if self.typ=="text":
                        self.holder.x=self.holder.x+event.unicode
                    elif self.typ=="float":
                        try:
                            o=float(event.unicode)
                            self.holder.x=float(str(self.holder.x)+event.unicode)
                        except ValueError:
                            pass
    def draw(self, screen):
        screen.blit(self.font.render(str(self.holder.x),1,(255,255,255)),self.position,(0,0,self.size[0],self.size[1]))
        if self.selected:
            pygame.draw.rect(screen,(255,255,255),(self.position[0],self.position[1],self.size[0],self.size[1]),1)
screen=pygame.display.set_mode((1200,700))
area_scale=6
screen.fill((0,0,0))

startpos=[0,0]
endpos=[0,0]

background=pygame.surface.Surface((area_scale*100,area_scale*100))
for i in range(100):
    for j in range(100):
        if (i+j)%2==0:
            if ((i//10)+(j//10))%2==0:
                color=(50,70,70)
            else:
                color=(100,50,50)
        else:
            if ((i//10)+(j//10))%2==0:
                color=(100,140,140)
            else:
                color=(200,100,100)
                
        background.fill(color,(i*area_scale,j*area_scale,area_scale,area_scale))

damage_types=("phis","ele","las","hea","rad","bio","gas")
rect_pos=("left","top","width","height")

ximage=pygame.image.load("x.png")
icons=[pygame.image.load(i+".png") for i in
       damage_types]

font=pygame.font.Font(None,28)

pressed=False

tree=et.parse("tmpxml.xml")
root=tree.getroot()
rectangles=[]
for child in root.findall("rectangle"):
    attribs=child.attrib
    if ("name" in attribs.keys()):
        name=Holder(attribs["name"])
    else:
        name=None
    squareX=child.find("dimentions")
    damageX=child.find("damage")
    slotX=child.find("slot")
    square=tuple(int(squareX.find(i).text) for i in rect_pos)
    damage=tuple(Holder((damageX.find(i).text)) for i in damage_types)
    slot=Holder(slotX.text)
    rectangles.append(Rectangle(square, damage, slot, font, name, len(rectangles)))
    
running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            if not pressed and event.button==1:
                pressed=True
                startpos=event.pos
                endpos=event.pos
        elif event.type==pygame.MOUSEMOTION:
            if pressed:
                endpos=event.pos
        elif event.type==pygame.MOUSEBUTTONUP:
            if pressed:
                endpos=event.pos
                if (endpos[0]<(area_scale*100) and startpos[0]<(area_scale*100)
                    and endpos[1]<(area_scale*100) and startpos[1]<(area_scale*100)):
                    rectangles.append(Rectangle((startpos[0]//area_scale,startpos[1]//area_scale,(endpos[0]-startpos[0])//area_scale,(endpos[1]-startpos[1])//area_scale),
                                                tuple(Holder("0") for i in range(7)),
                                                Holder("None"),font,None,len(rectangles)))
                    
                pressed=False
            if (area_scale*100)<endpos[0]<(area_scale*100+32):
                index=endpos[1]//32-1
                if index<len(rectangles):
                    del rectangles[index]
        for i in rectangles:
            for j in i.guis:
                j.event(event)
    screen.fill((0,0,0))
    screen.blit(background,(0,0))
    for i in rectangles:
        i.draw(screen)
    if pressed:
        pygame.draw.rect(screen,(255,0,0),(startpos[0],startpos[1],(endpos[0]-startpos[0]),(endpos[1]-startpos[1])),2)

    for i in range(len(rectangles)):
        screen.blit(ximage,(area_scale*100,32+32*i))
        for j in rectangles[i].guis:
            j.draw(screen)
        rectangles[i].reorder(i)
    for i in range(len(icons)):
        screen.blit(icons[i],(area_scale*100+32+(50*i),0))
    pygame.draw.rect(screen,(255,255,255),(0,0,area_scale*100,area_scale*100),1)
    pygame.display.flip()
pygame.quit()

with open("tmpxml.xml","w") as f:
    f.write("<rectangles>")
    for i in rectangles:
        f.write("<rectangle name=\""+str(i.name)+"\"><dimentions>"+
                " ".join("<"+rect_pos[j]+">"+str(i.rect[j])+"</"+rect_pos[j]+">" for j in range(len(rect_pos)))+"</dimentions>\n")
        f.write("<damage>"+" ".join("<"+damage_types[j]+">"+str(i.damage[j])+"</"+damage_types[j]+">" for j in range(len(damage_types))))
        f.write("</damage><slot>"+str(i.slotname)+"</slot>")         
        f.write("</rectangle>\n")
    f.write("</rectangles>")
