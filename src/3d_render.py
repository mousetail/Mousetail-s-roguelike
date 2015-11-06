'''
Created on 12 nov. 2014

@author: Maurits
'''
import pygame, sys
import windows, world
import imagecage

#insert any other item sets here

import constants

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
        """
        This function pretty much runs the whole game,
        calling the generate level functions, making the layout,
        redicting standared input,
        it also loads the sprite sheets
        """
        print "starting init"
        cage=imagecage.ImageCage()
        self.docheckbounds=kwargs["checkbounds"]
        pygame.init()
        self.screen=pygame.display.set_mode((1000,600))#,pygame.FULLSCREEN)#[1000,600])
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
        print "world is starting..."
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
        """
        refreshes the screen
        """
        for i in self.windows:
            i.redraw()
            
        for window in self.windows:
            if hasattr(window,"drawsurface"):
                self.screen.blit(window.drawsurface,window.position)
        pygame.display.flip()
    def update(self):
        """
        calls world.update mainly, then checks if the screen needs to be redrawn
        """
        self.world.update()
        if self.world.dirty:
            self.redraw()
        
        self.clock.tick()
    def event(self):
        """
        forwards pygame events to the windows and to the world object
        """
        for event in pygame.event.get():
            if event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
                #SAVE CODE HERE
                self.running=False
                self.world.quit()
            else:
                
                self.world.event(event)
                
                
            rd=False
            for i in self.windows:
                rd=i.addevent(event) or rd
            if rd:
                self.redraw()
    def finalize():
        self.world.finalize()
if __name__=="__main__":
    try:
        print "starting..."
        x=Displayer_3d(spritesheet="spritesheet_iso1.png",greyspritesheet="spritesheet_grey_1.png",
                       tilesize=64,checkbounds=False,grid_size=[constants.GRIDSIZE_X,constants.GRIDSIZE_Y])
        print "stage 2"
        pygame.USEREVENT+=1
        pygame.COLLISION=pygame.USEREVENT-1
        while x.running:
            x.event()
            x.update()
        print "done!"
        #print x.grid.data
    except Exception as ex:
        print ex;
        print ex.__dict__
        raise ex;
    finally:
        x.finalize()
        print "finally"
        pygame.quit()
        sys.exit()
