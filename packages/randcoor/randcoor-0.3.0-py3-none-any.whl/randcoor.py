import random as r
import math as m

def randCoor():
    """Returns a random position"""
    lon = r.uniform(-180,180)
    return (r.uniform(-90,90), lon if lon != -180 else 180)

def randCoorByDist(position, distanceMax, distanceMin=0):
    """Returns a random position that is situated between distanceMin km and distanceMax km from position"""
    deg100 = 0.8993216059187302 # Value such that the distance between (0,0) and (0,deg100) is 100km
    randDist = r.uniform(distanceMin, distanceMax)
    randAngle = r.uniform(0, 360)
    lat, lon = randDist*m.cos(m.radians(randAngle)), randDist*m.sin(m.radians(randAngle))
    lat, lon = position[0]+deg100/100*lat, position[1]+deg100/100*lon
    if abs(lat)>90:
        if lat>0:
            lat=-lat+180
        else:
            lat=-lat-180
    if abs(lon)>180:
        lon = (lon+180)%360-180
    return (lat, lon)

def randCoorByRule(rule, limit=None, showError=False):
    """
    Returns a random position that satisfies the function rule(lat, lon) with try-and-error
    unless the algorithm has tried limit times, and in that case show an error if showError
    """
    lenErr = iter(int, 1)
    if limit:
        lenErr = range(limit)
    for x in lenErr:
        lat, lon = randCoor()
        if rule(lat, lon):
            return (lat, lon)
    if showError:
        raise Exception('No randomly generated values satisfied the given condition')

def randCoorByArea(minCoor, maxCoor):
    """Returns a random position in the square formed by the points minCoor and maxCoor"""
    lat = r.uniform(minCoor[0], maxCoor[0])
    if minCoor[1] <= maxCoor[1]:
        return (lat, r.uniform(minCoor[1], maxCoor[1]))
    lon = r.choice([r.uniform(minCoor[1], 180), r.uniform(-180, maxCoor[1])])
    return (lat, lon if lon != -180 else 180)

def calcDist(*coordinates):
    """Calculates the distance between positions entered as parameters or contained in an iterable"""
    if len(coordinates) == 1:
        coordinates = coordinates[0]
    n = 0
    for x in range(len(coordinates)-1):
        c1, c2 = coordinates[x], coordinates[x+1]
        latDif = m.radians(c2[0]-c1[0])/2
        lonDif = m.radians(c2[1]-c1[1])/2
        lat1 = m.radians(c1[0])
        lat2 = m.radians(c2[0])
        calc = m.sin(latDif) * m.sin(latDif) + m.sin(lonDif) * m.sin(lonDif) * m.cos(lat1) * m.cos(lat2)
        n += 12742 * m.asin(m.sqrt(calc))
    return n

def roundCoor(coor, ndigits=0):
    """Round the two coordinates of a position (precision given by ndigits)"""
    return (round(coor[0], ndigits), round(coor[1], ndigits))

def decimalToDMS(coor):
    """Convert decimal notation to DMS notation ((°,',"), (°,',"))"""
    coor1 = (int(coor[0]), abs(int((coor[0]-int(coor[0]))*60)), abs(int((coor[0]*60-int(coor[0]*60))*60)))
    coor2 = (int(coor[1]), abs(int((coor[1]-int(coor[1]))*60)), abs(int((coor[1]*60-int(coor[1]*60))*60)))
    return (coor1, coor2)

def DMSToDecimal(coor):
    """Convert DMS notation ((°,',"), (°,',")) to decimal notation"""
    return (coor[0][0]+(1-2*(coor[0][0]<0))*(coor[0][1]/60+coor[0][2]/3600), coor[1][0]+(1-2*(coor[1][0]<0))*(coor[1][1]/60+coor[1][2]/3600))