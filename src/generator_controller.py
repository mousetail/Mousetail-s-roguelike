'''
Created on 8 jan. 2015

@author: Maurits
'''
import generator, sys, time

def generate(pipe1):
    pipe1.send("starting...")
    generating=False
    g=None
    level=None
    objects=None
    size=None
    roomsdone=0
    roomstodo=0
    running=True
    waitingfor=None
    
    
    while running:
        if pipe1.poll() or not generating:
            t=pipe1.recv()
            
            if t=="quit":
                running=False
            elif not generating:
                if waitingfor == "level":
                    level = t
                    waitingfor = "size"
                elif waitingfor == "size":
                    size = t
                    waitingfor = "start"
                    generating = True
                    numstats = 0
                    roomsdone = 0
                    g=generator.Generator(size, level)
                elif t == "stop":
                    pass
                elif t == "gener":
                    waitingfor = "level"
                elif t == "retu":
                    pipe1.send(g)
                    pipe1.send(objects)
                elif t == "stat":
                    pipe1.send(0)  # 0 signals the generation to not be active, which usually means it finished
                    numstats += 1
                else:
                    raise ValueError(str(t)+" is not a option I know of")
            else:  # if generating
                if t == "stat":
                    numstats += 1
                    pipe1.send(roomsdone + 1)  # 0 is the quit code, so I add one so it can never be 0
                elif t == "stop":
                    generating = False
                elif t == "retu":
                    pipe1.send(None)
                else:
                    raise ValueError(str(t)+" is not an option I know of while generating")
        elif generating:
            if waitingfor == "start":
                g.start()
                waitingfor = None
                roomstodo = g.numrooms  # the generator wants to know how many rooms to generate

            elif roomsdone < roomstodo:
                f=g.step()
                if f:
                    roomsdone += 1
                else:
                    objects = g.finish()  # the last part of generation - filling the map, scanning it for errors, deciding
                    # on the positions of objects,
                    # takes a lot of time, allmost as much as all the rooms together, especially
                    # with the reduced tries. I might
                    # want to split this up so I can send a status report in between
                    generating=False
                    roomsdone=0
            else:
                objects = g.finish()
                generating = False
                roomsdone = 0
