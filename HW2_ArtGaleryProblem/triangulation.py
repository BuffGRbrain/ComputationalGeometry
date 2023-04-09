import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import testing as tst
from diagonal import addDiag,print_semiedges,print_vertex,print_faces,print_incident_faces, print_ciclos, create_semi_edges, check_SE
from copy import deepcopy

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

#Input: list of vertex
#Output: Q list of vertex with the labels_t according to the ordering rule is_first
def labels_t(list_vertex):
    Q = [list_vertex[0]]
    for i in range(len(list_vertex)):
        counter = 0
        for j in range(len(Q)):
            if is_first(list_vertex[i].coordinate,Q[j].coordinate) == list_vertex[i].coordinate and counter == 0 and list_vertex[i] not in Q: #si el punto es el primero y no esta en la lista
                Q.insert(j,list_vertex[i])
                counter = 1
                break # solo quiero insertarlo una vez
            elif list_vertex[i] == Q[j]:
                counter = 1
                break
        if counter == 0: #si no lo inserto en ningun lugar, lo insertamos al final
            Q.append(list_vertex[i])
    #Tras ordenarlo, debemos asignarle el label
    for i in range(len(Q)):
        Q[i].label = i+1

    return Q

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

#Punto de cruce con la linea de barrido para ubicar el semiedge
def xk(s,y):#y es la altura actual de la linea de barrido
        if s.lower[1]-s.upper[1] == 0: #es un segmento horizontal
            print("segmento horizonal vuelva a intentar")
        alpha = (y-s.upper[1]) / (s.lower[1]-s.upper[1])
        return alpha*s.lower[0] + (1-alpha)*s.upper[0]

#Input: vertice actual
#Output: bool 1 para izquierda y 0 para derecha
def ladoPoligono(vi,actual_face):#vi actual
    #debemos obtener el previo y el siguiente para comparar
    #actual = vi
    #previo = actual.edge_incidente.origin
    #siguiente = actual.edge_incidente.next.next.origin

    #Usamos actual pues el previo y el siguiente deben pertenecer a la cara actual
    actual = vi
    list_semiedges_actuales = actual_face.ciclo
    actual_edge = [i for i in list_semiedges_actuales if i.origin == actual][0] #semiedge que sale del vertice actual
    previo = actual_edge.previous.origin
    siguiente = actual_edge.next.origin #solo un next pues equivale a estar en next del incicente

    #Ahora vamos a comparar coordenada y y los labels
    print("----------Imrpimiendo lado polígono------"*10)
    print_vertex([actual,previo,siguiente])
    print("--------------------"*10)
    if previo.coordinate[1]<siguiente.coordinate[1]:
        return 1 #SIGNIFICA QUE ESTA A LA IZQUIERDA
    else:
        return 0 #SIGNIFICA QUE ESTA A LA DERECHA

def diagValida(vi,vdest,S_1,actual_face):
    if check_SE(list_semiedges,[vi,vdest]):#Revisar si la diagonal ya existe
        return 0
    if is_first(vi.coordinate,vdest.coordinate) == vi.coordinate: #Si origen es mas alto debo modificarlos, pues para usar S_1 necesito que el origen sea el mas bajo
        aux = deepcopy(vi)
        vi = vdest
        vdest = aux
    #Si peta cambiar output de where2turn, TODO thanks past me
    if ladoPoligono(vi,actual_face) == 1:#si esta a la izquierda
        print("esta a la izquierda, el vertice es: ",vi.name)
        if where2turn(vi.coordinate,S_1.coordinate,vdest.coordinate) == 1:#esta a la derecha de S_1
            return 1
        else:
            return 0
    else:#si esta a la derecha
        if where2turn(vi.coordinate,S_1.coordinate,vdest.coordinate) == -1:#esta a la izquierda de S_1
            return 1
        else:
            return 0
#######################SWEEPLINE Auxiliar functions#######################


#######################Y-monotone polygon#################################

#Input: list of semiedges correspondent to the interior face, list of vertex
#Output: same input but updated with the labels
def labels(list_semiedges,list_vertex):

    menor = list_vertex[0]
    #print("menor inicial",menor)
    for i in list_vertex:
        if is_first(i.coordinate,menor.coordinate) == i.coordinate:
            menor = i
  #  print("menor encontrado",menor,"vertice incidente menor",menor.edge_incidente.name)
    
   # print("Datos de e121",)
    index_menor = list_semiedges.index(menor.edge_incidente)
    index_menorv = list_vertex.index(menor)
    menor.label = 1
    menor.edge_incidente.label = 1
    #Ahora lo reemplazamos en list_semiedges para que se actualice el dato
    list_semiedges[index_menor] = menor.edge_incidente#Actualizamos
    list_vertex[index_menorv] = menor#Actualizamos
    #print(menor.label ,"ha sido actualizado")
    #Ahora enumeramos los demas hacia la izquierda
    n = len(list_vertex) #Para el modulo
    actualv = menor.edge_incidente.origin
    
    #print("siguiente: ",actualv.name, actualv.edge_incidente.name)
    #print("soy n: ",n)
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
        print("Actual: ", actualv.name,"siguiente: ",actualv.edge_incidente.origin.name)
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


def eizq(vi,Tao,y):#buscamos el que esta mas cerca a vi por la izquierda
    '''
    if Tao:
        print("Tao no esta vacio")
    for i in Tao:
        print("DE TAO")
        print(i.name)
    '''
    xks = [xk(Segment(i.origin.coordinate,i.next.origin.coordinate),y) for i in Tao] #Indice nos asocia el semiedge con su xk
    #print(xks)
    #Hay un caso donde se rompe, cuando el semiedge es horizontal
    #print(vi.coordinate[0])
    xks_izq = [i for i in xks if i<=vi.coordinate[0]] #semiedges que estan a la izquierda de vi segun coordenada x
    #print(xks_izq)
    eizq = Tao[xks.index(max(xks_izq))] #semiedge izquierdo, tomamos el máximo de los que esta a la izquierda pues será el más cercano
    #print(f"eizq: {eizq.name}")
    return eizq
 
#######################SWEEPLINE Main function#######################

#######################Y-monotone polygon#################################




#######################SWEEPLINE Main function#######################
#Input:Poligono simple y-monotono dado por su cara interior, lista de semiedges de la cara exterior y lista de vertices
#Output: triangulacion de poligono
def triangulate(list_semiedges,list_vertex,list_faces,actual_face):
    #Ordenamos con la regla de orden rara y ademas asignamos un label a cada vertice
    Q = labels_t(list_vertex)
    S = []
    #Agregamos los primeros 2 elementos, U1 y U2
    S.append(Q[1]) #se nete así pq el último en ingresar debe quedar en la 0 y el append ingresa al final
    S.append(Q[0])

    n = len(Q)

    #Hasta n pq TODO HACK YOLO
    for i in range(2,n): #desde 2 y no 3 pq python inicio en 0
        print("S ACTUAL ",S,"iteracion ",i)
        #TODO:HACER FUNCION LADO POLIGONO
        #usar funcion ladoPoligono_t(S[0],list_semiedges)  pq la actual corresponde a la notación previa
        a = ladoPoligono(Q[i],actual_face) #ESTA DANDO NONE REVISAR PQ
        b = ladoPoligono(S[0],actual_face)

        print("Lados poligono para los vertices dados: ",a,b)
        if a != b : #si son de lados distintos
            print("estan en lados distintos: ",S[0].name," y ",Q[i].name)
            while len(S)!=1: #Si es uno entonces no lo hace con el último elemento TODO: revisar
                print("S ACTUAL ",S)
                if diagValida(S[0],Q[i],S[1],actual_face):# or diagValida(Q[i],S[0],list_semiedges): #si es valida, ese or es un failsafe
                    #Agregamos la diagonal
                    diagonal = [S[0],Q[i]]

                    print("---------------------Agregando diagonal---------------------",diagonal[0].name," y ",diagonal[1].name,"---------------------")

                    list_semiedges, list_faces = addDiag(list_semiedges,list_faces,diagonal)
                    #Eliminamos el primer elemento de S
                    S.pop(0)
                else:
                    print("No es valida digonal entre: ",S[0].name," y ",Q[i].name," y ",S[1].name)
                    S.pop(0) #Si no es posible trazar la diagonal igual eliminamos el primer elemento de S
            print("Sali del while del if: ",S)
            S.pop(0) #Eliminamos el elemento que hace falta de S con el que no intentamos trazar la diagonal
            S.insert(0,Q[i-1])#TODO:CHECK ORDEN
            S.insert(0,Q[i]) #Agregamos uj-1 y uj, usamos insert pues simulamos un stack entonces los que entran deben estar al principio de la lista
            print("S ACTUAL ",S)
        else: #si son del mismo lado
            print("estan en el mismo lado: ",S[0].name," y ",Q[i].name)
            print("iteracion: ",i," S: ",S)
            aux2 = S.pop(0) #Eliminamos el primer elemento de S
            while len(S)!=0: #lo hacemos con todos
                print("S ACTUAL ",S)
                #aux = S.pop(0) #Aprovechando que pop elimina el elemento, lo guardamos en aux
                print("S ACTUAL ",S)
                if len(S)==1: 
                    if diagValida(aux2,Q[i],S[0],actual_face): 
                        #Agregamos la diagonal
                        diagonal = [aux,Q[i]]
                        print("---------------------Agregando diagonal---------------------",diagonal[0].name," y ",diagonal[1].name,"---------------------")
                        list_semiedges, list_faces = addDiag(list_semiedges,list_faces,diagonal)
                        #Eliminamos el primer elemento de S
                        #PUES YA LLEGO AL ULTIMO ELEMENTO DE S
                        break
                    else: #cuando no es valida
                        #S.insert(0,aux)
                        print("---------------------Agregando aux a S pq no fue valida------------------------------------------")
                        S.insert(0,aux2)
                        print("S ACTUAL ",S)
                        break
                aux2 = S.pop(0)   
                #aux = S.pop(0) #Aprovechando que pop elimina el elemento, lo guardamos en aux
                #aux2 = aux
                if diagValida(aux2,Q[i],S[0],actual_face): #S[0] EQUIVALE A S[1] que pide diagValida pues acabamos de borrar uno
                    #Agregamos la diagonal
                    diagonal = [aux2,Q[i]]
                    print("---------------------Agregando diagonal---------------------",diagonal[0].name," y ",diagonal[1].name,"---------------------")
                    list_semiedges, list_faces = addDiag(list_semiedges,list_faces,diagonal)
                    #Eliminamos el primer elemento de S
                else: #cuando no es valida
                    #S.insert(0,aux) TODO sobra pq al final lo inserto entonces se repetiria
                    print("---------------------Agregando aux a S pq no fue valida------------------------------------------")
                    S.insert(0,aux2) #SI NO SE AGREGA DIAGONAL SE DEVUELVE EL ELEMENTO A S
                    print("S ACTUAL ",S)
                    break
            print("S ACTUAL ",S)
            S.insert(0,aux2) #Agreamos el último elemento eliminado
            S.insert(0,Q[i]) #Agregamos uj
            print("tras while: ",i," S: ",S)
    #Agregamos la ultima diagonal
    U_n = Q[-1]
    for i in S: #Si S solo tiene 2 elementos, no hace nada en el for
        print("S ACTUAL en ultimo for",S)
        if diagValida(U_n,i,S[1],actual_face):# or diagValida(i,U_n,list_semiedges): #SI es valida la agregamos dlc no
            diagonal = [U_n,i]
            print("---------------------Agregando diagonal---------------------",diagonal[0].name," y ",diagonal[1].name,"---------------------")
            list_semiedges, list_faces = addDiag(list_semiedges,list_faces,diagonal)
    return list_semiedges, list_faces


#######################SWEEPLINE Main function#######################

###############Helper para hacerlo con todas las piezas y-monotonas###############

def triangle_all(list_semiedges,list_faces):
    copy_faces = deepcopy(list_faces)
    #OBTENIENDO TODAS LAS PIEZAS Y-MONOTONAS de los ciclos de cada cara
    copy_faces.remove( [i for i in copy_faces if i.name == "f2"][0] )
    #vamos a probar cara por cara y arreglar el algoritmo
    # carai = copy_faces[1]
    # ciclo_actual = carai.ciclo
    # list_vertex_carai = [i.origin for i in ciclo_actual]
    # print_vertex(list_vertex_carai)
    # list_semiedges, list_faces = triangulate(list_semiedges,list_vertex_carai,list_faces,carai)
    
    
    for i in copy_faces:#todas son caras exteriores
        #if len(i.ciclo) == 3:
        #    continue #pues ya es un triangulo
        ciclo_actual = i.ciclo
        list_vertex_carai = [i.origin for i in ciclo_actual]
        print_vertex(list_vertex_carai)
        list_semiedges, list_faces = triangulate(list_semiedges,list_vertex_carai,list_faces,i)
    
    print_ciclos(list_faces)
    plotSemiEdges(list_semiedges) #temporal pq se va actualizando en cada iteración pues se agregan diagonales
    plt.show()
    return list_semiedges, list_faces 


###############Helper para hacerlo con todas las piezas y-monotonas###############
#Testing
#Borramos el último elemento pq esta duplicado
#P = [(9, 0.5), (8, 6), (7, -3), (6, 3), (4, -4), (2, -3), (3, 4), (4, 2.5), (5, 12), (7, 8.5), (8, 12), (9.5, 11), (11, 15), (13, 13), (12, 10), (13, 3), (11, 4), (10, -1)]
#hexagono = [(0,0),(-1,2),(-0.5,3.5),(0,4),(0.25,2.5),(1,1)]

#list_semiedges, list_vertex, list_twins_semiedges, list_faces = create_semi_edges(P)
#print("#####################################################################################################SEPARADOR#####################################################################################################")


list_semiedges, list_of_faces = tst.piezas_monotonas,tst.caras_monotonas

list_vertex = [i.origin for i in list_semiedges]

list_vertex = labels_t(list_vertex) #le paso twins pues es la cara interior que es la que no cambia

print_vertex(list_vertex)
print_ciclos(list_of_faces)
list_semiedges, list_faces = triangle_all(list_semiedges,list_of_faces)
print_ciclos(list_faces)
# v11 = [i for i in list_vertex if i.name == "v11"][0]
# v9 = [i for i in list_vertex if i.name == "v9"][0]
# list_semiedges, list_faces = addDiag(list_semiedges,list_faces,[v11,v9])
#plotSemiEdges(list_semiedges) #temporal pq se va actualizando en cada iteración pues se agregan diagonales
#plt.show()
list_semiedges_trianguladas, list_faces_trianguladas = list_semiedges, list_faces 
list_vertex_triangulado = list_vertex
print_semiedges(list_semiedges)
print_faces(list_faces)


print("#################################################################################################################################################################################################################################")
print("FIN TRIANGULAR PIEZAS Y-MONOTONAS")
print("#################################################################################################################################################################################################################################")