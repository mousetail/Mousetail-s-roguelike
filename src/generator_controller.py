'''
Created on 8 jan. 2015

@author: Maurits
'''
import generator

def generate(pipe):
    while True:
        if pipe.poll():
            t=pipe.recv()
            if t=="gener":
                level=pipe.recv()
                size=pipe.recv()
                g=generator.Generator(size, level)
                g.generate()
                pipe.send(g)
            elif t=="quit":
                break
    return
        
