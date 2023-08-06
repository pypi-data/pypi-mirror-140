#TODO faire une version "inteligente"

def getX(obj):
    try:
        return obj.x
    except:
        try:
            return obj.X
        except:
            try:
                return obj.getX()
            except:
                print("No X property for this object: "+str(obj))

def getY(obj):
    try:
        return obj.y
    except:
        try:
            return obj.Y
        except:
            try:
                return obj.getY()
            except:
                print("No Y property for this object: "+str(obj))

def getVx(obj):
    try:
        return obj.vx
    except:
        try:
            return obj.Vx
        except:
            try:
                return obj.getVx()
            except:
                print("No vx property for this object: "+str(obj))

def getVy(obj):
    try:
        return obj.vy
    except:
        try:
            return obj.Vy
        except:
            try:
                return obj.getVy()
            except:
                print("No vy property for this object: "+str(obj))


def getAx(obj):
    try:
        return obj.ax
    except:
        try:
            return obj.Ax
        except:
            try:
                return obj.getAx()
            except:
                print("No ax property for this object: "+str(obj))

def getAy(obj):
    try:
        return obj.ay
    except:
        try:
            return obj.Ay
        except:
            try:
                return obj.getAy()
            except:
                print("No ay property for this object: "+str(obj))
