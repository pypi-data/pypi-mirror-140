# randcoor BETA
A basic Python library to generate random geographical coordinates with additional features

## Installation
This module can quickly be installed with pip
```
pip install randcoor
```

## Usage
Geographical coordinates are represented by a tuple with two decimal values (Example: `(-73.1657655614035, 32.52677878350798)`)

Functions that can generate random coordinates:
* `randCoor()`: Generates random coordinates
* `randCoorByDist(position, distanceMax, distanceMin=0)`: Generates random coordinates by distance
* `randCoorByRule(rule, limit=None, showError=False)`: Generates random coordinates by checking if they follow the function rule
* `randCoorByArea(minCoor, maxCoor)`: Generates random coordinates that are between the coordinates of two points

Other functions:
* `calcDist(*coordinates)`: Calculates the distance between points
* `roundCoor(coor, ndigits=0)`: Round the two coordinates of a position
* `decimalToDMS(coor)`: Converts decimal notation to DMS notation
* `DMSToDecimal(coor)`: Converts DMS notation to decimal notation

If you need more information about these functions, you can use the help function

## Examples
```python
from randcoor import *
coor = randCoor()
print(coor)
# (0.5682138386708715, 7.332646594327713)
print(roundCoor(coor))
# (1.0, 7.0)
print(decimalToDMS(coor))
# ((0, 34, 5), (7, 19, 57))
randCoorByDist((0,0), 10, 5)
# (0.0795066131324715, -0.02793806206797174)
randCoorByArea((20,20),(50,50))
# (32.66256834620321, 44.82375046671473)
randCoorByArea((20,50),(50,20))
# (24.12540072542634, 169.03115180655362)
L = [randCoorByRule(lambda x, y: x>y) for x in range(3)]
print(L)
# [(71.83324744299622, -27.090322185441806), (-31.870493778872586, -167.80562795747355), (17.87985263208857, -162.7185532945298)]
calcDist(L)
# 20565.48275832477
```