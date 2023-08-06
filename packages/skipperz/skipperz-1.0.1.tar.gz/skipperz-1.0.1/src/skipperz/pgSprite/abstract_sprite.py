import time

from . import mobile as libMobile


class Animation:
    def __init__ (self,imageList=None):
        if imageList is None: imageList = []
        self.imageList = imageList
        
        self.t0 = time.time()
        self.frequence = 10 #par default, 10 image/sec.
        #Note: si on change la frequence, il faut initialiser t0

    def addImage(self,image):
        self.imageList.append(image)

    def nbImage(self, clock = None):
        if clock is None: clock = time.time()
        lapse = clock - self.t0
        
        return int((lapse * self.frequence) % len(self.imageList))

    def getImage(self, clock = None):
        return self.imageList[self.nbImage(clock)]

    #par default, on cycle lineairement, mais on peu surcharger pour plus complexe.
    #surtout je fait un sprite generique qui appele animation.update()
    def update(self):
        pass

class AbstractSprite (libMobile.Mobile):
    """ This sprite has no render methode nor data relatif to its appearence.
    It only add an animation loop to the Mobile class"""
    def __init__(self, mobile=None, animation=None):
        # bringing back balance in the parameters
        if mobile is None: mobile = libMobile.Mobile((0,0))        
        if animation is None: animation = Animation()
        
        # self.mobile = mobile
        libMobile.Mobile.__init__(self, mobile.position)
        self.animation = animation
        self.alive=True

    def update(self, clock = None, update_clock = True):
        libMobile.Mobile.update(self, clock,update_clock)
        self.animation.update()

    @property
    def image(self):
        return self.animation.getImage()

    def kill(self):
        self.alive = False

    def __str__(self):
        result = libMobile.Mobile.__str__(self) + ", image#="+str(self.animation.nbImage())
        return result



