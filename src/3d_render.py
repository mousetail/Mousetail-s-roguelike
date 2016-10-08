'''Created on 12 nov. 2014

@author: Maurits

uses python 2.7
'''

import pygame, sys, traceback
import windows, world
import imagecage

# insert any other item sets here

import constants


def splitsprites(spritesheet, tilesize):
    sprts=[]
    for i in range(0, spritesheet.get_width(), tilesize):
        s = pygame.Surface([tilesize, tilesize], pygame.SRCALPHA)
        s.fill([0, 0, 0, 0])
        s.blit(spritesheet, [0, 0], [i, 0, tilesize, tilesize])
        sprts.append(s.convert_alpha())
    return sprts


class Displayer_3d(object):
    '''
    A renderer that renderes Isometricly what a 2d renerer would render
    '''

    def __init__(self, fullscreen=True, **kwargs):
        """
        This function pretty much runs the whole game,
        calling the generate level functions, making the layout,
        redicting standared input,
        it also loads the sprite sheets
        """
        print "starting init"
        cage = imagecage.ImageCage()
        self.docheckbounds = kwargs["checkbounds"]
        pygame.init()
        if fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1000, 600))
        self.screen.fill([0, 0, 0])
        spritesheet = cage.lookup(kwargs["spritesheet"]).convert_alpha()
        greyspritesheet = cage.lookup(kwargs["greyspritesheet"]).convert_alpha()
        self.font = pygame.font.SysFont('Tahoma', 14)
        tilesize = kwargs["tilesize"]
        self.sprites = splitsprites(spritesheet, tilesize)
        self.greysprites = splitsprites(greyspritesheet, tilesize)

        self.state = "loading"
        self.draw_offset = 0
        pygame.display.flip()
        print "world is starting..."
        self.world = world.World(kwargs["grid_size"], cage)
        self.state = "game"
        self.draw_offset = [0, 0]
        self.running = True
        self.clock = pygame.time.Clock()
        self.focus = None
        #
        #
        # stat displayer
        # __________________________________
        #                      |
        #   #3d view           |Sys.Stdout displayer
        #        m             |--------------
        #                      |Inventory window
        #                      \

        inventoryWindow = windows.InventoryWindow(self.font, self.world.cage, self.world.player)
        logWindow = windows.LogWindow(self.font, self.world.cage)
        sys.stdout = logWindow
        mainWindow = windows.RenderWindow(self.world.cage, self.world,
                                          self.sprites, self.greysprites, self.world.player)
        statWindow = windows.StatWindow(self.world.cage, self.font, self.world.player)
        self.window = windows.PairWindow(0.1, 1, statWindow,
                                         windows.PairWindow(0.75, 0, mainWindow,
                                                            windows.PairWindow(0.5, 1, logWindow, inventoryWindow)))
        self.window.setSize(self.screen.get_size())

        self.world.player.welcomeMessage()
        self.draw()

    def draw(self):
        """
        refreshes the screen
        """
        self.window.draw(self.screen)
        pygame.display.flip()

    def update(self):
        """
        calls world.update mainly, then checks if the screen needs to be redrawn
        """
        self.world.update()
        self.draw()
        self.clock.tick()

    def event(self):
        """
        forwards pygame events to the windows and to the world object
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False
                self.world.quit()
            else:
                self.world.event(event)
            self.window.addEvent(event)

    def finalize(self):
        self.world.finalize()


if __name__=="__main__":
    x = None
    try:
        print "starting..."
        x = Displayer_3d(spritesheet="spritesheet_iso1.png", greyspritesheet="spritesheet_grey_1.png",
                         tilesize=64, checkbounds=False, grid_size=[constants.GRIDSIZE_X, constants.GRIDSIZE_Y],
                         fullscreen="window" not in sys.argv)
        print "stage 2"
        while x.running:
            x.event()
            x.update()
        print "done!"
    except Exception as ex:
        print "-"*30
        print "|", type(ex).__name__ + ":" + str(ex)
        print "|",ex.__dict__
        line=traceback.print_exc(None, None)
        if len(line)==0:
            print "|NO traceback"
        else:
            print line
    
    finally:
        if x is not None:
            x.finalize()
        print "finally"
        pygame.quit()
        sys.exit()
