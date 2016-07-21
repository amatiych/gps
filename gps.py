import serial
from math import pi,cos, sin,acos
from time import sleep
ser = serial.Serial('/dev/ttyS0',9600)

def parse_degrees(locinfo):
	fl = float(locinfo)/100.0
	deg = int(fl)
	fra = fl - deg
	return deg + fra*100.0/60

def distance( lat1,  lon1,  lat2,  lon2):
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

class location:

	def __init__(self,gpsline):
		toks = gpsline.split(',')
		self.time = toks[1]
		lng_s = 1 if toks[3] == 'N' else -1
		lat_s = 1 if toks[5] == 'E' else -1
		self.lat = parse_degrees(toks[2]) * lng_s
		self.lng = parse_degrees(toks[4]) * lat_s
		self.alt =float(toks[9])



while True:
	data = str(ser.readline())
	if "GPGGA" in data:
		loc = location(data)
		print(loc.lat, loc.lng,loc.alt)
		dist = distance(loc.lat,loc.lng,loc.lat,loc.lng+1 )

