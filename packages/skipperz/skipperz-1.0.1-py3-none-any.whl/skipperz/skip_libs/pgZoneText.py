import pygame

class TextZone:
    try:
        raise TypeError()
        pygame.font.init()
        defaultFont = pygame.font.Font(None,50)
    except(TypeError): # Pygame and PyInstaller have problems with default font. Read https://github.com/pygame/pygame/issues/2603
        pygame.init()
        defaultFont = pygame.font.Font('assets/Raleway-VariableFont_wght.ttf',50)
    
    def __init__(self, topLeft, bottomRight, font=None):
        if font is None:
            self.font = TextZone.defaultFont
        else:
            self.font = font

        self.topLeft = topLeft
        self.bottomRight = bottomRight

    def write(self, text, screen, color=(255,255,255,0)):
        #pygame.draw.rect(self.screen, BLACK, [0, 0, 1000, 100])
        #On converti le text en un bitmap (surface pygame)
        text = self.font.render(text, True, color)
        screen.blit(text,self.topLeft)
        
