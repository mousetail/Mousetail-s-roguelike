'''
Created on 29 dec. 2014

@author: Maurits
'''
import pygame
import player_input
import generator_controller
import multiprocessing
import XMLloading
import constants
import imagecage

import os
import pickle


class SpecialPickler(pickle.Pickler):
    def __init__(self, world, file):
        pickle.Pickler.__init__(self, file, 2)
        self.world = world

    def persistent_id(self, obj):
        # type: (object) -> str
        if obj is self.world:
            return "O_WORLD"
        elif obj is self.world.player:
            return "O_PLAYER"
        elif obj is self.world.cage:
            return "O_CAGE"
        elif isinstance(obj, imagecage.ImageProxy):
            return "surf: " + obj.name


class SpecialUnpicker(pickle.Unpickler):
    def __init__(self, world, file):
        pickle.Unpickler.__init__(self, file)
        self.world = world

    def persistent_load(self, obj):
        if obj == "O_WORLD":
            return self.world
        elif obj == "O_PLAYER":
            return self.world.player
        elif obj == "O_CAGE":
            return self.world.cage
        elif obj.startswith("surf: "):
            return imagecage.ImageProxy(self.world.cage, obj[6:])
        else:
            raise IndexError(obj)


class World(object):
    '''
    It is a level object that will change if levels change
    A class that keeps track of:
    *The grid
    *The object list
    *a light table(if I implement one)
    *Level generation
    '''

    def __init__(self, size=(50, 50), cage=None):
        '''
        Constructor
        '''
        self.levelToLoad = None
        self.grid = None
        self.level = -1
        self.objects = []
        self.player = None
        self.focus = None
        self.grid_size = size
        self.pipe = multiprocessing.Pipe()
        self.proc = multiprocessing.Process(target=generator_controller.generate, args=(self.pipe[1],))
        print self.proc.start()
        print self.pipe[0].recv()
        self.startGenerLevel(1)
        self.dungeon_level = 1
        self.itemPicker = XMLloading.XMLloader()
        self.itemPicker.loadFile(os.path.join("..", "data", "human.xml"))
        self.itemPicker.flush()
        self.cage = cage
        print ("Waiting for level to generate...")

        self.savePoint = "tmp_save"  # when I have a menu, change this to some usefull directory
        for file in os.listdir(self.savePoint):
            print "removing: "
            os.remove(os.path.join(self.savePoint, file))

        self.doLoadLevel(1)

        self.dirty = True
        self.objindex = 0
        self.newround = False

    def finalize(self):
        print(dir(self.proc))
        self.proc.terminate()

    def startGenerLevel(self, level):
        self.pipe[0].send("stop")
        self.pipe[0].send("gener")
        self.pipe[0].send(level)
        self.pipe[0].send(self.grid_size)
        self.levelBeingGenerated = level

    def loadLevel(self, level, direction="DOWN"):
        # level will be loaded at the end of the turn
        self.levelToLoad = level, direction

    def doLoadLevel(self, level, direction="DOWN"):
        print "R} Loading level " + str(level)
        if self.player:
            self.saveLevel()
        if self.level == level:
            print "No level change"
            return
        elif self.levelBeingGenerated == level:
            print "loading level from generator..."
            assert not self.pipe[0].poll(), "Some leftover information got stuck before loop"
            numstats = 0
            status = 1

            while status:
                self.pipe[0].send("stat")
                numstats += 1
                status = self.pipe[0].recv()
                assert not self.pipe[0].poll(), "Halfway loop, extra stuff got stuck"

            assert not self.pipe[0].poll(), "Some leftover information got stuck"
            self.pipe[0].send("retu")

            self.grid = self.pipe[0].recv()
            objects = self.pipe[0].recv()
            self.objects = []

            playerPos = self.grid.exits[direction]
            if self.player is None:
                pbody = self.itemPicker.fastItemByName("human", playerPos, self, self.cage, returnbody=True)
                self.objects.append(player_input.PlayerObject(playerPos, pbody, self.cage, self, True))
                self.focus = self.objects[-1]
                self.player = self.focus
            else:
                self.player.setPosition(playerPos)
                self.objects.append(self.player)
                self.player.setLevelSpecificState(self.player.getDefaultLevelSpecificState())

            for i in objects:
                try:
                    assert len(i[0]) == 3
                    self.objects.append(self.itemPicker.fastRandomItem(i[0], self, self.cage, level, (i[1],)))
                except IndexError:
                    print "r} CANT FIND OBJ FOR TAGS", i[1]

            self.objects.append(player_input.ObjectSpawner(self, 2, self.dungeon_level))
            for i in range(100):
                if not os.path.exists(os.path.join(self.savePoint, str(i + level))):
                    self.startGenerLevel(str(i + level))
                    break
        elif os.path.exists(os.path.join(self.savePoint, str(level))):
            print "Loading level..."
            with open(os.path.join(self.savePoint, str(level)), 'rb') as f:
                picker = SpecialUnpicker(self, f)
                print "loading objects..."
                self.objects[:] = picker.load()
                print "loading grid..."
                self.grid = picker.load()
                self.player.setLevelSpecificState(picker.load())
                self.player.setPosition(self.grid.exits[direction])
                print self.player
        else:
            print "starting generation..."
            self.startGenerLevel(level)
            self.doLoadLevel(level, direction)
        self.level = level

    def saveLevel(self):
        if not os.path.exists(self.savePoint):
            os.mkdir(self.savePoint)
        with open(os.path.join(self.savePoint, str(self.level)), 'wb') as f:
            pickler = SpecialPickler(self, f)
            pickler.dump(self.objects)
            pickler.dump(self.grid)
            pickler.dump(self.player.getLevelSpecificState())

    def update(self):
        """
        first calls update on all objects (for updating animations)
        then calculates who'se turn it is to move, then returns to
        3d_render
        """
        self.dirty = False
        for i in self.objects:
            if hasattr(i, "update"):
                self.dirty = self.dirty or i.update()
        deadobj = []
        for obj in self.objects:
            if hasattr(obj, "dead") and obj.dead:
                deadobj.append(obj)
        for obj in deadobj:
            self.objects.remove(obj)
            if self.player == deadobj:
                # self.player=None
                pass
        while True:
            if self.objindex >= len(self.objects):
                self.objindex = 0
                if not self.newround:

                    for i in self.objects:
                        if hasattr(i, "action_points"):
                            if hasattr(i, "getspeed"):
                                i.action_points += i.getspeed()
                            else:
                                i.action_points += i.speed
                else:

                    self.dirty = True
                    self.newround = False
                    break

                self.newround = False
            elif isinstance(i, player_input.PlayerObject):
                pass
            i = self.objects[self.objindex]
            if hasattr(i, "action_points") and i.action_points > 0:
                if hasattr(i, "AIturn"):
                    i.AIturn()
                if hasattr(i, "gameTurn"):
                    if (not hasattr(i, "actions") or len(i.actions) > 0):
                        change = i.gameTurn()
                    else:
                        change = 0
                    if change <= 0:
                        break
                    else:
                        if not isinstance(i, player_input.MonsterObject):
                            pass
                        if hasattr(i, "body"):
                            i.body.get_visible()
                        if hasattr(i, "action_points"):
                            i.action_points -= change
                        self.newround = True

                else:
                    pass

            self.objindex += 1
        if self.levelToLoad is not None:
            self.doLoadLevel(*self.levelToLoad)
            self.levelToLoad = None
    def event(self, event):
        """passes on events to objects"""
        for i in self.objects:
            if hasattr(i, "receiveEvent"):
                i.receiveEvent(event)

    def spawnItem(self, *items):
        """adds one or more object to the world, preferable over adding it yourself"""
        for item in items:
            item.owner = self
            self.objects.append(item)

    def getsolid(self, position):
        return self.grid[position] in constants.WALLS

    def getcollisions(self, position):
        objs = []
        for i in self.objects:
            if hasattr(i, "position") and i.position[0] == position[0] and i.position[1] == position[1]:
                objs.append(i)
        return objs

    def quit(self):
        for i in self.objects:
            if hasattr(i, "quit"):
                i.quit()
        self.pipe[0].send("quit")
        self.proc.join(1)
        self.pipe[0].close()

    def getDirty(self):
        return self.dirty


if __name__ == "__main__":
    print "please run 3d_render.py"
    print dir(World)
    pygame.time.delay(5000)
