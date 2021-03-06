import sys
import math
import collections
import copy
import fileinput


class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __str__(self):
        return "{}, {}".format(self.x, self.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __sub__(self, point):
        return self + -point


class Polar:
    def __init__(self, r, theta):
        self.r, self.theta = r, theta

    def __str__(self):
        return "{}, {}".format(self.r, self.theta)


updateRate = 83
TILE_SIZE = 256
prevx = 0
prevy = 0
pointPerFoot = 1  # .0000021333333251050135
topAcceptableFeet = 10 * pointPerFoot
bottomAcceptableFeet = 10 * pointPerFoot

newroverLatlng = 0
dx = 1 * pointPerFoot
dy = 0
roverSpeed = 3 * pointPerFoot
heading = Polar(0, 0)
turningAngle = .07854 * 2  # turn 90 degrees in 5 seconds if updating at intervals of 2hz
accetableRangeTopWayPointWorldCoordinate = Point(0, 0)
accetableRangeBottomWayPointWorldCoordinate = Point(0, 0)

accetableRangeTopstartingPointWorldCoordinate = Point(0, 0)
accetableRangeBottomstartingPointWorldCoordinate = Point(0, 0)
roverWorldCoordinate = 0
WayPointWorldCoordinate = 0
startingPointWorldCoordinate = 0
rover = 0
waypointAcceptableRange = 3
waypointQueue = collections.deque()
headingQueue = collections.deque()
navigationQueue = collections.deque()

wasAtWaypoint = False  # should not start at waypoint
roverNewHeadingDebounce = False  # not debouncing
roverNewHeadingDebounceTime = 3000  # find a new heading in 3 seconds
roverPostions = collections.deque()

startingPoint = 0


# initailizecode

def iniatilze():
    global WayPointWorldCoordinate, navigationQueue
    WayPointWorldCoordinate = Point(200, 200)
    navigationQueue.append(copy.copy(WayPointWorldCoordinate))


def distance(point1, point2):
    # distance formula returns in point
    return math.sqrt(math.pow((point2.x - point1.x), 2) + math.pow((point2.y - point1.y), 2))


def atWayPoint():
    global roverWorldCoordinate, WayPointWorldCoordinate, waypointAcceptableRange, pointPerFoot, navigationQueue, startingPoint, heading, startingPointWorldCoordinate
    # if distance betwen the way point and the rover is less than 3 feet
    if (distance(roverWorldCoordinate, WayPointWorldCoordinate) < waypointAcceptableRange * pointPerFoot):
        if (len(navigationQueue) > 1):
            startingPoint = navigationQueue.popleft()
        else:
            startingPoint = navigationQueue[0]
            heading.r = 0
        if (len(navigationQueue) >= 1):
            startingPointWorldCoordinate = startingPoint
            WayPointWorldCoordinate = navigationQueue[0]
        else:
            heading.r = 0  # stop car

        return True

    else:
        return False


        # if the previous rover position distance to the waypoint is smaller
        # than the current than its go away from the waypoint


def distanceIsIncreasing():
    global roverPostions, WayPointWorldCoordinate
    if (distance(roverPostions[0], WayPointWorldCoordinate) < distance(roverPostions[1], WayPointWorldCoordinate)):
        return True
    return False


# compute the angle which the rover should rotate in order to be facing in a heading parrallel
# #to the way point using the forumala at
# #http://tpub.com/math2/5.htm

# first check that the arover has moved once

def slope(a, b):
    # y1 - y2 / x2 - x1
    # console.log((a.y - b.y)/(a.x - b.x))
    try:
        return (a.y - b.y) / (a.x - b.x)
    except:
        return float('inf')  # math.inf #"Error" a.y  / a.x



def rotateToParrallel():
    global roverPostions, WayPointWorldCoordinate
    m1 = slope(roverPostions[0], WayPointWorldCoordinate)
    m2 = slope(roverPostions[0], roverPostions[1])

    try:
        if (not math.isinf(m2) and not math.isinf(m1)):
            if (roverPostions[0].x < roverPostions[1].x):
                bearing = math.atan2(m2, 1)
            else:
                bearing = math.atan2(m2, 1) + math.pi
            heading.theta = normalizeAngle(bearingToUnits(bearing))
            #print str(heading.theta)
            tanTheta = (m2 - m1) / (1 + m1 * m2)
            if (not math.isinf(tanTheta)):
                theta = math.atan2(tanTheta, 1)
                if (not math.isinf(theta)):
                    if (theta):
                        return theta
                    else:
                        return 0
                else:
                    return 0
        else:
            return 0
    except:
        #print "Unexpected error:", sys.exc_info()[0]
        return 0  # print "error"

    return 0


# y = mx + b
# b = y - m
def intercept(point, m):
    return point.y - (m * point.x)


def aboveLine(a, b):
    global roverWorldCoordinate
    m = slope(a, b)
    b = intercept(b, m)
    y = m * roverWorldCoordinate.x + b
    return y < roverWorldCoordinate.y


    # check to see if rover is moving away from the way point
    # if so then turn it around 180 degrees.
    # make sure that it is between 0 and and 2pi.


def Turn():
    global heading, startingPointWorldCoordinate, WayPointWorldCoordinate, turningAngle
    if False:  # (distanceIsIncreasing()):
        heading.theta += math.pi
        heading.theta %= 2 * math.pi
    else:
        try:
            turningAngle = 1 * abs(rotateToParrallel())
            #print turningAngle
            pass
        except:
            #print "help"
            pass
        if (startingPointWorldCoordinate.x < WayPointWorldCoordinate.x):
            if (aboveLine(startingPointWorldCoordinate, WayPointWorldCoordinate)):
                heading.theta += turningAngle
                print  "d"


            else:
                heading.theta -= turningAngle
                print  "a"
        else:
            if (aboveLine(startingPointWorldCoordinate, WayPointWorldCoordinate)):
                heading.theta -= turningAngle
                print  "a"

            else:
                heading.theta += turningAngle
                print  "d"
    # if (heading.theta < 0):
    #     heading.theta += 2 * math.pi
    # heading.theta = heading.theta % (2 * math.pi)
   # print  normalizeAngle(heading.theta)


def moveRover():
    global wasAtWaypoint, startingPointWorldCoordinate
    wasAtWaypoint = atWayPoint()
    Turn()
    startingPointWorldCoordinate = copy.copy(roverWorldCoordinate)


def bearingToUnits(bearing):
    return flipHorizontally(rotateLeft(bearing))


def rotateLeft(angle):
    return normalizeAngle(angle + (math.pi / 2))


def flipHorizontally(angle):
    n = math.floor(angle / (math.pi))
    return normalizeAngle((math.pi) - (angle % (math.pi)) + n * (math.pi))


def normalizeAngle(angle):
    return (angle + (2 * math.pi)) % (2 * math.pi)


def deg_to_rad(deg):
    return (deg * math.pi / 180)


def rad_to_deg(rad):
    return (rad * 180 / math.pi)


iniatilze()
lineNumber = 1
# while 1:
#     try:
#         line = sys.stdin.readline()
#     except KeyboardInterrupt:
#         break
#
#     if not line:
#         break
for line in fileinput.input():
    cordStr = line.split(",")
    if lineNumber > 2:
        try:
            gpsX = float(cordStr[1])
            gpsY = float(cordStr[0])

            #print str(gpsX) + " : " + str(gpsY)
        except:
            #print "bad coordinates"
            continue

    if lineNumber == 3:
        startingPointWorldCoordinate = Point(gpsX, gpsY)
    if lineNumber == 4:
        roverWorldCoordinate = Point(gpsX, gpsY)
        roverPostions.append(copy.copy(roverWorldCoordinate))
        roverPostions.append(copy.copy(roverWorldCoordinate))

    if lineNumber > 4:
        roverWorldCoordinate = Point(gpsX, gpsY)
        roverPostions.append(copy.copy(roverWorldCoordinate))
        if (len(roverPostions) > 2):
            roverPostions.popleft()
        moveRover()
    lineNumber += 1
    # time.sleep(.083) #12 hz refresh rate




    # GpsUpdateLogic()

