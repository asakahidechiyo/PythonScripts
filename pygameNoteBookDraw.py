import pygame
from pygame.locals import *


def drawNoteBook(surface, sizeX, sizeY):
    blue = (0, 0, 200)
    red = (200, 0, 0)
    white = (255, 255, 255)
    surface.fill(white)
    for y in range(60, sizeY, 20):
        leftSide = (0, y)
        rightSide = (sizeX, y)
        pygame.draw.line(surface, blue, leftSide, rightSide)
    pygame.draw.line(surface, red, (25, 0), (25, sizeY))


def main():
    pygame.init()
    pygame.key.stop_text_input()
    window_size_x = 400
    window_size_y = 600
    surface = pygame.display.set_mode([window_size_x, window_size_y])
    pygame.display.set_caption("Notepaper, now with drawing")

    bDrawing = False
    lastPos = None
    BLACK = (0, 0, 0)
    nThickness = 3
    bRunning = True

    canvas = pygame.Surface([window_size_x, window_size_y])
    drawNoteBook(canvas, window_size_x, window_size_y)
    while bRunning:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                bRunning = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                bDrawing = True
                lastPos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                bDrawing = False
                lastPos = None
            elif event.type == pygame.MOUSEMOTION:
                if bDrawing and lastPos:
                    curPos = event.pos
                    pygame.draw.line(canvas, BLACK, lastPos, curPos, nThickness)
                    lastPos = curPos
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    bRunning = False
                elif event.key == pygame.K_c:
                    drawNoteBook(canvas, window_size_x, window_size_y)
                    surface.blit(canvas, (0, 0))
        surface.blit(canvas, (0, 0))
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
