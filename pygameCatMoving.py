import sys
import pygame
from pygame.locals import *

pygame.init()
FPS = 120
fpsClock = pygame.time.Clock()

DISPLAYSURF = pygame.display.set_mode((1200, 900), 0, 32)
anotherSurface = DISPLAYSURF.convert_alpha()
pygame.display.set_caption("CatMoving")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
catImg = pygame.image.load("cat.png")
catx = 10
caty = 10
step = 3
direction = "right"

while True:  # main game loop
    DISPLAYSURF.fill(WHITE)

    if direction == "right":
        catx += step
        if catx >= 300 * 3:
            direction = "down"
    elif direction == "down":
        caty += step
        if caty >= 240 * 3:
            direction = "left"
    elif direction == "left":
        catx -= step
        if catx <= 10:
            direction = "up"
    elif direction == "up":
        caty -= step
        if caty <= 10:
            direction = "right"
    DISPLAYSURF.blit(catImg, (catx, caty))

    for event in pygame.event.get():  # 获取操作事件列表event
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            catx, caty = event.pos
    pygame.display.update()
    fpsClock.tick(FPS)
