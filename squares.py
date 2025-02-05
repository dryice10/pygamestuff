import os
import pygame
from pygame.math import Vector2
import random

"""
https://www.patternsgameprog.com/discover-python-and-patterns-12-command-pattern/
https://www.patternsgameprog.com/discover-python-and-patterns-20-better-commands


char observations?:
x y coords
areas within X tiles (probably closest 5-10)
-get distance and type
should characters be a subclass of area?
"""


os.environ['SDL_VIDEO_CENTERED'] = '1'
WINDOW_X = 500
WINDOW_Y = 500
FPS = 15


def collideBasic(x,y,w,h,x2,y2,w2,h2):
    if (x + w > x2 and x < x2 + w2
        and y + h > y2 and y < y2 + h2):
        return True
    else: return False

class Character():
    def __init__(self,gamestate,selected,maxHp,x,y):
        self.size = 20
        self.w = self.size
        self.h = self.size
        self.x = x
        self.y = y
        self.speed = 10
        self.alive = True
        self.gamestate = gamestate
        self.selected = selected
        self.maxHp = maxHp
        self.hp = maxHp
        self.color = (20,20,255)

    def addHp(self, amount):
        self.hp += amount
        #cap at max
        if self.hp > self.maxHp:
            self.hp = self.maxHp
        return
    
    def removeHp(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            print(str(self) + " died :(")
            self.die()
        return

    def die(self):
        self.alive = False
        self.speed = 0
        self.color = (0,0,180)
        return
    
    def collideArea(self, area):
        return collideBasic(self.x,self.y,self.w,self.h,area.x,area.y,area.w,area.h)

    def doMove(self, moveVector):
        newx = (self.x + moveVector.x * self.speed)
        newy = (self.y + moveVector.y * self.speed)
        #don't move ouside window
        if (newx < 0 or newx + (self.size - self.speed) >= WINDOW_X 
            or newy < 0 or newy + (self.size - self.speed) >= WINDOW_Y):
            return
        #don't move into other chars
        for otherChar in self.gamestate.chars:
            if otherChar != self:
                if collideBasic(newx,newy,self.w,self.h,otherChar.x,otherChar.y,otherChar.w,otherChar.h):
                    return
        for area in self.gamestate.areas:
            #don't move into walls
            if area.areaType == 'wall':
                if collideBasic(newx,newy,self.w,self.h,area.x,area.y,area.w,area.h):
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

    #active is ran on all alive things
    def Active(self):
        if self.alive and not self.selected:
            self.randomMove()
        for area in self.gamestate.areas:
            #eat fruit
            if area.areaType == 'fruit':
                if self.collideArea(area):
                    print("ate: "+ str(area))
                    self.gamestate.areas.remove(area)
                    area.bush.fruits[area.index] = None
                    self.addHp(10)
            #get hurt
            if area.areaType == 'danger':
                if self.collideArea(area):
                    self.removeHp(1)  
        return


class Area():
    def __init__(self,gamestate,areaType,color,x,y,w,h):
        self.gamestate = gamestate
        self.areaType = areaType
        self.color = color
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        return
    
    def Active(self):
        return
    
class Bush(Area):
    def __init__(self,gamestate,x,y):
        areaType = 'bush'
        self.color = (0,255,0)
        self.w = 40
        self.h = 40
        self.timerMax = 15
        self.timer = self.timerMax
        self.spots = [Vector2(0, 0),Vector2(30, 0),Vector2(0, 30),Vector2(30, 30)]
        self.fruits = [None, None, None, None]
        self.maxFruit = 4
        super().__init__(gamestate,areaType,self.color,x,y,self.w,self.h)
    
    def Active(self):
        if self.timer == 0:
            self.growFruit()
            self.timer = self.timerMax
        else:
            self.timer -= 1
        return

    def growFruit(self):
        #chance to grow fruit
        amount = len([f for f in self.fruits if f is not None])
        odds = [0.5, 0.5, 0.5, 0.5]
        if amount < self.maxFruit:
            choice = random.random()
            if choice < odds[amount]:
                self.gamestate.areas.append(Fruit(self))
        return

class Fruit(Area):
    def __init__(self,bush):
        self.bush = bush
        self.areaType = 'fruit'
        self.fruitx, self.fruity = self.fruitSpot(self.bush)
        self.w = 10
        self.h = 10
        self.color = (100,10,10)
        super().__init__(self.bush.gamestate, self.areaType, self.color, self.fruitx,self.fruity,self.w,self.h)
        return

    def fruitSpot(self,bush):
        #checks the fruit list for a spot to grow
        x, y = 0, 0
        for i in range(bush.maxFruit):
            if bush.fruits[i] is None:
                bush.fruits[i] = self
                self.index = i
                x = bush.spots[i].x + bush.x
                y = bush.spots[i].y + bush.y
                print(bush.fruits)
                return x, y
            #do a check for character in the way?
        return

class GameState():
    def __init__(self):
        self.chars = [
            Character(self, False,  100, 120, 120),
            Character(self, False,  100, 220, 220),
            Character(self, False, 100, 280, 220),
            Character(self, False, 100, 350, 300)
        ]
        self.areas = [
            Area(self, 'danger',(255,0,0), 0, 0, 200, 80),
            Area(self, 'danger',(255,0,0), 400, 300, 60, 80),
            Area(self, 'wall',  (150,150,150), 100, 360, 10, 100),
            Area(self, 'wall',  (150,150,150), 180, 360, 10, 100),
            Area(self, 'wall',  (150,150,150), 350, 150, 150, 10),
            Area(self, 'wall',  (150,150,150), 450, 100, 10, 150),

            Bush(self,200,400),
            Bush(self,40,120),
            Bush(self,320,60)
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

    def update(self):
        for char in self.chars:
            if char.alive:
                char.Active()
        for area in self.areas:
            area.Active()
        # for cmd in self.cmds:
        #     return
        return

class UserInterface():
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_X,WINDOW_Y))
        pygame.display.set_caption("squares")
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
        self.gameState.update()
        for char in self.gameState.chars:
            if char.selected:
                if self.moveVector != Vector2(0,0):
                    char.doMove(self.moveVector)
        #only send mouse command on click
        if self.mouseCommand[2] == True:
            self.gameState.mouseSelect(self.mouseCommand)

    def render(self):
        self.window.fill((10,15,10))
        for area in self.gameState.areas:
            if area.areaType == 'bush':
                #special draw for bush and fruit
                pygame.draw.rect(self.window,area.color,((area.x - 1),(area.y - 1),(area.w + 2),(area.h + 2)))
                for fruit in area.fruits:
                    if fruit is not None:
                        pygame.draw.rect(self.window,fruit.color,(fruit.x,fruit.y,fruit.w,fruit.h))
            else:
                #everything else uses one draw call
                pygame.draw.rect(self.window,area.color,(area.x,area.y,area.w,area.h))
        
        for char in self.gameState.chars:
            #draw char
            pygame.draw.rect(self.window,char.color,(char.x,char.y,char.w,char.h))
        pygame.display.update()


    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(FPS)

userInterface = UserInterface()
userInterface.run()

pygame.quit()