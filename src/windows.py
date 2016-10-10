'''
Created on 29 dec. 2014

@author: Maurits
'''
import pygame, textwrap
from constants import *

class BaseWindow(object):
    """a type of interface documenting what you need to implement.
    It's kinda an interface, mostly inherited by Window
    and it's subclasses, and PairWindow"""

    def draw(self):
        """updates the variable drawsurface to reflect what the screen should show
        should be called by base classes **after** it's redrawn istelf basically"""
        pass

    def setSize(self, size):
        """Should be implemented by base classes,
        sets the size of the child"""
        pass

    def getSize(self):
        """Again, implement this to return the actual size"""
        return 0, 0

    def addEvent(self, event):
        pass


class PairWindow(BaseWindow):
    """A basic window that holds 2 other windows"""

    def __init__(self, split=0.5, splitDirection=0, leftWindow=None, rightWindow=None):
        self.split = split
        self.leftWindow = leftWindow
        self.rightWindow = rightWindow
        self.size = (0, 0)
        self.splitDirection = splitDirection
        self.rightWindowSize = (0, 0)
        self.fixSplit()

    def setSize(self, size):
        self.size = tuple(size)
        self.fixSplit()

    def getSize(self):
        return self.size

    def fixSplit(self):
        # type: () -> None
        if self.splitDirection == 0:
            self.rightWindowSize = (self.size[0] - int(self.size[0] * self.split), self.size[1])
            self.leftWindow.setSize((int(self.size[0] * self.split), self.size[1]))
            self.rightWindow.setSize(self.rightWindowSize)
        else:
            self.rightWindowSize = (self.size[0], self.size[1] - int(self.size[1] * self.split))
            self.leftWindow.setSize((self.size[0], int(self.size[1] * self.split)))
            self.rightWindow.setSize(self.rightWindowSize)

    def draw(self, surface):
        self.leftWindow.draw(surface.subsurface((0, 0) + self.leftWindow.getSize()))
        if self.splitDirection == 0:
            self.rightWindow.draw(surface.subsurface((int(self.size[0] * self.split), 0,
                                                      self.rightWindowSize[0], self.rightWindowSize[1])))
        else:
            self.rightWindow.draw(surface.subsurface((0, int(self.size[1] * self.split),
                                                      self.rightWindowSize[0], self.rightWindowSize[1])))

    def addEvent(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP or
                    event.type == pygame.MOUSEMOTION):
            if self.splitDirection == 0:
                if event.pos[0] > self.leftWindow.getSize()[0]:
                    event.pos = (event.pos[0] - self.leftWindow.getSize()[0], event.pos[1])
                    self.rightWindow.addEvent(event)
                else:
                    self.leftWindow.addEvent(event)
            else:
                if event.pos[1] > self.leftWindow.getSize()[1]:
                    event.pos = (event.pos[0], event.pos[1] - self.leftWindow.getSize()[1])
                    self.rightWindow.addEvent(event)
                else:
                    self.leftWindow.addEvent(event)
        else:
            self.leftWindow.addEvent(event)
            self.rightWindow.addEvent(event)


class Window(BaseWindow):
    def __init__(self, imagecage):
        self.size = (0, 0)
        self.dirty = True
        self.image = imagecage.getProxy("GUI/frame.png", True)
        self.frameSize = 32  # Hardcoded for now, size of border
        self.borderWidth = 127 - self.frameSize * 2  # The longest side of the borders

    def setSize(self, size):
        self.size = size

    def getSize(self):
        return self.size

    def draw(self, surface):
        """Heavy method, don't call often when inherited"""
        if self.dirty:
            self.dirty = False
            for i in range(3):
                for j in range(3):
                    corner = [i, j]
                    originpos = [0, 0]
                    originsize = [0, 0]
                    size = [0, 0]
                    destpos = [0, 0]
                    for k in range(2):
                        if corner[k] == 0:
                            originpos[k] = 0
                            size[k] = self.frameSize
                            originsize[k] = self.frameSize
                            destpos[k] = 0
                        elif corner[k] == 1:
                            originpos[k] = self.frameSize
                            size[k] = self.size[k] - self.frameSize * 2
                            originsize[k] = self.borderWidth
                            destpos[k] = self.frameSize
                        else:
                            originpos[k] = self.frameSize + self.borderWidth
                            size[k] = self.frameSize
                            originsize[k] = self.frameSize
                            destpos[k] = self.size[k] - self.frameSize
                    # print >> stderr, "destpos: ", destpos, self.size, size
                    surface.blit(pygame.transform.scale(self.image.subsurface((originpos[0], originpos[1],
                                                                               originsize[0], originsize[1])),
                                                        size),
                                 destpos)


class RenderWindow(Window):
    '''
    A window that renders the scene
    '''

    def __init__(self, imageCage, world, sprites, greysprites=None, focus=None):
        '''
        world=the world to render, size=size of the frame, otherdatatostore:if you need to store something like the position
        '''
        Window.__init__(self, imageCage)
        self.world = world
        self.dynamicobjectsstore = tuple([] for i in range(world.grid_size[1] + world.grid_size[0]))
        self.focus = focus
        self.sprites = sprites
        if greysprites:
            self.greysprites = greysprites
        else:
            self.greysprites = sprites
        self.draw_offset = [98, 37]

    def draw(self, surface):
        self.dirty |= self.world.dirty
        if self.dirty:
            if self.focus and self.focus.dead:
                self.focus = None

            for i in self.dynamicobjectsstore:
                i[:] = []

            for x in self.world.objects:
                if hasattr(x, "position"):
                    try:
                        self.dynamicobjectsstore[(x.position[1]) - x.position[0] + self.world.grid_size[0] + 1].append(
                            x)
                    except IndexError:
                        pass

            if self.focus:
                self.draw_offset[0] = (self.focus.position[0] + self.focus.position[1]) * 32 - 500
                self.draw_offset[1] = (self.focus.position[1] - self.focus.position[0]) * 16 - 300
            else:
                pass

            surface.fill([0, 0, 0])

            for y in range(self.draw_offset[1] // 16 - 4, self.size[1] // 16 + self.draw_offset[1] // 16):
                for x in range(self.draw_offset[0] // 64 - 4, (self.size[0] // 64) + (self.draw_offset[0]) // 64 + 2):
                    if y % 2:
                        pos = [(x - y // 2), (x + y // 2)]
                        ad = 0
                    else:
                        pos = [(x - y // 2 + 1), (x + y // 2)]
                        ad = 32
                    if (pos[0] > 0 and pos[1] > 0 and pos[0] < self.world.grid_size[0]
                        and pos[1] < self.world.grid_size[1]):
                        if self.world.grid[pos] and (not self.focus or self.focus.visible[pos]):
                            if not self.focus or self.focus.visible[pos]==2:
                                surface.blit(self.sprites[self.world.grid[pos]],
                                             ((x * 64 - self.draw_offset[0]) + ad, (y * 16 - self.draw_offset[1])))
                            else:
                                surface.blit(self.greysprites[self.world.grid[pos]],
                                             ((x * 64 - self.draw_offset[0]) + ad, (y * 16 - self.draw_offset[1])))
                if 0 < (y + self.world.grid_size[0]) < len(self.dynamicobjectsstore):
                    assert pygame.display.get_init()
                    for x in self.dynamicobjectsstore[y + self.world.grid_size[0]]:
                        if not self.focus or self.focus.visible[x.position] == 2:
                            x.draw(surface, ((x.position[0] + x.position[1]) * 32 - self.draw_offset[0],
                                             y * 16 - self.draw_offset[1]))
            Window.draw(self, surface)


class LogWindow(Window):
    """A window, to be used like a file, that creates a surface of what has been inputted into it"""

    def __init__(self, font, imageCage, **other):
        """Most varables are self-explanatory, but it's important to have a stdout keyword argument, refering to
        something to forward output to after it's been processed,
        and autorender is a dangerous option that refreshes the screen and flushes some of pygames quires when something
        is writen to the file"""
        Window.__init__(self, imageCage)
        self.data = other
        self.lines = []
        self.font = font
        self.numlines = 100
        self.wrapper = textwrap.TextWrapper(width=self.size[0] / 8)
        self.wrapper.drop_whitespace = False
        if "stdout" not in self.data:
            self.data["stdout"]=None
        else:
            pass
        if "antialias" not in self.data:
            self.data["antialias"] = True

    def flush(self):
        self.data["stdout"].flush()

    def getpid(self):
        self.data["stdout"].getpid()

    def setSize(self, size):
        Window.setSize(self, size)
        self.numlines = self.size[1] / 18
        self.wrapper.width = self.numlines

    def draw(self, surface):
        if self.dirty:
            surface.fill((0, 0, 0))
            linenum = 0
            for line in self.lines[-self.numlines:]:
                linenum += 1
                clr = line[:3]

                color = [255, 255, 255]
                if len(clr) == 3 and clr[1] == "}":
                    line = line[2:]
                    if clr[0] == "0" or clr[0] == "g":
                        color = [200, 200, 200]
                    elif clr[0] == "1" or clr[0] == "R":
                        color = [255, 0, 0]
                    elif clr[0] == "2" or clr[0] == "W":
                        color = [255, 255, 255]
                    elif clr[0] == "3" or clr[0] == "G":
                        color = [0, 255, 0]
                    elif clr[0] == "4" or clr[0] == "Y":
                        color = [0, 255, 255]
                    elif clr[0] == "5" or clr[0] == "B":
                        color = [0X2b, 0Xa3, 0Xab]
                surface.blit(self.font.render(line.strip(), self.data["antialias"], color),
                             [32, 16 * linenum])
            Window.draw(self, surface)
        
    def write(self, text):
        if text == "\b":
            try:
                self.lines[-1]=self.lines[-1][:-1]
                if len(self.lines[-1])==0 or (len(self.lines[-1])==2 and self.lines[-1][1]=="}"):
                    del self.lines[-1]
            except IndexError:
                self.data["stdout"].write("INVALID BACKSPACE")
        else:
            if len(self.lines)==0 or self.lines[-1].endswith("\n"):
                line = text
            else:
                line = self.lines.pop() + text
            if len(line) >= 2 and line[1] == "}":
                splitlines = self.wrapper.wrap(line[2:])
                color = line[0]
            else:
                splitlines = self.wrapper.wrap(line)
                color = "W"
            for i in splitlines:
                self.lines.append(color+"}"+i)
            if text.endswith("\n"):
                self.lines[-1] += "\n"
        self.dirty = True


class StatWindow(Window):
    """A window that renders the stats of a PlayerObject or a subcass. Records stats from xp, and any status messages, converted via the constants dict
    The messages are outlines so they are equidistant. Colored low HP may be supported in the future"""

    def __init__(self, cage, font, trackmonster):
        Window.__init__(self, cage)
        self.trackmonster = trackmonster
        self.font = font

    def draw(self, surface):
        if self.trackmonster.getStatsDirty():
            self.dirty = True
            surface.fill([0, 0, 0])
            strings = []
            for i in self.trackmonster.stats:
                strings.append(str(i) + ":" + str(self.trackmonster.stats[i]))
            if hasattr(self.trackmonster, "body"):
                strings.append("HP:{0:.1f}/{1}".format(self.trackmonster.body.health, self.trackmonster.body.maxhealth))
            strings.extend(flag_uncode[i] for i in self.trackmonster.status_messages if i in flag_uncode.keys())
            sperstring = self.size[0] / len(strings)
            for i in range(len(strings)):
                s = self.font.render(strings[i], 1, [255, 255, 255])
                surface.blit(s, [10 + sperstring * i, (self.size[1] - s.get_height()) / 2])

            Window.draw(self, surface)


class InventoryWindow(Window):
    """Right now, has a list of inventory, and armor when clikced on the right side, should probably be split up later"""

    def __init__(self, font, imageCage, trackmonster):
        Window.__init__(self, imageCage)
        self.scroll = 0
        self.selected = None
        self.tab = "inv"
        self.font = font
        self.trackmonster = trackmonster

    def draw(self, surface):
        if self.trackmonster.getInvDirty() or self.dirty:
            self.dirty = True
            surface.fill((0, 0, 0))
            tm = self.trackmonster
            ypos = -self.scroll
            if self.tab == "inv":
                for item in self.trackmonster.inventory:
                    if tm.inventory[item][0].image.get_height() == 64:
                        surface.blit(tm.inventory[item][0].image.toSurf(), [5, ypos])
                    else:
                        surface.blit(tm.inventory[item][0].image.toSurf(), [5, ypos - 32])
                    nm = self.trackmonster.getitemname(tm.inventory[item][0], p=(len(tm.inventory[item]) != 1))
                    weight = tm.inventory[item][0].getWeight() * len(tm.inventory[item])
                    surface.blit(self.font.render(
                        item + ": " + str(len(tm.inventory[item])) + " " + str(nm) + " (" + str(weight) + "g)", 1,
                        [255, 255, 255]),
                        [74, ypos])

                    ypos+=65
            elif self.tab == "arm":
                ypos += 30
                surface.blit(self.font.render("Active slots: ", 1, [255, 255, 255]), (74, ypos))
                ypos += 60
                for letter in self.trackmonster.equipment_letters:
                    item = self.trackmonster.equipment_letters[letter]
                    surface.blit(tm.equipment[item].image.toSurf(), [5, ypos])
                    nm = self.trackmonster.getitemname(tm.equipment[item])
                    surface.blit(self.font.render(item + ": (" + letter + ") " + str(nm), 1, [255, 255, 255]),
                                 (74, ypos))
                    ypos += 65
                ypos += 30
                surface.blit(self.font.render("all slots: ", 1, [255, 255, 255]), (74, ypos))
                ypos += 60
                for item in self.trackmonster.equipment:
                    if not self.trackmonster.equipment[item]:
                        surface.blit(self.font.render(item + ": Nothing", 1, [255, 255, 255]), (74, ypos))
                        ypos += 65
            Window.draw(self, surface)

    def addEvent(self, event):
        if event.type == pygame.MOUSEMOTION:
            if event.pos[0] > self.size[0] - 50:
                if self.tab == "inv":
                    totaldist = len(self.trackmonster.inventory) * 64 - self.size[1]
                else:
                    totaldist = len(self.trackmonster.equipment) * 64 - self.size[1] + 90  # 90 compensates for header
                if totaldist > 0:
                    self.scroll = int(event.pos[1] / float(self.size[1]) * totaldist)
                    self.dirty = True
                    return True
            return False
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.size[1] - event.pos[1] > 20:
                if event.pos[0] > (self.size[0] / 2):
                    self.tab = "inv"
                    self.scroll = 0
                else:
                    self.tab = "arm"
                    self.scroll = 0
                self.dirty = True
                return True
            else:
                return False
        else:
            return False
