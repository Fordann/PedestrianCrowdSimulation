from xml.dom import minidom
import math

doc = minidom.parse("BACK_test.svg")  # parseString also exists
path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]

categories = [element for element in doc.getElementsByTagName('g')][1:]
starter = [ (element.getAttribute('cx'), element.getAttribute('cy')) for element in categories[0].childNodes if element.nodeType != 3 ]
attraction =  [(element.getAttribute('cx'), element.getAttribute('cy')) for element in categories[1].childNodes if element.nodeType != 3 ]
carrefour = [ (element.getAttribute('cx'), element.getAttribute('cy')) for element in categories[2].childNodes if element.nodeType != 3 ]
edges =  [[element.split(",") for element in "".join(list(element.getAttribute('d'))[0:]).split()] for element in categories[3].childNodes if element.nodeType != 3 ]
import copy
#A enlever
starter = [attraction[3]]+[attraction[10]]
attraction = copy.deepcopy(starter)
def distance_to(position1,position2): #necessite 
    return math.sqrt((float(position1[0]) - float(position2[0]))**2 + (float(position1[1]) - float(position2[1]))**2)

def coord_approximation(point): 
        candidat = starter + attraction + carrefour
        approximation = (candidat[0] , distance_to(candidat[0],point))
        for coord in candidat:                          #méthode du candidat
            distance = distance_to(coord,point)
            if approximation[1] > distance:
                approximation = [coord,distance]
        return (approximation[0][0],approximation[0][1])

edges_copy = []

for edge in edges:
    x=float(edge[2][0])
    y=float(edge[2][1])
    if edge[0][0]=='m':
        x = float(edge[1][0]) + x
        y = float(edge[1][1]) + y
    edges_copy.append((coord_approximation(edge[1]),coord_approximation([x,y])))
edges = edges_copy

