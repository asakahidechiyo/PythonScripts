import random
import sys

import pygame
from pygame.locals import *  # noqa: F403
from rich.progress import track


def drawRect(surface, color, width):
    points = [(0, 0), (200, 0), (200, 100), (0, 100)]
    # pygame.draw.lines(surface, color, False, points, width)
    pygame.draw.polygon(surface, BLACK, points, width)


def getNextRand(n):
    # a, c, m = 1664525, 1013904223, 4294967296
    a, c, m = 7, 3, 45
    return (a * n + c) % m


def getCycleLen(t):
    cnt = 1
    for i in range(1, len(t)):
        if t[i] == t[0]:
            return cnt
        cnt += 1


def Cycle():
    solveList = []
    iList = []
    for j in track(range(100)):
        nextInt = 1
        solveList = []
        for index in range(1, 1000):
            for i in range(1000):
                iList.append(nextInt)
            nextInt = getNextRand(nextInt)
        solveList.append(getCycleLen(iList))
    print(list(solveList))


def RollDice(nDices, nSides):
    # dice range from 1-nSides
    dices = []
    # roll 1
    for i in range(nDices):
        dices.append(random.randint(1, nSides))
    dices = sorted(dices)
    dices[0] = random.randint(1, nSides)
    sum = 0
    for dice in dices:
        sum += dice
    # print(list(dices))
    # print(sum)
    return sum


pygame.init()
DISPLAYSURF = pygame.display.set_mode((500, 400), 0, 32)
anotherSurface = DISPLAYSURF.convert_alpha()
pygame.display.set_caption("New Sekai")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

DISPLAYSURF.fill(WHITE)
spamRect = pygame.Rect(10, 20, 200, 300)
# pygame.draw.polygon(DISPLAYSURF,GREEN,((146,0),(291,106),(236,277),(56,277),(0,106)))
# pygame.draw.rect(DISPLAYSURF,RED,spamRect)
r = pygame.Rect(0, 0, 200, 100)
# pygame.draw.rect(DISPLAYSURF,BLACK,r,10)
drawRect(DISPLAYSURF, BLACK, 5)
DISPLAYSURF.set_at((400, 300), BLUE)

cnt = 0
for i in track(range(10000000)):
    if RollDice(4, 5) == 17:
        cnt += 1
print(cnt / 10000000)

while True:  # main game loop
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
