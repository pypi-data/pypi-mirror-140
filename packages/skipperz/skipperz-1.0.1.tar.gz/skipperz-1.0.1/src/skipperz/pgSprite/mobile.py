import time

from . import euclid


def mobileToStr(obj):

    try:
      x=obj.x
    except(AttributeError):
        try:
            x=obj.getX()
        except(AttributeError):
            x="N/A"
    try:
      y=obj.y
    except(AttributeError):
        try:
            y=obj.getY()
        except(AttributeError):
            y="N/A"
    try:
      vx=obj.vx
    except(AttributeError):
        try:
            vx=obj.getVx()
        except(AttributeError):
            vx="N/A"
    try:
      vy=obj.vy
    except(AttributeError):
        try:
            vy=obj.getVy()
        except(AttributeError):
            vy="N/A"
    try:
      ax=obj.ax
    except(AttributeError):
        try:
            ax=obj.getAx()
        except(AttributeError):
            ax="N/A"
    try:
      ay=obj.ay
    except(AttributeError):
        try:
            ay=obj.getAy()
        except(AttributeError):
            ay="N/A"
    return "x="+str(x)+", y="+str(y)+" vx="+str(vx)+", vy="+str(vy) +" ax="+str(ax)+", ay="+str(ay)

# on essaie de transformer un machin en un vector2
# return an euclid.Vector2 object
def trucToVector2(machin):
    try:
        result = euclid.Vector2(machin[0], machin[1])
    except:
        try:
            result = euclid.Vector2(machin.getX(), machin.getY())
        except:
            #If this one fail too, it throw an error
            result = euclid.Vector2(machin.x, machin.y)
    return result
        
        
                        
class Mobile:
        
    def __init__(self,position):
        if type(position)  is euclid.Vector2:
                self.position = position
        else:
                self.position = trucToVector2(position)
        
        self.t0 = time.time()  #top a partir duquel on mesure les temps. Comportement par defaut: c'est le temp du dernier update

        self.speed = euclid.Vector2(0, 0)
        self.acceleration = euclid.Vector2(0, 0)
        

        
    # met a jour position et speed en fonction tu temps ecoule
    # Par defaut, clock = now
    def update(self, clock = None, update_clock = True):
        if clock is None: clock = time.time()
        lapse = clock - self.t0

        if self.speed is not None:
            self.position += lapse*self.speed
        if self.acceleration is not None:
            self.speed += lapse*self.acceleration

        if update_clock: # update_clock = False allow some kind of similation from t0
            self.t0=clock # t0 = date de dernier update

    def __str__(self):
        return mobileToStr(self)


    #des racourcis
    @property
    def x(self):
        return self.position.x
    @x.setter
    def x(self, new_x): self.position.x = new_x

    @property
    def y(self): return self.position.y
    @y.setter
    def y(self, new_y): self.position.y = new_y

    @property
    def vx(self): return self.speed.x
    @vx.setter
    def vx(self, new_vx): self.speed.x = new_vx

    @property
    def vy(self): return self.speed.y
    @vy.setter
    def vy(self, new_vy): self.speed.y = new_vy
    
    @property
    def ax(self): return self.acceleration.x
    @ax.setter
    def ax(self, new_ax): self.acceleration.x = new_ax
    
    @property
    def ay(self): return self.acceleration.y
    @ay.setter
    def ay(self, new_ay): self.acceleration.y = new_ay
    
    


#class MobileSurRail(Mobile):
    #TODO l'update est diferent
