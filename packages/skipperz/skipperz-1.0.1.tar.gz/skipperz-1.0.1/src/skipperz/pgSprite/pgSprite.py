import pygame

from . import abstract_sprite


class Animation(abstract_sprite.Animation):
    def __init__ (self,imageList=[]):
        # on s'assure que toute les image sont de type pyGame.Surface
        properList=[] 
        for image in imageList:
            if  (type(image) is pygame.Surface):
                #image = image.convert_alpha()
                properList.append(image)
            else:
                #ca marche pour un nom de fichier. Peut etre dans d'autre cas
                try:
                    image = pygame.image.load(image)
                except(FileNotFoundError):
                    raise FileNotFoundError("can't find file "+str(image))
                #image = image.convert_alpha()
                properList.append(image)
        super().__init__(properList) 
  

    def addImage(self,image):
        # on s'assure que l'image sont de type pyGame.Surface
        if  isinstance(image, pygame.Surface):
            self.imageList.append(image)
        else:
            #ca marche pour un nom de fichier. Peut etre dans d'autre cas
            image = pygame.image.load(image)
            self.imageList.append(image)

# TODO rendre compatible avec pyGame.Sprite
class Sprite(abstract_sprite.AbstractSprite):
    def display(self, screen):
        screen.blit(self.image, (self.x, self.y))

    @property
    def rect(self):
        image = self.image
        result = pygame.Rect(self.x,self.y,image.get_width(), image.get_height())
        return result
    
    def collide(self, otherSprite):
        #return self.rect.colliderect(otherSprite.rect)
        return pygame.sprite.collide_mask(self, otherSprite)
    
        
        
    # MEthode statique pour tester colision entre 1 sprite (a priori le heros)
    # et tout les sprites d'une liste (les obstacles/méchant)
    # Return false si pas de colision. return le badGuy si colision
    def collideAny(self, list_of_sprites):
        for sprite in list_of_sprites :
            if self.collide(sprite):
                return sprite
        return False
