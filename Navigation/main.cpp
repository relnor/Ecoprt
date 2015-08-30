#include <iostream>
#include <complex>      // std::complex, std::polar
#include <deque>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>

using namespace std;
#define False 0;

std::vector<std::string> &split( std::string &s, char delim, std::vector<std::string> &elems) {
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}


std::vector<std::string> split( std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, elems);
    return elems;
}

// Class to represent points.
class Point {
private:
        double xval, yval;
public:
        // Constructor uses default arguments to allow calling with zero, one,
        // or two values.
        Point(double x = 0.0, double y = 0.0) {
                xval = x;
                yval = y;
        }

        // Extractors.
        double x() { return xval; }
        double y() { return yval; }

        // Distance to another point.  Pythagorean thm.
        double dist(Point other) {
                double xd = xval - other.xval;
                double yd = yval - other.yval;
                return sqrt(xd*xd + yd*yd);
        }

        // Add or subtract two points.
        Point add(Point b)
        {
                return Point(xval + b.xval, yval + b.yval);
        }
        Point sub(Point b)
        {
                return Point(xval - b.xval, yval - b.yval);
        }

        // Move the existing point.
        void move(double a, double b)
        {
                xval += a;
                yval += b;
        }

        // Print the point on the stream.  The class ostream is a base class
        // for output streams of various types.
        void print(ostream &strm)
        {
                strm << "(" << xval << "," << yval << ")";
        }
};

int updateRate = 83;
int TILE_SIZE = 256;
int prevx = 0;
int prevy = 0;
int pointPerFoot = 1;
int topAcceptableFeet = 10 * pointPerFoot;
int bottomAcceptableFeet = 10 * pointPerFoot;

int newroverLatlng = 0;
int dx = 1 * pointPerFoot;
int dy = 0;
int roverSpeed = 3 * pointPerFoot;
complex<int> heading = polar(0, 0);
int turningAngle = .07854 * 2;  // turn 90 degrees in 5 seconds if updating at intervals of 2hz
Point accetableRangeTopWayPointWorldCoordinate = Point(0, 0);
Point accetableRangeBottomWayPointWorldCoordinate = Point(0, 0);

Point accetableRangeTopstartingPointWorldCoordinate = Point(0, 0);
Point accetableRangeBottomstartingPointWorldCoordinate = Point(0, 0);
Point roverWorldCoordinate = 0;
Point WayPointWorldCoordinate = 0;
Point startingPointWorldCoordinate = 0;
int rover = 0;
int waypointAcceptableRange = 3;
int lineNumber = 1;
deque<int> waypointQueue ;
deque<int> headingQueue ;
deque<Point> navigationQueue;

int wasAtWaypoint = False;  // should not start at waypoint
int roverNewHeadingDebounce = False;  // not debouncing
int roverNewHeadingDebounceTime = 3000;  // find a new heading in 3 seconds
deque<Point> roverPostions ;

int  startingPoint = 0;

void iniatilze(){
    WayPointWorldCoordinate = Point(200, 200); // set a waypoint at 200 meter 200 meteres
    navigationQueue.push_back(WayPointWorldCoordinate); // add the waypoint to the collection of waypoints
}

std::string::size_type sz;     // alias of size_t
float gpsX;
float gpsY;

void moveRover(){
//    global wasAtWaypoint, startingPointWorldCoordinate
//    wasAtWaypoint = atWayPoint()
//    Turn()
//    startingPointWorldCoordinate = copy.copy(roverWorldCoordinate)
}

int main()
{
    iniatilze(); // set a random destation
    string line; //strores the raw string of the NEDS example of a line -73.6010,67.6970,0.0000
    ifstream myfile ("log.txt"); // use example a log given from piksi gps
    std::vector<std::string> cordStr; // a vector collection of the NED
     if (myfile.is_open()) // make sure the file exist
    {
    while ( getline (myfile,line) ) // get a line from the log
    {
      cordStr.clear(); // clear the contents of the vector so it doesnt' grow from last line
       split( line, ',', cordStr); // we parse each coordinate of the NED ito a list of strings for each ned
//       for (std::vector<string>::iterator it = cordStr.begin(); it != cordStr.end(); ++it)
//            std::cout << ' ' << *it; // iterate through vector of coordinates and print them
        if (lineNumber > 2) // we skip the first two lines because they are errors from piksi
        {
            try // we try to convert the coordinates from strings to floats
            {

                gpsX = std::stof (cordStr[1], &sz);
                gpsY = std::stof (cordStr[0], &sz);
                //cout << gpsX << " " << gpsY << "\n";
            }
            catch(...){ // if we are given errors from piksi we will just go to next line
               // #print "bad coordinates"
                continue;
            }
        }
        if (lineNumber == 3)
        { //after a points been recored you can mark the starting postion
            startingPointWorldCoordinate = Point(gpsX, gpsY);
        }
        if (lineNumber == 4)
        { // next we start tracking two postion in rover postions to determin heading update rovers postion
            roverWorldCoordinate = Point(gpsX, gpsY);
            roverPostions.push_back(roverWorldCoordinate);
            roverPostions.push_back(roverWorldCoordinate);
        }
        if (lineNumber > 4)
        {// only want two rover postions so trim pop off the oldest postion after two.
            roverWorldCoordinate = Point(gpsX, gpsY);
            roverPostions.push_back(roverWorldCoordinate);
            if (roverPostions.size() > 2)
            {
                roverPostions.pop_front();
            }
            moveRover();
        }
        lineNumber += 1;


    }
    myfile.close();
    }

    else cout << "Unable to open file";

    return 0;
}
