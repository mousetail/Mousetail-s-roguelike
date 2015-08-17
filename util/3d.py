import pygame
pygame.init()
screen=pygame.display.set_mode((1000,600))
screen.fill((0,0,0))

cube=[]
for x in (-1,1):
    for y in (-1,1):
        for z in (-1,1):
            t=[x,y,z]
            for w in range(3):
                t2=t[:]
                t2[w]=-t2[w]
                cube.append((t,t2))

rotation=0
running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    screen.fill((0,0,0))
    for line in cube:
        points=[]
        for p in line:
            mul=500/(2+p[1])
            points.append((int(p[0] * mul + 500),int(p[2]*mul+300)))
        pygame.draw.line(screen,(255,255,255),*points)
    pygame.display.flip()
pygame.quit()
