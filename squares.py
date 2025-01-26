import os
import pygame
from pygame.math import Vector2
import random

"""
https://www.patternsgameprog.com/discover-python-and-patterns-12-command-pattern/
https://www.patternsgameprog.com/discover-python-and-patterns-20-better-commands
"""


os.environ['SDL_VIDEO_CENTERED'] = '1'
windowx = 640
windowy = 480

class Character():
    def __init__(self,gamestate,selected,health,x,y):
        self.size = 30
        self.speed = 10
        self.gamestate = gamestate
        self.selected = selected
        self.health = health
        self.x = x
        self.y = y

    def doMove(self,moveVector):
        newx = self.x + (moveVector.x * self.speed)
        newy = self.y + (moveVector.y * self.speed)
        #don't move ouside window
        if (newx < 0 or newx + 20 >= windowx 
            or newy < 0 or newy + 20 >= windowy):
            return
        #don't move into other chars
        for otherChar in self.gamestate.chars:
            if (otherChar != self and
                newx + self.size > otherChar.x and newx < otherChar.x + otherChar.size 
                and newy + self.size > otherChar.y and newy < otherChar.y + otherChar.size):
                return
        #don't move into walls
        for area in self.gamestate.areas:
            if (area.areaType == 'wall' and
                newx + self.size > area.x and newx < area.x + area.w 
                and newy + self.size > area.y and newy < area.y + area.h):
                return

        self.x = newx
        self.y = newy
        return

    def randomMove(self):
        choice = random.random()
        #percent chance to move or pass
        if choice < 0.5:
            choice = random.randint(1, 4)
            if choice == 1: #up
                self.doMove(Vector2(0,-1))
            elif choice == 2: #down
                self.doMove(Vector2(0,1))
            elif choice == 3: #left
                self.doMove(Vector2(-1,0))
            elif choice == 4: #right
                self.doMove(Vector2(1,0))
        else:
            pass
        return


class Area():
    def __init__(self,gamestate,areaType,x,y,w,h):
        self.gamestate = gamestate
        self.areaType = areaType
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        return
    

class GameState():
    def __init__(self):
        self.chars = [
            Character(self, True, 100, 120, 120),
            Character(self, True, 100, 220, 220),
            Character(self, False, 100, 280, 220),
            Character(self, False, 100, 350, 300)
        ]
        self.areas = [
            Area(self, 'danger', 0, 0, 200, 80),
            Area(self, 'danger', 400, 300, 60, 80),
            Area(self, 'wall', 100, 330, 20, 120),
            Area(self, 'wall', 180, 330, 20, 120),
            Area(self, 'wall', 350, 150, 150, 20),
            Area(self, 'wall', 450, 100, 20, 150)
        ]
    #control other squares
    def mouseSelect(self,mouseCommand):
        if mouseCommand[2] == True:
            for char in self.chars:
                if (mouseCommand[0] > char.x and mouseCommand[0] < char.x + char.size 
                    and mouseCommand[1] > char.y and mouseCommand[1] < char.y + char.size):
                    for char2 in self.chars:
                        char2.selected = False
                    char.selected = True
                    return

class UserInterface():
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((windowx,windowy))
        #pygame.display.set_caption("Discover Python & Patterns - https://www.patternsgameprog.com")
        #pygame.display.set_icon(pygame.image.load("icon.png"))
        self.clock = pygame.time.Clock()
        self.gameState = GameState()
        self.running = True
        self.moveVector = Vector2(0,0)
        self.mouseCommand = [0,0,False]

    def processInput(self):
        self.moveVector = Vector2(0,0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    self.moveVector = Vector2(1,0)
                elif event.key == pygame.K_LEFT:
                    self.moveVector = Vector2(-1,0)
                elif event.key == pygame.K_DOWN:
                    self.moveVector = Vector2(0,1)
                elif event.key == pygame.K_UP:
                    self.moveVector = Vector2(0,-1)
            
            mouse = pygame.mouse.get_pos()
            self.mouseCommand[0] = mouse[0]
            self.mouseCommand[1] = mouse[1]
            pressed = pygame.mouse.get_pressed() #returns a list of bool
            self.mouseCommand[2] = pressed[0]


    def update(self):
        for char in self.gameState.chars:
            if char.selected:
                char.doMove(self.moveVector)
            else:
                char.randomMove()
        self.gameState.mouseSelect(self.mouseCommand)

    def render(self):
        self.window.fill((0,0,0))
        for area in self.gameState.areas:
            if area.areaType == 'danger':
                pygame.draw.rect(self.window,(255,0,0),(area.x,area.y,area.w,area.h))
            if area.areaType == 'wall':
                pygame.draw.rect(self.window,(150,150,150),(area.x,area.y,area.w,area.h))

        for char in self.gameState.chars:
            pygame.draw.rect(self.window,(0,0,255),(char.x,char.y,char.size,char.size))
        pygame.display.update()

    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(15)

userInterface = UserInterface()
userInterface.run()

pygame.quit()