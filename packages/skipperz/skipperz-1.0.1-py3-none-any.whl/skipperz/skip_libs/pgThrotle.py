#cette librairie set a bouger un sprite
#avec les 4 touche directionelle du clavier
#Elle utilise pyGame pour gerer les touche
#Le sprite est n'importe quel objet acepteant les fonction suivante
# getX, setX, getY, setY getVx, getVy, setVx, setVy, getAx, getAy, setAx, setAy
# Ceci dit, si les valeur corespondant a la creation de Throtle sont nulle, ces methodes sont optionelle
import pygame
from ..params import throtle_sound, directional_key

from ..pgSprite.euclid import Vector2


def init():
    try:
        if not isinstance( directional_key.left, (list, tuple)):
            directional_key.left  = [directional_key.left]
        if not isinstance( directional_key.right, (list, tuple)):
            directional_key.right = [directional_key.right]
        if not isinstance( directional_key.up, (list, tuple)):
            directional_key.up    = [directional_key.up]
        if not isinstance( directional_key.down, (list, tuple)):
            directional_key.down  = [directional_key.down]
    except (AttributeError):
        raise AttributeError('There seems to be a problem in file "param.py", object "directional_key"  ')

def isZeroVector(vector):
    return vector.x != 0 and vector.y != 0

#If the given "something" is a vector2 then just return it(not a clone)
#Else, try to return a new vector
def makeVector2(something):
    if isinstance(something, Vector2):
        return something
    else:
        return Vector2(something[0],something[1])

class Throtle:
 #   def __init__(self,sprite, x=0,y=0,vx=0,vy=0,ax=0,ay=0):
    def __init__(self, sprite, speed=(0, 0), acceleration=(0, 0), deltaAcceleration=(0, 0)):
        self.sprite = sprite

        self.speed = makeVector2(speed)
        self.acceleration  = makeVector2(acceleration)
        self.deltaAcceleration = makeVector2(deltaAcceleration)

    #si touche droite => keyX=-1, gauche=>keyX=+1, haut=>keyY=-1, bas=>key=+1 
    def move(self,keyX, keyY):
        sprite = self.sprite
        
        if self.speed.__nonzero__() :
            sprite.vx = (self.speed.x * keyX)
            sprite.vy = (self.speed.y * keyY)

        if self.acceleration.__nonzero__() :
            sprite.ax = (self.acceleration.x * keyX)
            sprite.ay = (self.acceleration.y * keyY)

        # ca ne gere pas proprement (ou en tout cas diferement) le temp ou on presse la touche
        if self.deltaAcceleration.__nonzero__() :
            sprite.ax = (sprite.ax + self.deltaAcceleration.x*keyX)
            sprite.ay = (sprite.ay + self.deltaAcceleration.y*keyY)
                         


    def readKeyboard(self):
        keyX=0
        keyY=0
        pressed = pygame.key.get_pressed()

        if [key_pressed for key_pressed in directional_key.left if pressed[key_pressed]]: # if any key within left_keys is pressed
            keyX -=1
        if [key_pressed for key_pressed in directional_key.right if pressed[key_pressed]]:
            keyX +=1
        if [key_pressed for key_pressed in directional_key.up if pressed[key_pressed]]:
            keyY -=1
        if [key_pressed for key_pressed in directional_key.down if pressed[key_pressed]]:
            keyY +=1

        self.move(keyX,keyY)

init()