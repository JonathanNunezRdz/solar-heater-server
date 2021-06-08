import math

def dist(a:float, b:float)->float:
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x:float, y:float, z:float)->float:
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x:float, y:float, z:float)->float:
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)