'''
Created on 14 jul. 2015

A function to calculate number of drops

@author: Maurits
'''
import random


def calculateDrops(world, cage, drops, position=(0, 0, 0), addtoworld=False):
    gen = world.itemPicker
    itms = []
    # print drops
    for i in drops:
        # print i, len(i)
        if random.random()<i[0]:
            for k in range(i[1]):
                if isinstance(i[2],str):
                    itms.append(gen.fastItemByName(i[2],position,world,cage))
                elif isinstance(i[2],list) or isinstance(i[2],tuple):
                    itms.append(gen.fastRandomItem(position,world,cage,0,i[2]))
                else:
                    raise ValueError(i[2])
    if addtoworld:
        for i in itms:
            world.spawnItem(i)
    return itms
