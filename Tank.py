#!/usr/bin/python3

import pygame
import os
import colorama
from rot_center import *
from Target import *

colorama.init()
def tankPrint(text):
    print(colorama.Fore.YELLOW + text + colorama.Style.RESET_ALL)

class Tank(pygame.sprite.Sprite):
    '''represents a tank,
    allows to move, change direction, shot
    turret moves seperatly'''

    toLeft = {  'up' : 'left',
                'left' : 'down',
                'down' : 'right',
                'right' : 'up'  }

    toRight = {  'up' : 'right',
                'right' : 'down',
                'down' : 'left',
                'left' : 'up'  }

    ammo = 10
    fuel = 2000 # 3000 should be ok

    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 2
        self.upper = pygame.image.load(os.path.join('Images','tankUpper.png')).convert_alpha()
        self.lower = pygame.image.load(os.path.join('Images','tankLower.png')).convert_alpha()
        self.image = pygame.image.load(os.path.join('Images','tankLower.png')).convert_alpha()
        self.rect = self.lower.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 'up'
        self.aim = 'up'
        self.rush = False
        self.ammo = Tank.ammo
        self.fuel = Tank.fuel
        self.exist = True
        self.inWater = False
        self.youDiedMassage = False

    def detectWaterCollision(self,lake):
        if pygame.sprite.collide_mask(lake, self):
            if self.inWater == False:
                tankPrint('Tanks cant swim!')
                self.inWater = True
            self.exist = False


    def turnRight(self):
        if not self.fuel:
            tankPrint("You don't have any fuel!")
            return
        self.direction = Tank.toRight[self.direction]
        self.aim = Tank.toRight[self.aim]
        self.lower = rot_center(self.lower, 270)
        self.upper = rot_center(self.upper, 270)
    def turnLeft(self):
        if not self.fuel:
            tankPrint("You don't have any fuel!")
            return
        self.direction = Tank.toLeft[self.direction]
        self.aim = Tank.toLeft[self.aim]
        self.lower = rot_center(self.lower, 90)
        self.upper = rot_center(self.upper, 90)
    def towerRight(self): #it shuld be turret not tower, but I am too lazy to change now
        if not self.fuel:
            tankPrint("You don't have any fuel!")
            return
        self.aim = Tank.toRight[self.aim]
        self.upper = rot_center(self.upper, 270)
    def towerLeft(self):
        if not self.fuel:
            tankPrint("You don't have any fuel!")
            return
        self.aim = Tank.toLeft[self.aim]
        self.upper = rot_center(self.upper, 90)


    def move(self):
        if self.fuel % 200 == 0 and not self.fuel == Tank.fuel:
            tankPrint('You have ' + str(self.fuel) + ' out of ' + str(Tank.fuel) + ' units of fuel.')
        if self.fuel <= 500 and self.fuel % 200 == 0:
            tankPrint('Your level of fuel is critically low. Consider refilling the fuel tank.')
        if self.fuel > 0:
            self.fuel -= 1
            if self.direction == 'up':
                self.rect.y -= self.speed
            elif self.direction == 'right':
                self.rect.x += self.speed
            elif self.direction == 'down':
                self.rect.y += self.speed
            elif self.direction == 'left':
                self.rect.x -= self.speed
        else:
            tankPrint("You don't have any fuel!")
            self.rush = False

    def display(self, display):
        display.blit(self.lower, (self.rect.x, self.rect.y))
        display.blit(self.upper, (self.rect.x, self.rect.y))

    def setRush(self, value):
        assert value in (True, False)
        self.rush = value

    def shoot(self):
        if self.ammo > 0:
            shoot = Bullet(self.rect.x, self.rect.y, self.aim)
            self.ammo -= 1
            tankPrint('You have ' + str(self.ammo) + ' out of ' +str(Tank.ammo) + ' bullets now.')
        else:
            tankPrint("Sorry, You don't have enough ammo.")

    def wait(self):
        pass

class Bullet(pygame.sprite.Sprite):
    bullets = []
    speed = 15
    existTime = 900 // speed

    def __init__(self,x,y, aim):
        self.image = pygame.image.load(os.path.join('Images','bullet.png')).convert_alpha()
        if aim == 'up':
            pass
        elif aim == 'right':
            self.image = rot_center(self.image, 270)
        elif aim == 'down':
            self.image = rot_center(self.image, 180)
        elif aim == 'left':
            self.image = rot_center(self.image, 90)
        else:
            assert False

        self.lifeTime = Bullet.existTime
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = aim

        Bullet.bullets.append(self)

    def move(self):
        if self.direction == 'up':
            self.rect.y -= Bullet.speed
        elif self.direction == 'right':
            self.rect.x += Bullet.speed
        elif self.direction == 'down':
            self.rect.y += Bullet.speed
        elif self.direction == 'left':
            self.rect.x -= Bullet.speed
        else:
            assert False
        if self.existTime < 0:
            self.remove()
        else:
            self.existTime -= 1

    def display(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))


    def remove(self):
        Bullet.bullets.remove(self)


class AmmoBox(pygame.sprite.Sprite, Target):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        Target.__init__(self,False,'ammo')
        self.image= pygame.image.load(os.path.join('Images','ammobox.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def display(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))
    def refillAmmoIfCollison(self, tank):
        if pygame.sprite.collide_mask(self, tank) and tank.ammo != Tank.ammo:
            tank.ammo = Tank.ammo
            tankPrint('Ammo refilled')


class Fuel(pygame.sprite.Sprite, Target):
    margin = 30
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        Target.__init__(self,False,'fuel')
        self.image= pygame.image.load(os.path.join('Images','fuel.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def display(self, display):
        display.blit(self.image, (self.rect.x, self.rect.y))
    def refillFuelIfCollison(self, tank):
        if pygame.sprite.collide_mask(self, tank) and tank.fuel < Tank.fuel - Fuel.margin:
            if Tank.fuel - tank.fuel > 80:
                tankPrint('Fuel refilled')
            tank.fuel = Tank.fuel
