import serial
from time import sleep
from datetime import datetime
from math import pi,cos, sin,acos
import threading

def capture_ex(fun):
        def wrapper(*args, **kwargs):
                try:
                        return fun(*args,**kwargs)
                except Exception as ex:
                        print(ex)
        return wrapper

def parse_degrees(locinfo):
    fl = float(locinfo)/100.0
    deg = int(fl)
    fra = fl - deg
    return deg + fra*100.0/60

@capture_ex
def distance( loc1,loc2):
    lat1,lon1 = loc1.lat,loc1.lng
    lat2,lon2 = loc2.lat,loc2.lng

    if (lat1,lon1) == (lat2,lon2):
        return 0

        # Convert degrees to radians
    lat1 = lat1 * pi / 180.0
    lon1 = lon1 * pi / 180.0
    lat2 = lat2 * pi / 180.0
    lon2 = lon2 * pi / 180.0
    r = 6378100

    rho1 = r * cos(lat1)
    z1 = r * sin(lat1)
    x1 = rho1 * cos(lon1)
    y1 = rho1 * sin(lon1)

    rho2 = r * cos(lat2)
    z2 = r * sin(lat2)
    x2 = rho2 * cos(lon2)
    y2 = rho2 * sin(lon2)

    dot = (x1 * x2 + y1 * y2 + z1 * z2)
    cos_theta = dot / (r * r)
    theta = acos(cos_theta)
    return r * theta

@capture_ex
def speed(loc1,loc2):
    dist = distance(loc1,loc2)
    tdif = abs((loc1.time - loc2.time).seconds)
    if tdif == 0:
        return 0
    met_seconds = dist / tdif
    met_hour = met_seconds * 3600
    mph = met_hour / 1609.34
    return mph




class Location:

    def __init__(self):
        self.lat = 0
        self.lng = 0
        self.alt = 0
        self.time = datetime.now()

    @capture_ex        
    def update(self,gpsline):

        toks = gpsline.split(',')

        if toks[6] != "0":
            self.time = datetime.strptime(toks[1][:6],"%H%M%S")
            lng_s = 1 if toks[3] == 'N' else -1
            lat_s = 1 if toks[5] == 'E' else -1
            self.lat = parse_degrees(toks[2]) * lng_s
            self.lng = parse_degrees(toks[4]) * lat_s
            self.alt =float(toks[9])

    def __repr__(self):
        return str.format("{2}:{0},{1}", self.lat, self.lng,self.time)

class GPSThread(threading.Thread):
    
    def __init__(self,loc):
        self.loc = loc
        self.ser = serial.Serial('/dev/ttyS0',9600)
        super(GPSThread, self).__init__()
        
    def run(self):
        while True:
            data = str(self.ser.readline())
            if "GPGGA" in data:
                self.loc.update(data)
    
   
if __name__ == '__main__':
    loc = Location()
    gps = GPSThread(loc)
    gps.start()

    while True:
        print(loc)
        sleep(1)



