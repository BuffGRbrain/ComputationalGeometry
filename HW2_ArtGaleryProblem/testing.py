import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random as rd
import copy as cp
from diagonal import addDiag,print_semiedges,print_vertex,print_faces,print_incident_faces, print_ciclos


class Segment(object):
    def __init__(self, upper, lower):
        self.upper = upper #is the upper point in the format (x,y)
        self.lower = lower #is the lower point in the format (x,y)

    def __str__(self):
        return "Segmento: " + str(self.upper) + " " + str(self.lower)

class Vertice(object):
    def __init__(self, name, x, y, edge_incidente=None, typee=None,label = None):
        self.name = name
        # this is a point from the class above or [x,y]
        self.coordinate = [x, y]
        self.edge_incidente = edge_incidente  # this is una arista de la clase arista
        self.typee = None  # to identify node type and prevent confusing it with the python function, the type is the initial in spanish
        self.label = label
    def __repr__(self) -> str:
        return f"{self.name}"

class SemiEdge(object):
    def __init__(self, name=None, origin=None, cara_incidente=None, twin=None, next=None, previous=None, helper=None, label = None):
        self.name = name
        self.origin = origin  # this is a vertice object
        # this is a name of the object same as this one
        self.cara_incidente = cara_incidente
        self.next = next  # this is a name of the object same as this one
        self.previous = previous  # this is a name of the object same as this one
        self.twin = twin  # only the name of the object
        self.helper = helper  # only the name of the object
        self.label = label

    def __repr__(self)-> str:
        return f"{self.name},{self.origin},{self.next.origin}"

    def add2plot(self): #Adding a segment to the current plot, using its start/end points and label if any
        plt.plot([self.origin.coordinate[0], self.next.origin.coordinate[0]], [self.origin.coordinate[1], self.next.origin.coordinate[1]], '-', label=self.name)

def plotSemiEdges(list_of_semiedges): #Helper to plot either Edges or SemiEdges
    for i in list_of_semiedges:
        i.add2plot()


class Cara(object):
    def __init__(self, name=None, interior_frontier=None, exterior_frontier=None,ciclo = None):
        self.name = name
        self.interior_frontier = interior_frontier  
        self.exterior_frontier = exterior_frontier
        self.ciclo = ciclo
    def __repr__(self)-> str:
        return f"{self.name},{self.interior_frontier},{self.exterior_frontier}"

# Input 2 points in R2 in the format of list
# Output the point who goes firts accodirginly to the ordering rule


def is_first(p0, p1):  # new ordering symbol
    if (p0[1] == p1[1]):
        if (p0[0] < p1[0]):  # the == case doesn´t exist since the points are different
            return p0
        else:
            return p1
    elif (p0[1] > p1[1]):
        return p0
    else:
        return p1

#Input: list of points in R2 that represent the polygon
#Output: list of edges in the polygon,list of vertex,list of semi edges, list of twins semi edges and list of faces
def create_semi_edges(list_of_points):  
    list_of_semi_edges = []
    list_of_vertex = []
    list_of_twins_semi_edges = []
    list_of_faces = []
    # create the vertex
    for i in range(len(list_of_points)):
        list_of_vertex.append(Vertice( f"v{i}", list_of_points[i][0], list_of_points[i][1], f"e{i}1" )) #arbitrariamente decido registrar los del ciclo interno
    # create the semi edges, ESTAS SON LAS DE LA CARA INTERIOR
    for i in range(len(list_of_vertex)):
        list_of_semi_edges.append(SemiEdge(f"e{i}1", list_of_vertex[i-1])) #-1 pues el nombre esta asociado al incidente de ese nodo, por lo tanto el origen sera el anteriora ese
    #create the twins semi edges
    for i in range(len(list_of_vertex)):
        list_of_twins_semi_edges.append(SemiEdge(f"e{i}2", list_of_vertex[i], twin=list_of_semi_edges[i]))#i y no i-1 pues es el twin, y la pose i pues se creo en un for del mismo tamaño
    #Asign the next and previous and twin, to the semi edges and twins semi edges
    for i in range(len(list_of_vertex)):
        list_of_semi_edges[i].next = list_of_semi_edges[(i+1)%len(list_of_semi_edges)]
        list_of_semi_edges[i].previous = list_of_semi_edges[i-1] #we dont need module since python manages the negative index
        list_of_semi_edges[i].twin = list_of_twins_semi_edges[i]
        list_of_twins_semi_edges[i].next = list_of_twins_semi_edges[(i+1)%len(list_of_twins_semi_edges)]
        list_of_twins_semi_edges[i].previous = list_of_twins_semi_edges[i-1]
    #Now we need to assign the edge_incidente to the vertex
    for i in range(len(list_of_vertex)):
        #como tenemos el nombre del incidente debemos usarlo para relacionarlo con el objeto
        name = list_of_vertex[i].edge_incidente #Pues inicialmente es un string
        incidente = [i for i in list_of_semi_edges if i.name == name][0] #Pues es un objeto
        list_of_vertex[i].edge_incidente = incidente#Pues ahora es un objeto
    #TODO:incidente es de la cara interior
    #create the faces
    #only 2 faces, the exterior and the interior, for semi edges and twins semi edges respectively
    list_of_faces.append(Cara(name = "f1", interior_frontier = None, exterior_frontier = list_of_semi_edges[0]))
    list_of_faces.append(Cara(name = "f2", interior_frontier = list_of_twins_semi_edges[0], exterior_frontier = None))
    #assign the incident face to the semi edges and twins semi edges
    for i in range(len(list_of_vertex)):
        list_of_semi_edges[i].cara_incidente = list_of_faces[0]
        list_of_twins_semi_edges[i].cara_incidente = list_of_faces[1]
    return list_of_semi_edges, list_of_vertex, list_of_twins_semi_edges, list_of_faces


#Input: list of semiedges correspondent to the interior face, list of vertex
#Output: same input but updated with the labels
def labels(list_semiedges,list_vertex):

    menor = list_vertex[0]
    ##print("menor inicial",menor)
    for i in list_vertex:
        if is_first(i.coordinate,menor.coordinate) == i.coordinate:
            menor = i
    ##print("menor encontrado",menor,"vertice incidente menor",menor.edge_incidente.name)
    
    ##print("Datos de e121",)
    index_menor = list_semiedges.index(menor.edge_incidente)
    index_menorv = list_vertex.index(menor)
    menor.label = 1
    menor.edge_incidente.label = 1
    #Ahora lo reemplazamos en list_semiedges para que se actualice el dato
    list_semiedges[index_menor] = menor.edge_incidente#Actualizamos
    list_vertex[index_menorv] = menor#Actualizamos
    ##print(menor.label ,"ha sido actualizado")
    #Ahora enumeramos los demas hacia la izquierda
    n = len(list_vertex) #Para el modulo
    actualv = menor.edge_incidente.origin
    
    ##print("siguiente: ",actualv.name, actualv.edge_incidente.name)
    ##print("soy n: ",n)
    for i in range(2,n+1): #desde 2 pues el 1 ya lo usamos y +1 pues el range no incluye el ultimo
        index_actualv = list_vertex.index(actualv)
        index_actualv_edge = list_semiedges.index(actualv.edge_incidente)
        #print(actualv.name,actualv.edge_incidente.name,"i actual: ",i)
        actualv.label = i
        actualv.edge_incidente.label = i
        #Ahora lo reemplazamos en list_semiedges para que se actualice el dato
        
        list_semiedges[index_actualv_edge] = actualv.edge_incidente#Actualizamos
        list_vertex[index_actualv] = actualv#Actualizamos
        #Ahora pasamos al siguiente vertice
        ##print("Actual: ", actualv.name,"siguiente: ",actualv.edge_incidente.origin.name)
        actualv = actualv.edge_incidente.origin

    return list_semiedges,list_vertex

def product2d(p_0, p_origin, p_destiny):
    d = ((p_origin[0]-p_0[0])*(p_destiny[1]-p_0[1])) - \
        ((p_origin[1]-p_0[1])*(p_destiny[0]-p_0[0]))
    return d

# segmento p_0 a p_1 y para ir a p_dest retorno el sentido en que debe ir
def where2turn(p_0, p_1, p_dest):
    d = product2d(p_0, p_1, p_dest)
    if (d > 0):
        direccion = -1  # "Sentido horario",der
    elif (d < 0):
        direccion = 1  # "Sentido antihorario", izq
    else:
        direccion = 0  # "Son colineales"
    return direccion

# Input:list_vertex a list of vertex objects from the class vertex. and a list of semiedges from the class semiedge
# Output: A list of vertex with the atribute typee != None #double e to prevent confusion with the reserved word
def nodeType(list_vertex, list_of_semiedges):
    # vecinos son los dos siguientes en la lista de vertices

    # el ciclo nos sirve pues la cardinalidad de las aristas es la misma que los nodos
    for i in list_of_semiedges:  # usamos esto para tener contexto sobre en que dirección calculamos el giro
        p0 = i.origin
        p1 = i.next.origin  # este es el que estoy revisando
        p2 = i.next.next.origin  # this will always exist since its a cycle
        # para conocer el indice del vertice que estoy revisando
        index_p1 = list_vertex.index(p1)
        if is_first(p1.coordinate, p2.coordinate) == p1.coordinate and is_first(p1.coordinate, p0.coordinate) == p1.coordinate:  # inicio o division

            # giro a derecha o colineal indica menor a pi, entonces es inicio
            if where2turn(p0.coordinate, p1.coordinate, p2.coordinate) <= 0:
                p1.typee = "division"

            else:
                p1.typee = "inicio"

        elif is_first(p1.coordinate, p2.coordinate) == p2.coordinate and is_first(p1.coordinate, p0.coordinate) == p0.coordinate:  # fin o union
            # giro a derecha o colineal indica menor a pi, entonces es inicio
            if where2turn(p0.coordinate, p1.coordinate, p2.coordinate) <= 0:
                p1.typee = "Union"
            else:
                p1.typee = "Fin"

        else:  # Es regular
            p1.typee = "regular"
        # ya que lo revisamos lo reemplazamos por si mismo
        list_vertex[index_p1] = p1  # ahora incluye el tipo
    return list_vertex  # ya esta modificado en el ciclo for

#Punto de cruce con la linea de barrido para ubicar el semiedge
def xk(s,y):#y es la altura actual de la linea de barrido
        if s.lower[1]-s.upper[1] == 0: #es un segmento horizontal
            print("segmento horizonal vuelva a intentar")
        alpha = (y-s.upper[1]) / (s.lower[1]-s.upper[1])
        return alpha*s.lower[0] + (1-alpha)*s.upper[0]

#Input: vertice actual
#Output: bool 1 para izquierda y 0 para derecha
def ladoPoligono(vi):#vi actual
    #debemos obtener el previo y el siguiente para comparar
    actual = vi
    previo = actual.edge_incidente.origin
    siguiente = actual.edge_incidente.next.next.origin
    #Ahora vamos a comparar coordenada y y los labels
    if previo.label<actual.label and actual.label<siguiente.label: #subindice crece
        if previo.coordinates[1]<actual.coordinates[1] and actual.coordinates[1]<siguiente.coordinates[1]:
            return 1 #SIGNIFICA QUE ESTA A LA IZQUIERDA
    elif previo.label>actual.label and actual.label>siguiente.label:
        return 0 #no es necesario revisar las coordenadas y pues decir que el subindice crece y la coordenada y tambien equiavale a decir que el subindice decrece
        

def eizq(vi,Tao,y):#buscamos el que esta mas cerca a vi por la izquierda
    #if Tao:
        ##print("Tao no esta vacio")
    #for i in Tao:
        ##print("DE TAO")
        ##print(i.name)
    xks = [xk(Segment(i.origin.coordinate,i.next.origin.coordinate),y) for i in Tao] #Indice nos asocia el semiedge con su xk
    #print(xks)
    #Hay un caso donde se rompe, cuando el semiedge es horizontal
    #print(vi.coordinate[0])
    xks_izq = [i for i in xks if i<=vi.coordinate[0]] #semiedges que estan a la izquierda de vi segun coordenada x
    #print(xks_izq)
    eizq = Tao[xks.index(max(xks_izq))] #semiedge izquierdo, tomamos el máximo de los que esta a la izquierda pues será el más cercano
    #print(f"eizq: {eizq.name}")
    return eizq

#######################SWEEPLINE Auxiliar functions#######################


#######################SWEEPLINE Main function#######################
#Input: list of semiedges, list of points (list of vertex)
#OPutput: list of list of semiedges each representing a monotone polygon (each list of semiedges is a monotone polygon).

def monotone_yparts(list_of_semiedges,list_of_points,list_faces): #este listof points son tuplas y no objetos de la clase vertex
    #primero encontramos los tipos de vertice
    #list_vertex = [i.origin for i in list_of_points] #lista de vertices
    #ya desde antes cada nodo tiene su tipo asignado y su label
    n = len(list_of_points)+1 #numero de vertices, +1 para un caso especial y no obviar el label de n
    #order given list of points using the is_first function
    #Q = sorted(list_of_points,key=lambda v: v.coordinate if v.coordinate else [0, 0], cmp=is_first) #ordenamos los puntos de acuerdo a la funcion is_first
    
    Q = [list_of_points[0]]
    for i in range(len(list_of_points)):
        counter = 0
        for j in range(len(Q)):#por alguna razón agrega el 0 dos veces
            if is_first(list_of_points[i].coordinate,Q[j].coordinate) == list_of_points[i].coordinate and counter == 0 and list_of_points[i] not in Q: #si esta primero que ese j lo insertamos antes y prueba con todos hasta encontrar su lugar. 
                Q.insert(j,list_of_points[i])
                counter = 1
                break # solo quiero insertarlo una vez
            elif list_of_points[i] == Q[j]:
                counter = 1
                break
        if counter == 0: #si no lo inserto en ningun lugar, lo insertamos al final
            Q.append(list_of_points[i])
    #print("#"*20,"Q ordenado","#"*20)
    #print_vertex(Q)
    #print("#"*20,"Q ordenado","#"*20)
    count = 0
    
    Tao = [] #tao is a dictionary that hast the pair vertex, helper
    #tao tambien usa la regla de orden rara para el insert
    while len(Q)>0: #Q acts as a FIFO queue, mientras Q no este vacio
        #Qs = [[i.name,i.label] for i in Q]
        ##print(Qs)
        vi = Q[0] #vi es el primer elemento de Q
        y = vi.coordinate[1] #Altura actual de la linea de barrido
        Q.remove(vi)
        #print(vi.typee)
        ##print("Actualmente en TAO")
        #for i in Tao:
        #    #print(i.name,i.label,i.helper.name,i.helper.label)
        
        ##print("Fin elmentos en TAO")
        if vi.typee == "inicio":
            ei = vi.edge_incidente
            ei.helper = vi
            #print("semiedge a insertar en tao ", ei.name)
            Tao.append(ei) #insertamos el semiedge en tao, el cual tiene el dato de helper ya asignado
        elif vi.typee == "Fin":
            Tao,list_of_semiedges, list_faces = manipular_fin(vi,Tao,n,list_of_semiedges,list_faces)
        elif vi.typee == "division":
            Tao,list_of_semiedges, list_faces = manipular_division(vi,y,Tao,list_of_semiedges, list_faces)
        elif vi.typee == "Union":
            Tao,list_of_semiedges, list_faces = manipular_union(vi,y,Tao,n,list_of_semiedges,list_faces)
        else: #es regular
            Tao,list_of_semiedges, list_faces = manipular_regular(vi,n,Tao,list_of_semiedges,list_faces,y)
    return list_of_semiedges, list_faces

#Input:
#Output:Listas modificadas
def manipular_fin(vi,Tao,n,list_of_semiedges,list_faces):
    ##print("Fin name y label ", vi.name,vi.label)
    label_eim1 = (vi.label-1) % n #Modulo n para que no se salga del rango
    ##print(label_eim1)
    eim1_aux = [i for i in Tao if i.label == label_eim1] #encontramos el semiedge que tiene como helper al objeto
    while eim1_aux == []:
        eim1_aux = [i for i in Tao if i.label == label_eim1-1]
    eim1= eim1_aux[0]
    ##print("Fin eim1",eim1.name,eim1.helper.name)
    if eim1.helper.typee == "Union":
        #Agregar una diagonal que conecta vi con el helper de eim1
        diag = [vi,eim1.helper]
        list_of_semiedges, list_faces = addDiag(list_of_semiedges,list_faces,diag)
    Tao.remove(eim1) #tiene que estar para poder borrarla
    return Tao,list_of_semiedges, list_faces


def manipular_union(vi,y,Tao,n,list_of_semiedges,list_faces):
    ##print("Union name y label ", vi.name,vi.label)
    label_eim1 = (vi.label-1) % n #Modulo n para que no se salga del rango
    eim1 = [i for i in Tao if i.label == label_eim1][0] #encontramos el semiedge que tiene como helper al objeto
    ##print("Union eim1",eim1.name,eim1.helper.name)
    if eim1.helper.typee == "Union":
        #Agregar una diagonal que conecta vi con el helper de eim1
        diag = [vi,eim1.helper]
        list_of_semiedges, list_faces = addDiag(list_of_semiedges,list_faces,diag)
    Tao.remove(eim1) #tiene que estar para poder borrarla
    ej = eizq(vi,Tao,y) #encontramos el semiedge a la izquierda de vi
    if ej.helper.typee == "Union":
        #Agregar una diagonal que conecta vi con el helper de eim1
        diag = [vi,ej.helper]
        list_of_semiedges, list_faces = addDiag(list_of_semiedges,list_faces,diag)
    Tao.remove(ej) #Lo borramos antes del update pq si no no lo encuentra
    ej.helper = vi
    #ahora debemos el existente ej en tao por este que tiene el helper actualizado
    Tao.append(ej)
    return Tao,list_of_semiedges, list_faces

def manipular_division(vi,y,Tao,list_of_semiedges, list_faces):
    ##print("Y = ",y)
    ej = eizq(vi,Tao, y) #encontramos el semiedge a la izquierda de vi
    diag = [vi,ej.helper]
    list_of_semiedges, list_faces = addDiag(list_of_semiedges,list_faces,diag)
    #Actualizando ej en tao
    Tao.remove(ej) #Lo borramos antes del update pq si no no lo encuentra
    ej.helper = vi #puedo hacerlo pq lo saque de tao
    Tao.append(ej)
    #AGREGANDO ei a TAO
    ei = vi.edge_incidente
    ei.helper = vi #Ahora debemos actualizar en tao y list_of_semiedges
    Tao.append(ei) #ya actualizado

    return Tao,list_of_semiedges, list_faces

def manipular_regular(vi,n,Tao,list_of_semiedges,list_faces,y): #n es el numero de vertices en el poligono
    ##print("regular name y label ", vi.name,vi.label)
    if ladoPoligono(vi) == 1:#si esta a la izquierda
        label_eim1 = (vi.label-1) % n #Modulo n para que no se salga del rango
        eim1 = [i for i in Tao if i.label == label_eim1][0] #encontramos el semiedge que tiene como helper al objeto
        ##print("regular eim1",eim1.name,eim1.helper.name)
        if eim1.helper.typee == "Union":
            diag = [vi,eim1.helper]
            list_of_semiedges, list_faces = addDiag(list_of_semiedges,list_faces,diag)
        Tao.remove(eim1)
        ei = vi.edge_incidente
        ei.helper = vi
        Tao.append(ei)
    else: #esta a la derecha
        ej = eizq(vi,Tao,y) 
        if ej.helper.typee == "Union":
            diag = [vi,ej.helper]
            list_of_semiedges, list_faces = addDiag(list_of_semiedges,list_faces,diag)
        Tao.remove(ej) #LO borramos antes del update pq si no no lo encuentra
        ej.helper = vi
        #ahora debemos el existente ej en tao por este que tiene el helper actualizado
        Tao.append(ej)
    return Tao,list_of_semiedges, list_faces
#######################SWEEPLINE Main function#######################




#Testing
#Borramos el último elemento pq esta duplicado
P = [(9, 0.5), (8, 6), (7, -3), (6, 3), (4, -4), (2, -3), (3, 4), (4, 2.5), (5, 12), (7, 8.5), (8, 12), (9.5, 11), (11, 15), (13, 13), (12, 10), (13, 3), (11, 4), (10, -1)]

list_of_semi_edges, list_of_vertex, list_of_twins_semi_edges, list_of_faces = create_semi_edges(P)
list_of_vertex = nodeType(list_of_vertex, list_of_semi_edges)

#print_vertex(list_of_vertex)
#print_semiedges(list_of_semi_edges)
list_of_semi_edges,list_of_vertex = labels(list_of_semi_edges,list_of_vertex) #le paso twins pues es la cara interior que es la que no cambia
#Ahora debemos poner los tipos de nodo

plotSemiEdges(list_of_semi_edges)
plt.show()

list_of_semi_edges, list_of_faces = monotone_yparts(list_of_semi_edges,list_of_vertex,list_of_faces) #Actualiza mal los semiedges 
plotSemiEdges(list_of_semi_edges)
plt.show()

piezas_monotonas = cp.deepcopy(list_of_semi_edges)
caras_monotonas = cp.deepcopy(list_of_faces)

#print("Despues de enumerar")
#print_vertex(list_of_vertex)

# create data frames for each attribute of the classes

#print_semiedges(list_of_semi_edges)

#repetimos para la cara interior
#print_incident_faces(list_of_twins_semi_edges)

#print_faces(list_of_faces)

#print_ciclos(list_of_faces)

print("#################################################################################################################################################################################################################################")
print("FIN DE PIEZAS MONOTONAS")
print("#################################################################################################################################################################################################################################")
