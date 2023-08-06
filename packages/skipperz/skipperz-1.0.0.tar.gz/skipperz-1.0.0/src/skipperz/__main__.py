import os
folder = os.path.dirname(__file__)
print('main file dir:', folder)
os.chdir(folder)
print("Current working directory: {0}".format(os.getcwd()))

import pygame
from pygame.locals import *

from .skip_libs.badGuys import BadGuy
from .pgSprite import pgSprite
from .skip_libs import pgZoneText
from .pgSprite.euclid import Vector2
from .skip_libs.pgThrotle import Throtle
from . import params

#globals
screen = None
still_running = True # False if user close window or press "Esc" key
score = 0

sound_bank = dict()

animationHeros = pgSprite.Animation(params.hero_1_animation)
animationBoum = pgSprite.Animation(params.explosion_1_animation)
textZone = pgZoneText.TextZone( (800,1),(900,50))
clock = pygame.time.Clock()
spriteHeros = pgSprite.Sprite(animation=animationHeros)
herosThrotle = Throtle(spriteHeros, acceleration=(80, 80)) # each tick with key pressed, speed increase

def initialisation():
    global screen, clock,spriteHeros,herosThrotle, score
    pygame.init()
    screen = pygame.display.set_mode((1024, 668),DOUBLEBUF)
    spriteHeros = pgSprite.Sprite(animation=animationHeros)
    herosThrotle = Throtle(spriteHeros, acceleration=(80, 80))  # each tick with key pressed, speed increase

    spriteHeros.x = 50
    spriteHeros.y = 300
    pygame.init()
    clock = pygame.time.Clock()
    load_sounds(sound_bank)
    pygame.mixer.music.play(-1)

    spriteHeros.alive = True
    score = 0

def displayHero():
    spriteHeros.display(screen)
 
def displayBadGuy():
    for sprite_BadGuy in BadGuy.listBadGuys :
        sprite_BadGuy.display(screen)

def refresh():
    global still_running
    clock.tick(30)
    pygame.display.flip()
    screen.fill((0,0,0,0))
    displayHero()
    displayBadGuy()
    textZone.write(str(score), screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            still_running = False

    pressed = pygame.key.get_pressed() # TODO: surement gérable dans les events
    if  pressed[pygame.K_ESCAPE]:
        still_running = False

    pygame.event.pump()
    #Il est indispensable de traiter les evenement a un moment. Sinon, Pygame merdois


def exitScreen(sprite):
    if sprite.x<-50 or  sprite.x > 1000 or sprite.y < -50 or sprite.y > 650:
        return True
    else:
        return False

def killOnExit(sprite):
    sprite.speed = - sprite.speed  # the sprite bounces
    sprite.kill()

def load_sounds(dico_sound:dict):
    dico_sound['sound_loop'] = pygame.mixer.music.load(params.sound_loop)
    dico_sound['death_of_hero'] = pygame.mixer.Sound(params.death_of_hero)

def death_animation():
    """when the heroe dies"""
    global still_running

    sound_bank['death_of_hero'].play()

    spriteHeros.animation = animationBoum
    spriteHeros.animation.frequence = 5
    for i in range(100):
        spriteHeros.acceleration = Vector2(0, 0)
        refresh()
        for sprite_BadGuy in BadGuy.listBadGuys:
            sprite_BadGuy.update()  # modifie la position logique du mechant
        spriteHeros.update()
        if not still_running: # if Esc pressed or window manually closed
            return

def launch_game():
    global still_running, screen, score

    initialisation()

    # on lance un méchant d'amblée
    BadGuy.newBadGuyRandom()
    timeLastBadGuy = pygame.time.get_ticks()

    spawn_time = 4000 # at first, spawn 1 enemy each 4 millisecond

    while spriteHeros.alive and still_running:
        refresh()

        herosThrotle.readKeyboard() #modifie vitesse ou acceleration heros

        for spriteBadGuy in BadGuy.listBadGuys :
            spriteBadGuy.update() #modifie la position logique du mechant
        spriteHeros.update()

        if spriteHeros.collideAny( BadGuy.listBadGuys): # comment those 2 lines for god-mode
            spriteHeros.kill()               # comment those 2 lines for god-mode
        if exitScreen(spriteHeros):
            killOnExit(spriteHeros)

        spawn_time *= 0.9995
        if pygame.time.get_ticks() > timeLastBadGuy + spawn_time :
          score+=1
          BadGuy.newBadGuyRandom()
          timeLastBadGuy = pygame.time.get_ticks()

    # Here, the hero just died
    death_animation()
    print (score)


if __name__ == "__main__":
    while still_running:
        launch_game()