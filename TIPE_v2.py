import pygame
from pygame.locals import *
import sys
import math
import svg_parser
from collections import defaultdict
import random


PEOPLE_SIZE = 5
BLACK = (225,225,225)
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)  
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()    
display = USEREVENT+2
apparition = USEREVENT+3
MAX_DENSITY_EDGE = 1

pygame.init()
pygame.time.set_timer(display, 20)
pygame.time.set_timer(apparition, 200)
image = pygame.image.load('background.jpg')
image = pygame.transform.scale(image, (1000,1000))

class Graph():
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.starter = []
        self.attraction = []
        self.carrefour = []
        self.edges = defaultdict(list)
        self.edges_object = defaultdict(list)
        self.weights = {}
        self.blocked = []

    def init_graph(self):
        for node in svg_parser.starter + svg_parser.attraction + svg_parser.carrefour:
            if node in svg_parser.carrefour:
                self.carrefour.append(node)
            if node in svg_parser.starter:
                self.starter.append(node)
            elif node in svg_parser.attraction:
                self.attraction.append(node)
            else:
                self.carrefour.append(node)
        import copy
        self.starter = svg_parser.starter
        self.attraction = copy.deepcopy(self.starter)
    
    def dijsktra(self,initial, end):
        # shortest paths is a dict of nodes
        # whose value is a tuple of (previous node, weight)
        shortest_paths = {initial: (None, 0)}
        current_node = initial
        visited = set()
        
        while current_node != end:
            visited.add(current_node)
            destinations = self.edges[current_node]
            weight_to_current_node = shortest_paths[current_node][1]

            for next_node in destinations:
                weight = self.weights[(current_node, next_node)] + weight_to_current_node
                if next_node not in shortest_paths:
                    shortest_paths[next_node] = (current_node, weight)
                else:
                    current_shortest_weight = shortest_paths[next_node][1]
                    if current_shortest_weight > weight:
                        shortest_paths[next_node] = (current_node, weight)
            
            next_destinations = {node: shortest_paths[node] for node in shortest_paths if node not in visited}
            if not next_destinations:
                return []
            # next node is the destination with the lowest weight
            current_node = min(next_destinations, key=lambda k: next_destinations[k][1])
        
        # Work back through destinations in shortest path

        path = []
        while current_node is not None:
            path.append(current_node)
            next_node = shortest_paths[current_node][0]
            current_node = next_node
        # Reverse path

        path = path[::-1]
        return path

    def distance_to(self,position1,position2):
        return math.sqrt((float(position1[0]) - float(position2[0]))**2 + (float(position1[1]) - float(position2[1]))**2)

graph = Graph()
graph.init_graph()

class Edge:
    def __init__(self,start_node,end_node,length,discretized_nb_part):
        self.start_node = start_node
        self.end_node= end_node
        self.length = length
        self.discretized_nb_part = discretized_nb_part   #en cb de morceaux on a coupé la liaison 
        self.people_on_edge = defaultdict(list)
        self.max_density = 4
        self.status = 'activated'

class People:
    def __init__(self):
        self.position = {
                         'coord_x_y' : [0,0],
                         'last_node' : [0,0],
                         'next_node' : [0,0],
                         'current_edge' : None,
                         'coord_on_edge' : 0 }  
        self.speed = 5
        self.edge = [[0,0],0]
        self.path = []
        self.status = "moving"
        self.stopped = False
        self.color = (255,0,36)
        self.direction ='up'   #up ou down
        self.attraction_visited = []
    
    def calcul_nouvelle_position(self):
        Xfinal = float(self.path[1][0])
        Yfinal = float(self.path[1][1])
        x_self = float((self.position['coord_x_y'][0]))
        y_self = float(self.position['coord_x_y'][1])
        DeltaX = Xfinal - x_self 
        DeltaY = Yfinal - y_self 

        angle = math.atan(DeltaY/DeltaX) if DeltaX != 0 else 0
        if DeltaX <0:
            angle += math.pi
        POSITION = [x_self + self.speed*math.cos(angle), y_self + self.speed*math.sin(angle)] 
        return POSITION


    def distance_to(self,position1,position2):
        return math.sqrt((float(position1[0]) - float(position2[0]))**2 + (float(position1[1]) - float(position2[1]))**2)

    
    def init_pos_on_segment(self):
        a = self.position['coord_x_y']
        """print(self.position['coord_x_y'])"""
        self.position['coord_x_y'] = self.path[0]
        """print(self.position['coord_x_y'])
        print(self.distance_to(self.position['coord_x_y'],self.position['coord_x_y']))
        print()"""
        self.position['last_node'] = self.path[0]
        self.position['next_node'] = self.path[1]
        self.position['current_edge'] = graph.edges_object[(self.path[0],self.path[1])]
        self.direction = 'up'

        edge = self.position['current_edge']
        #print(self.position)
        #print('toto',self.position['current_edge'].people_on_edge[self.position['coord_on_edge']])
        assert [self] not in [valeur for valeur in self.position['current_edge'].people_on_edge.values()], 'init_pos'
        if self in self.position['current_edge'].people_on_edge[self.position['coord_on_edge']]:  
            self.position['current_edge'].people_on_edge[self.position['coord_on_edge']].remove(self)
            assert [self] not in [valeur for valeur in self.position['current_edge'].people_on_edge.values()], 'init_pos'
        #print(self.path[0])
        self.position['coord_on_edge'] = 0
        if self.path[0] == edge.end_node:
            self.direction = 'down'
            self.position['coord_on_edge'] = edge.discretized_nb_part-1

        self.position['current_edge'].people_on_edge[self.position['coord_on_edge']].append(self)
        #print(self.position['current_edge'].people_on_edge)

    def contournement(self,edge):
        if self.distance_to(self.position['coord_x_y' ],self.path[0]) > 5:
            self.path.insert(0,tuple(self.position['coord_x_y']))
            self.position['coord_x_y'] = self.calcul_nouvelle_position()
            if self.direction == 'up':
                self.direction = 'down'
            else: 
                self.direction = 'up'

        if edge.end_node in graph.edges[edge.start_node]:
            graph.edges[edge.start_node].remove(edge.end_node) 
        if edge.start_node in graph.edges[edge.end_node]:
            graph.edges[edge.end_node].remove(edge.start_node) 
        #print(self.path)
        self.path =  graph.dijsktra(self.path[1] , self.path[-1]) 
        graph.blocked.append(edge)


    def deplacement(self):    
        def is_at_the_end_segment():
            
            if self == world.peoples[0] and len(self.position['current_edge'].people_on_edge) >2:
                #print()
                pass
                #print(self.position['current_edge'].people_on_edge)
            if (self.direction == 'up') and (self.position['coord_on_edge'] == self.position['current_edge'].discretized_nb_part-1):
                return True
            if (self.direction == 'down') and (self.position['coord_on_edge'] == 0):
                return True
            return False 

        def deplacement_possible(temporary_pos,temporary_edge):
            """if len(self.position['current_edge'].people_on_edge[temporary_pos]) >10:
                print(self.position['current_edge'].people_on_edge[temporary_pos])
                print(len(world.peoples))zz
                pygame.draw.rect(screen, (0,0,0), pygame.Rect(float(self.calcul_nouvelle_position()[0])*0.265-2, float(self.calcul_nouvelle_position()[1])*0.35, 10, 10))
            else:
                pygame.draw.rect(screen, (0,0,0), pygame.Rect(float(self.calcul_nouvelle_position()[0])*0.265-2, float(self.calcul_nouvelle_position()[1])*0.35, 10, 10))"""
            if len(temporary_edge.people_on_edge[temporary_pos]) >MAX_DENSITY_EDGE:
                self.color = (0,2,34)
            return len(temporary_edge.people_on_edge[temporary_pos]) <MAX_DENSITY_EDGE

        if not is_at_the_end_segment():
            if self.direction == 'up':
                temporary_pos = self.position['coord_on_edge'] +1
            else: 
                temporary_pos = self.position['coord_on_edge'] -1
            
            if deplacement_possible(temporary_pos,self.position['current_edge']):   #on peut mettre self.position['current_edge'] not in graph.blocked mais il faut faire rentrer people au dernier noeud avant d'appliquer djikstra
            #autre problème : si edge a disparu alors que le path est déjà défini => faire un test

                self.position['coord_x_y'] = self.calcul_nouvelle_position()
                #print([valeur for valeur in self.position['current_edge'].people_on_edge.values() if valeur != []])
                if len(self.position['current_edge'].people_on_edge[self.position['coord_on_edge']]) >MAX_DENSITY_EDGE:
                    #pygame.draw.rect(screen, (244,202,15), pygame.Rect(float(people.position['coord_x_y'][0])*0.265 -2, float(people.position['coord_x_y'][1])*0.35   , PEOPLE_SIZE*2, PEOPLE_SIZE*2))
                    from pygame import mixer
                    mixer.init() 
                    sound=mixer.Sound("sound.wav")
                    sound.play()
                    """print('peop world',len(world.peoples))
                    print(len(self.position['current_edge'].people_on_edge[self.position['coord_on_edge']]))
                    print([valeur for valeur in self.position['current_edge'].people_on_edge.values() if valeur != []])
                    print()"""
                if self in self.position['current_edge'].people_on_edge[self.position['coord_on_edge']]:  
                    self.position['current_edge'].people_on_edge[self.position['coord_on_edge']].remove(self)
                    if self in self.position['current_edge'].people_on_edge[self.position['coord_on_edge']]: 
                        print(self.position['current_edge'].people_on_edge[self.position['coord_on_edge']])
                    assert [self] not in [valeur for valeur in self.position['current_edge'].people_on_edge.values()], "deplacement possible"

                self.position['coord_on_edge'] = temporary_pos
                self.position['current_edge'].people_on_edge[temporary_pos].append(self)
                #print([valeur for valeur in self.position['current_edge'].people_on_edge.values()])
                #print('je suis là',[self] in [valeur for valeur in self.position['current_edge'].people_on_edge.values()])
            else:
                self.contournement(self.position['current_edge'])
        else: 
            if len(self.path[1:]) != 1:
                self.direction == 'up'
                unsure_path = self.path[1:]
                edge = graph.edges_object[(unsure_path[0],unsure_path[1])]
                if self.path[1:][0] == edge.end_node:
                    self.direction = 'down'

                if self.direction == 'up':
                    temporary_pos = 0
                else: 
                    temporary_pos = edge.discretized_nb_part -1
                
                if deplacement_possible(temporary_pos,self.position['current_edge']):
                    self.path = self.path[1:]
                    self.position['current_edge'].people_on_edge[self.position['coord_on_edge']].remove(self)
                    self.init_pos_on_segment()
            else:
                liste_attente = [self.path[1:][0]] + self.attraction_visited

                if set(liste_attente) != set(graph.attraction):
                    random_end = random.choice(list(set(graph.attraction) - set(liste_attente)))
                else:
                    self.attraction_visited = [self.path[1:][0]] #A enlever
                    random_end = random.choice(list(set(graph.attraction) - set(self.attraction_visited)))

                unsure_path = graph.dijsktra(self.path[1:][0] , random_end ) 

                self.direction == 'up'
                edge = graph.edges_object[(unsure_path[0],unsure_path[1])]
                if self.path[1:][0] == edge.end_node:
                    self.direction = 'down'

                if self.direction == 'up':
                    temporary_pos = 0
                else: 
                    temporary_pos = edge.discretized_nb_part -1
            
                if deplacement_possible(temporary_pos,self.position['current_edge']):

            #if len(self.path) == 1:
                    

                    if self.status == 'back_home':
                        world.peoples.remove(self)
                    
                        assert [self] not in [valeur for valeur in self.position['current_edge'].people_on_edge.values()], 'backhome'
                            
                    #self.status = "waiting"
                    self.attraction_visited.append(self.path[0])
                    if set(self.attraction_visited) != set(graph.attraction):
                        random_end = random.choice(list(set(graph.attraction) - set(self.attraction_visited)))
                    else:
                        random_end = random.choice(list(set(graph.starter)))
                        #self.status = 'back_home'  A remettre
                        
                        self.attraction_visited = [self.path[0]] #A enlever
                        
                        random_end = random.choice(list(set(graph.attraction) - set(self.attraction_visited))) #A enlever
                    self.path = self.path[1:]
                    self.path =  unsure_path
                    #print(self.path)
                    self.position['current_edge'].people_on_edge[self.position['coord_on_edge']].remove(self)
                    #print('toto')
                    self.init_pos_on_segment()
        
    def changement_vitesse_densité():
        pass


    def new_people(self):
        current_position = random.choice(list(graph.starter))
        wished_position = random.choice(list(graph.attraction))
        self.path = graph.dijsktra(current_position , wished_position) 
        #print(self.path)
        if len(self.path) >1: 
            self.init_pos_on_segment()
            world.peoples += [people]

class World:
    def __init__(self):
        self.peoples = []
        self.edges = []

    def init_edges(self):
        for edge in svg_parser.edges:
            edge_object = Edge(
                start_node = edge[0],
                end_node = edge[1],
                length = graph.distance_to(edge[0],edge[1]),
                discretized_nb_part = int(graph.distance_to(edge[0],edge[1])//PEOPLE_SIZE))

            graph.edges_object[(edge[0],edge[1])] = edge_object
            graph.edges_object[(edge[1],edge[0])] = edge_object
            graph.edges[edge[0]].append(edge[1]) 
            graph.edges[edge[1]].append(edge[0]) 
            graph.weights[(edge[0], edge[1])] = graph.distance_to(edge[0],edge[1])
            graph.weights[(edge[1], edge[0])] = graph.distance_to(edge[0],edge[1])
            self.edges.append(edge_object)

world = World()
world.init_edges()


while True:
    keys=pygame.key.get_pressed()  
    screen.blit(image, (0,0))
    ensemble = (set(graph.edges_object.values()) - set(graph.blocked))
    for edge in ensemble:
        start = edge.start_node 
        end = edge.end_node
        color = (12,210,36)
        """pygame.draw.rect(screen, color, pygame.Rect(float(start[0])*0.265-2, float(L[0][1])*0.35, 10, 10))
        pygame.draw.rect(screen, color, pygame.Rect(float(L[1][0])*0.265-2, float(L[1][1])*0.35, 10, 10))"""
        pygame.draw.line(screen,color,(float(start[0])*0.265-2, float(start[1])*0.35),(float(end[0])*0.265-2, float(end[1])*0.35))
    
    for people in world.peoples:
        pygame.draw.rect(screen, people.color, pygame.Rect(float(people.position['coord_x_y'][0])*0.265 -2, float(people.position['coord_x_y'][1])*0.35   , PEOPLE_SIZE, PEOPLE_SIZE))
        #if people.status == "moving":
        people.deplacement()  

    """for edge in graph.blocked:
        if max([len(case) for case in edge.people_on_edge.values() if case != []]) < MAX_DENSITY_EDGE:
            graph.blocked.remove(edge)
            graph.edges[edge.end_node].append(edge.start_node)
            graph.edges[edge.start_node].append(edge.end_node)"""
        

    pygame.display.flip()

    for event in pygame.event.get(): 
        if event.type == pygame.KEYUP:
            if keys[K_UP]:
                pygame.quit()
                sys.exit()

            if keys[K_a]:
                for i in range(1):                
                    people = People()
                    people.new_people()
                
            if keys[K_z]:
                print(len(world.peoples))