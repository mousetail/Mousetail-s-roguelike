'''
Created on 8 jan. 2015

@author: Maurits
'''
import generator

def generate(pipe1):
    pipe1.send("starting...")
    while True:
        if pipe1.poll():
            t=pipe1.recv()
            if t=="gener":
                pipe1.send("starting...")
                
                level=pipe1.recv()
                size=pipe1.recv()
                g=generator.Generator(size, level)
                objects=g.generate()
                pipe1.send("done")
                pipe1.send(g)
                pipe1.send(objects)
            elif t=="quit":
                break
    return
        
