import pygame
import sys
import time
from pygame.locals import *
import math 
BLACK = (225,225,225)
pygame.init()
screen = pygame.display.set_mode()        
consommation = USEREVENT+1
display = USEREVENT+2
apparition = USEREVENT+3

pygame.time.set_timer(consommation, 1000)
pygame.time.set_timer(display, 20)
pygame.time.set_timer(apparition, 200)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

WHITE = ( 255, 255, 255)



class People:
    def __init__(self,position,city_goal,coordo_goal,speed,number):
        self.position = position
        self.coordo_goal = coordo_goal
        self.speed = speed
        self.number = number
        self.city_goal = city_goal
        self.arrived = False
        self.color = (0,0,0)
        self.angle = 0
        self.voisins = []
        self.stopped = False
        
    def init_angle(self):
        x = self.coordo_goal[0] - (self.position[0])
        y = self.coordo_goal[1] - (self.position[1])
        angle = math.atan(y/x) if x!= 0 else 0
        if x <0:
            angle += math.pi
        self.angle = angle

    def distance_to(self,position1,position2):
        return math.sqrt((position1[0] - position2[0])**2 + (position1[1] - position2[1])**2)

    def deplacement(self):
        if self in world.peoples[0].voisins:
            self.color = (234,341,12)
        else:
            self.color = (0,0,0)
        if self.distance_to(self.coordo_goal,self.position) > 20:
            position = [self.position[0] + self.speed*math.cos(self.angle), self.position[1] + self.speed*math.sin(self.angle)]
            if self.collision(position):

                self.position = position
                self.init_angle()

        else:
            if self not in self.city_goal.peoples:
                self.city_goal.peoples += [self]

                self.arrived = True

            
    def plus_proche_voisin(self): 
        region = Rect(self.position[0],self.position[1],100,100)
        found_points=[]
        self.voisins = qtree.query(region,found_points,self)

    def collision(self,position):

        #for people in self.voisins:

        for people in world.peoples:
            
            if people != self:
                if self.distance_to(people.position,position) < 20:
                    if people.arrived:
                        self.stopped = True
                        return False
                    
                    #self.color = (255,0,0)
                    self.angle += random.uniform(math.pi/8,math.pi/4)
                    return False  
        self.stopped = False
        return True


    def redirection():
        pass

class World:
    def __init__(self):
        self.peoples = []

world = World()
class Ville:
    def __init__(self,influence,position):
        self.influence = influence
        self.position = position
        self.nbre_people = influence
        self.peoples = []

    def draw_town(self):
        pygame.draw.rect(screen, (12,210,36), pygame.Rect(self.position[0], self.position[1], 200, 200))

    def consommation_people():
        pass

Tokyo = Ville(1000,[800,25])
Singapour = Ville(1000,[1000,500])
Lyon = Ville(1000,[25,400])
Towns = [Tokyo,Singapour,Lyon]


import random

def generation_people():
    
    city_goal = random.choice(Towns)
    #nbre_people = random.randint(10,100)
    #people = People([random.randint(SCREEN_WIDTH/3,2*SCREEN_WIDTH/3),random.randint(SCREEN_HEIGHT/3,2*SCREEN_HEIGHT/3)],city_goal,[city_goal.position[0],city_goal.position[1]],1,10)
    
    people = People([SCREEN_WIDTH/2,SCREEN_HEIGHT/2],city_goal,[random.randint(city_goal.position[0]-10,city_goal.position[0]+10),random.randint(city_goal.position[1]-10,city_goal.position[1]+10)],5,10)
    people.init_angle()
    world.peoples += [people]

def fast_generation_people():
    for i in range(100):
        city_goal = random.choice(Towns)
        people = People([random.randint(0,SCREEN_WIDTH),random.randint(0,SCREEN_HEIGHT)],city_goal,[city_goal.position[0],city_goal.position[1]],5,10)
        world.peoples += [people]



import numpy as np

class Point:
    """A point located at (x,y) in 2D space.

    Each Point object may be associated with a payload object.

    """

    def __init__(self, position, payload=None):
        self.position = self.position
        self.payload = payload

    def __repr__(self):
        return '{}: {}'.format(str((self.position[0], self.position[1])), repr(self.payload))
    def __str__(self):
        return 'P({:.2f}, {:.2f})'.format(self.position[0], self.position[1])

    def distance_to(self, other):
        try:
            other_x, other_y = other.position[0], other.position[1]
        except AttributeError:
            other_x, other_y = other
        return np.hypot(self.position[0] - other_x, self.position[1] - other_y)

class Rect:
    """A rectangle centred at (cx, cy) with width w and height h."""

    def __init__(self, cx, cy, w, h):
        self.cx, self.cy = cx, cy
        self.w, self.h = w, h
        self.west_edge, self.east_edge = cx - w/2, cx + w/2
        self.north_edge, self.south_edge = cy - h/2, cy + h/2

    def __repr__(self):
        return str((self.west_edge, self.east_edge, self.north_edge,
                self.south_edge))

    def __str__(self):
        return '({:.2f}, {:.2f}, {:.2f}, {:.2f})'.format(self.west_edge,
                    self.north_edge, self.east_edge, self.south_edge)

    def contains(self, point):
        """Is point (a Point object or (x,y) tuple) inside this Rect?"""

        try:
            point_x, point_y = point.position[0], point.position[1]
        except AttributeError:
            point_x, point_y = point

        return (point_x >= self.west_edge and
                point_x <  self.east_edge and
                point_y >= self.north_edge and
                point_y < self.south_edge)

    def intersects(self, other):
        """Does Rect object other interesect this Rect?"""
        return not (other.west_edge > self.east_edge or
                    other.east_edge < self.west_edge or
                    other.north_edge > self.south_edge or
                    other.south_edge < self.north_edge)  

class QuadTree:
    """A class implementing a quadtree."""

    def __init__(self, boundary, max_points=4, depth=0):
        """Initialize this node of the quadtree.

        boundary is a Rect object defining the region from which points are
        placed into this node; max_points is the maximum number of points the
        node can hold before it must divide (branch into four more nodes);
        depth keeps track of how deep into the quadtree this node lies.

        """

        self.boundary = boundary
        self.max_points = max_points
        self.points = []
        self.depth = depth
        # A flag to indicate whether this node has divided (branched) or not.
        self.divided = False

    def __str__(self):
        """Return a string representation of this node, suitably formatted."""
        sp = ' ' * self.depth * 2
        s = str(self.boundary) + '\n'
        s += sp + ', '.join(str(point) for point in self.points)
        if not self.divided:
            return s
        return s + '\n' + '\n'.join([
                sp + 'nw: ' + str(self.nw), sp + 'ne: ' + str(self.ne),
                sp + 'se: ' + str(self.se), sp + 'sw: ' + str(self.sw)])

    def divide(self):
        """Divide (branch) this node by spawning four children nodes."""

        cx, cy = self.boundary.cx, self.boundary.cy
        w, h = self.boundary.w / 2, self.boundary.h / 2
        # The boundaries of the four children nodes are "northwest",
        # "northeast", "southeast" and "southwest" quadrants within the
        # boundary of the current node.
        self.nw = QuadTree(Rect(cx - w/2, cy - h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.ne = QuadTree(Rect(cx + w/2, cy - h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.se = QuadTree(Rect(cx + w/2, cy + h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.sw = QuadTree(Rect(cx - w/2, cy + h/2, w, h),
                                    self.max_points, self.depth + 1)
        self.divided = True

    def insert(self, point):
        """Try to insert Point point into this QuadTree."""

        if not self.boundary.contains(point):
            # The point does not lie inside boundary: bail.
            return False
        if len(self.points) < self.max_points:
            # There's room for our point without dividing the QuadTree.
            self.points.append(point)
            return True

        # No room: divide if necessary, then try the sub-quads.
        if not self.divided:
            self.divide()

        return (self.ne.insert(point) or
                self.nw.insert(point) or
                self.se.insert(point) or
                self.sw.insert(point))

    def query(self, boundary,found_points,people):
        """Find the points in the quadtree that lie within boundary."""

        if not self.boundary.intersects(boundary):
            # If the domain of this node does not intersect the search
            # region, we don't need to look in it for points.
            return []

        # Search this node's points to see if they lie within boundary ...
        for point in self.points:
            if boundary.contains(point):
                if point != self:
                    found_points.append(point)
        # ... and if this node has children, search them too.
        if self.divided:
            self.nw.query(boundary, found_points,people)
            self.ne.query(boundary, found_points,people)
            self.se.query(boundary, found_points,people)
            self.sw.query(boundary, found_points,people)
        return found_points


    def query_circle(self, boundary, centre, radius, found_points):
        """Find the points in the quadtree that lie within radius of centre.

        boundary is a Rect object (a square) that bounds the search circle.
        There is no need to call this method directly: use query_radius.

        """

        if not self.boundary.intersects(boundary):
            # If the domain of this node does not intersect the search
            # region, we don't need to look in it for points.
            return []

        # Search this node's points to see if they lie within boundary
        # and also lie within a circle of given radius around the centre point.
        for point in self.points:
            if (boundary.contains(point) and
                    point.distance_to(centre) <= radius):
                found_points.append(point)

        # Recurse the search into this node's children.
        if self.divided:
            self.nw.query_circle(boundary, centre, radius, found_points)
            self.ne.query_circle(boundary, centre, radius, found_points)
            self.se.query_circle(boundary, centre, radius, found_points)
            self.sw.query_circle(boundary, centre, radius, found_points)
        return found_points

    def query_radius(self, centre, radius, found_points):
        """Find the points in the quadtree that lie within radius of centre."""

        # First find the square that bounds the search circle as a Rect object.
        boundary = Rect(*centre, radius, radius)
        return self.query_circle(boundary, centre, radius, found_points)


    def __len__(self):
        """Return the number of points in the quadtree."""

        npoints = len(self.points)
        if self.divided:
            npoints += len(self.nw)+len(self.ne)+len(self.se)+len(self.sw)
        return npoints



width, height = SCREEN_WIDTH, SCREEN_HEIGHT


domain = Rect(0, 0, width, height)



while True:
    screen.fill(WHITE)
    qtree = QuadTree(domain, 3)
    police = pygame.font.Font(None,72)

    
    keys=pygame.key.get_pressed()  
    for event in pygame.event.get(): 
        if keys[K_UP]:
                pygame.quit()
                sys.exit()

        if event.type == display:
            for point in world.peoples:
                qtree.insert(point)

            for point in world.peoples:
                point.plus_proche_voisin()
                

            for town in Towns:
                town.draw_town()

            for people in world.peoples:
                people.deplacement()
                pygame.draw.circle(screen,(0,0,0),people.position,people.number)

            """if world.peoples:
                pygame.draw.circle(screen,world.peoples[0].color,world.peoples[0].position,50,1)
                #screen.blit(score, (10, 100))"""
            pygame.display.flip()

        if event.type == MOUSEBUTTONUP:
            
            fast_generation_people()
           
        if event.type == apparition:
            generation_people()
        if event.type == consommation:
            for town in Towns:
                for people in town.peoples:
                    difference = town.nbre_people - people.number
                    if difference > 0:
                        town.nbre_people -= difference
                        people.number = 0
                    else:
                        people.number -= people.city_goal.nbre_people
                        town.nbre_people = 0

                    if people.number == 0:
                        world.peoples.remove(people)
                        town.peoples.remove(people)

            for town in Towns:
                town.nbre_people = 100
