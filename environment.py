import pygame
import numpy as np
import os
import random
from math import sqrt
import gym


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
    
    def distanceA(self,area):
        return sqrt((area.x - self.x)**2 + (area.y - self.y)**2)
    
    def distanceChar(self,char):
        return sqrt((char.x - self.x)**2 + (char.y - self.y)**2)

### Observations ###

    def nearestObs(self):
        distList = []
        typeList = []
        for area in self.gamestate.areas:
            distList.append(self.distanceA(area))
            typeList.append(area.areaType)
        for otherChar in self.gamestate.chars:
            if otherChar != self:
                distList.append(self.distanceChar(otherChar))
                typeList.append('char')
        for item in typeList:
            if item == 'char':
                item = 1
            elif item == 'wall':
                item = 2
            elif item == 'danger':
                item = 3
            elif item == 'bush':
                item = 4
            elif item == 'fruit':
                item = 5
            else:
                item = 0
        zipped = zip(distList, typeList)
        sorted = list(sorted(zipped, key=lambda item: item[0]))
        return sorted

    def updateObservations(self):
        #position can be normed to -1,1
        #distances to 0,1
        #labels are ints

        xobs = np.interp(self.x, [0.0, WINDOW_X], [-1, 1])
        yobs = np.interp(self.y, [0.0, WINDOW_Y], [-1, 1])
        
        #distance and labels
        thingsList = self.nearestObs[:5]
        distances, types = zip(*thingsList)
        distances = list(distances)
        for dist in distances:
            dist = np.interp(dist, [0.0, 500], [0, 1])
        #######
        ##TODO
        ##np.concatenate the vectors
        #######
        return
    
### Receives Action ###

    def doMove(self, moveVector):
        newx = (self.x + moveVector[0] * self.speed)
        newy = (self.y + moveVector[1] * self.speed)
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
                self.doMove((0,-1))
            elif choice == 2: #down
                self.doMove((0,1))
            elif choice == 3: #left
                self.doMove((-1,0))
            elif choice == 4: #right
                self.doMove((1,0))
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
        self.spots = [(0, 0),(30, 0),(0, 30),(30, 30)]
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
                x = bush.spots[i][0] + bush.x
                y = bush.spots[i][1] + bush.y
                print(bush.fruits)
                return x, y
            #do a check for character in the way?
        return

class GameState():
    def __init__(self):
        self.chars = [
            Character(self, True,  100, 120, 120),
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

class UserInterface(gym.Env):      ##
    def __init__(self):
        #self.observation_space = gym.spaces.Box()
        self.action_space = gym.spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(2,),
            dtype=float
        )
        self.gameState = GameState()
        self.running = True
        self.moveVector = [0,0]
        self.mouseCommand = [0,0,False]

    def init_render(self):
        import pygame
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_X,WINDOW_Y))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("squares")

    # def reset(self):
    #TODO
    #     return observation

    def step(self, action):
        self.gameState.update()
        for char in self.gameState.chars:
            if char.selected:
                if (action[0] != 0 or action[1] != 0):
                    char.doMove(action)
        # #only send mouse command on click
        # if self.mouseCommand[2] == True:
        #     self.gameState.mouseSelect(self.mouseCommand)

        observation, reward, done, info = 0, 0, False, {}
        
        return observation, reward, done, info


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

    #def run(self):
       # while self.running:
            #self.processInput()
            #self.update()
            #self.render()
            #self.clock.tick(FPS)

def input_to_action():
    global run
    moveX = 0
    moveY = 0    
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break
                elif event.key == pygame.K_RIGHT:
                    moveX, moveY = (1,0)
                elif event.key == pygame.K_LEFT:
                    moveX, moveY = (-1,0)
                elif event.key == pygame.K_DOWN:
                    moveX, moveY = (0,1)
                elif event.key == pygame.K_UP:
                    moveX, moveY = (0,-1)

    return np.array([moveX,moveY])

environment = UserInterface()
environment.init_render()
run = True
while run:
    action = (0,0)
    environment.clock.tick(FPS)
    action = input_to_action()
    environment.step(action)
    environment.render()
pygame.quit()
