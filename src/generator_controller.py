'''
Created on 8 jan. 2015

@author: Maurits
'''
import generator, sys, time

def generate(pipe1):
    pipe1.send("starting...")
    while True:
        t=pipe1.recv()
        if t=="gener":
            pipe1.send("starting...")
            
            level=pipe1.recv()
            size=pipe1.recv()
            
            pipe1.send(str(generator))
            time.sleep(1)
            g=generator.Generator(size, level, pipe=pipe1)
            pipe1.send("made object...")
            objects=g.generate()
            pipe1.send("done")
            pipe1.send(g)
            pipe1.send(objects)
        elif t=="quit":
            break
    return
        
