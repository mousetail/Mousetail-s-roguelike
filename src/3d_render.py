'''
Created on 12 nov. 2014

@author: Maurits
'''
import pygame, sys
import windows, world
import imagecage

#insert any other item sets here

import containers
import potions
import weapons

#----------------------------
def splitsprites(spritesheet, tilesize):
    sprts=[]
    for i in range(0,spritesheet.get_width(),tilesize):
        s=pygame.Surface([tilesize,tilesize],pygame.SRCALPHA)
        s.fill([0,0,0,0])
        s.blit(spritesheet,[0,0],[i,0,tilesize,tilesize])
        sprts.append(s.convert_alpha())#                                    /
        #print s.get_at([0,0])                                                     |
        #END LOAD SPRITES -------------------------------------------------------------|
    return sprts
class Displayer_3d():
    '''
    A renderer that renderes Isometricly what a 2d renerer would render
    '''

    
    def __init__(self,**kwargs):
        cage=imagecage.ImageCage()
        self.docheckbounds=kwargs["checkbounds"]
        pygame.init()
        self.screen=pygame.display.set_mode((0,0),pygame.FULLSCREEN)#[1000,600])
        self.screen.fill([0,0,0])
        #LOAD SPRITES ------------------------------------------------------------------
        spritesheet=cage.lookup(kwargs["spritesheet"]).convert_alpha()
        greyspritesheet=cage.lookup(kwargs["greyspritesheet"]).convert_alpha()
        self.font=pygame.font.SysFont('Tahoma',14)
        tilesize=kwargs["tilesize"]
        self.sprites=splitsprites(spritesheet, tilesize)
        self.greysprites=splitsprites(greyspritesheet, tilesize)
        
        self.state="loading"
        self.draw_offset=0
        #print "4}generating level..."
        textwidget=windows.LogWindow([300,600],(0,0),self.font,self.screen,stdout=sys.stdout,antialias=False)
        sys.stdout=textwidget
        pygame.display.flip()
        self.world=world.World(kwargs["grid_size"],cage,)
        sys.stdout=textwidget.data["stdout"]
        #print "STDOUT ",sys.stdout
        del textwidget
        self.state="game"
        self.draw_offset=[0,0]
        self.running=True
        self.clock=pygame.time.Clock()
        #pygame.key.set_repeat(100,100)   
        self.focus=None
        self.windows=[]
        #
        #
        # stat displayer
        #__________________________________
        #                      |
        #   #3d view           |Sys.Stdout displayer
        #        m             |--------------
        #                      |Inventory window
        #                      \
        self.windows.append(windows.StatWindow([self.screen.get_width(),32],[0,0],self.font,self.world.player))
        self.windows.append(windows.RenderWindow(self.world,[self.screen.get_width()-300,self.screen.get_height()-32],[0,32],self.sprites,self.greysprites,self.world.player,))
        self.windows.append(windows.LogWindow([300,(self.screen.get_height()-32)/2],[self.screen.get_width()-300,32],self.font,False,stdout=sys.stdout))
        
        sys.stdout=self.windows[-1]
        self.windows.append(windows.InventoryWindow([300,(self.screen.get_height()-32)/2],[self.screen.get_width()-300,(self.screen.get_height()-32)/2+32],
                                                    self.font, self.world.player))
        self.windows.append(windows.CombatDebugWindow([100,200],[50,50],self.font,self.world.player))
        
        self.world.player.welcomeMessage()
        
        self.redraw()
    def redraw(self):
        for i in self.windows:
            i.redraw()
    def update(self):
        self.world.update()
        if self.world.dirty:
            self.redraw()
    def draw(self):
        self.clock.tick()
        for window in self.windows:
            if hasattr(window,"drawsurface"):
                self.screen.blit(window.drawsurface,window.position)
        pygame.display.flip()
    def event(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                #SAVE CODE HERE
                self.running=False
            else:
                
                self.world.event(event)
                
                
            rd=False
            for i in self.windows:
                rd=i.addevent(event) or rd
            if rd:
                self.redraw()
                    
if __name__=="__main__":
    x=Displayer_3d(spritesheet="spritesheet_iso1.png",greyspritesheet="spritesheet_grey_1.png",
    tilesize=64,checkbounds=False,grid_size=[150,150])
    pygame.USEREVENT+=1
    pygame.COLLISION=pygame.USEREVENT-1
    while x.running:
        x.draw()
        x.event()
        x.update()
    #print x.grid.data
    pygame.quit()     