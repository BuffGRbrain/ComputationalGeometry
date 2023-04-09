import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import copy as cp

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

    def add2plot(self): #Adding a segment to the current plot, using its start/end points and label if any
        plt.plot([self.origin.coordinate[0], self.next.origin.coordinate[0]], [self.origin.coordinate[1], self.next.origin.coordinate[1]], '-', label=self.name)

def plotSemiEdges(list_of_semiedges): #Helper to plot either Edges or SemiEdges
    for i in list_of_semiedges:
        i.add2plot()


class Cara(object):
    def __init__(self, name=None, interior_frontier=None, exterior_frontier=None, ciclo=None):
        self.name = name
        self.interior_frontier = interior_frontier  
        self.exterior_frontier = exterior_frontier
        self.ciclo = ciclo


##############################################PRINTING FUNCTIONS##############################################

def print_incident_faces(list_semiedges):
    list_of_faces = []

    for i in list_semiedges:
        if i.cara_incidente not in list_of_faces:
            list_of_faces.append(i.cara_incidente)

    caras_df = pd.DataFrame({'name': [f.name for f in list_of_faces],'interior_frontier': [f.interior_frontier.name if f.interior_frontier!=None else None for f in list_of_faces ],
                            'exterior_frontier': [f.exterior_frontier.name  if f.exterior_frontier!=None else None for f in list_of_faces ]})
    print("######################################Separador de caras######################################")
    print('Caras Incidentes:\n', caras_df)
    print("######################################Separador de caras######################################")
    return None

def print_faces(list_faces):
    faces_df = pd.DataFrame({'name': [f.name for f in list_faces],'interior_frontier': [f.interior_frontier.name if f.interior_frontier!=None else None for f in list_faces ],
                            'exterior_frontier': [f.exterior_frontier.name  if f.exterior_frontier!=None else None for f in list_faces ]})
    print('Caras:\n', faces_df)
    return None

def print_semiedges(list_of_semi_edges):
    semi_edges_df = pd.DataFrame({'name': [se.name for se in list_of_semi_edges],
                                'origin': [se.origin for se in list_of_semi_edges],
                                'cara_incidente': [se.cara_incidente.name for se in list_of_semi_edges],
                                'previous': [se.previous.name for se in list_of_semi_edges],
                                'next': [se.next.name for se in list_of_semi_edges],
                                'twin': [se.twin.name for se in list_of_semi_edges],
                                'helper': [se.helper.name if se.helper!=None else None for se in list_of_semi_edges],
                                'label': [se.label if se.label!=None else None for se in list_of_semi_edges]
                                })
    print('Semi-Edges:\n', semi_edges_df)
    return None
def print_vertex(list_of_vertex):
    vertices_df = pd.DataFrame({'name': [v.name for v in list_of_vertex],
                            'coordinate': [v.coordinate for v in list_of_vertex],
                            'edge_incidente': [v.edge_incidente.name for v in list_of_vertex],
                            'typee': [v.typee for v in list_of_vertex],
                            'label': [v.label if v.label!=None else None for v in list_of_vertex]})
    print('Vertices:\n', vertices_df)
    return None

def print_ciclos(list_faces):
    for i in list_faces:
        if i.name != "f2":
            b = i.ciclo #lista de semiedges
            print(i.name,[j.name for j in b]) 

##############################################CREATION FUNCTIONS##############################################





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


def check_SE(list_of_semiedges, diag):
    for i in list_of_semiedges:
        if i.origin.coordinate == diag[0].coordinate or i.origin.coordinate == diag[1].coordinate: #Uno de los dos vertex es el origen ahora vamos a ver si el otro es el destino
            if i.next.origin.coordinate == diag[0].coordinate or i.next.origin.coordinate == diag[1].coordinate:#entonces uno es destino y otro es origen
                return True #Nos dice que ya esta en la lista
    return False #Nos dice que no esta en la lista

#Function to add diagonal to the polygon
#Input: list of vertex, list of semiedges, list of faces, representing a simple polygon
#Output: updated: list of semiedges, list of faces and list of vertex
def addDiag(list_of_semiedges,list_faces,diag):
    print("Diagonal a agregar: ", diag[0].name, diag[1].name)
    if check_SE(list_of_semiedges, diag):
        print("--"*50)
        print("The diagonal is already in the polygon")
        print("--"*50)
        return list_of_semiedges, list_faces
    print("#"*50, "Before adding the diagonal", "#"*50)
    print_semiedges(list_of_semiedges)
    #diag is a list of 2 vertex, va y vb como el ejemplo de clase
    va = diag[0]
    vb = diag[1] #since they are vertex we can use the coordinate attribute pues los nombres son diferentes
    #TODO: Para escoger ea y eb tiene como req que su twin tenga cara incidente f2 que es la de afuera
    print("Faces: ",[i.name for i in list_faces])

    ea = None
    eb = None
    for i in list_of_semiedges:
        if (i.origin.coordinate == va.coordinate and i.cara_incidente.interior_frontier == None):
            ea = i
            eb = None
            for j in list_of_semiedges:
                if j != i:
                    if (j.origin.coordinate == vb.coordinate and j.cara_incidente.interior_frontier == None and i.cara_incidente == j.cara_incidente ):
                        eb = j
                        break
            if eb is not None:
                break


    if eb is None:
        print("#"*50)
        print("NO SEA IMBECIL DEBERIA EXISTIR")
        print_ciclos(list_faces)
        print("#"*50)

    aux_list = [ea,eb]
    print("################IMPRIMIENDO EA Y EB####################")
    print_semiedges(aux_list)
    print("#############################################")
    #ea = [i for i in list_of_semiedges if i.origin.coordinate == va.coordinate and i.twin.cara_incidente.name =="f2"][0] 
    #eb = [i for i in list_of_semiedges if i.origin.coordinate == vb.coordinate and i.twin.cara_incidente.name =='f2' and ea.cara_incidente == i.cara_incidente][0]
    #encontrando el k para poner a cada nuevo semiedge, el cual no debe existir previamente
    #por formato el nombre es ek1 o ek2 siendo k el numero del vertice origen
    ks = [int(i.name[1:-1]) for i in list_of_semiedges] #lista de ks
    k = max(ks)+1 #Al ser el máximo se que el siguiente no existe entonces puedo usarlo

    print("#############################################")
    print(k)
    print("#############################################")


    #ea.origin en vez de va pues la diferencia es en el atributo name y quiero mantener el mismo
    ek1 = SemiEdge(name = f"e{k}1" ,origin=ea.origin, cara_incidente=None, twin=None, next=eb, previous=None)
    ek2 = SemiEdge(name = f"e{k}2",origin=eb.origin, cara_incidente=None, twin=ek1, next=ea, previous=None)
    ek1.twin = ek2
    #Actualizando los datos de los semiedges

    ea.previous.next = ek1
    eb.previous.next = ek2

    ek1.previous = ea.previous
    ek2.previous = eb.previous
    #Los nexts los puse en la creacion de los semiedges arriba
    eb.previous = ek1
    ea.previous = ek2
    print(f"{ea.name} ea actual")
    #Actualizando los datos de las caras

    ek1prev = ek1.previous
    ek2prev = ek2.previous
    print(f"{ek1prev.name} ek1prev")
    print(f"{ek2prev.name} ek2prev")
    print([i.name for i in list_of_semiedges])
    list_of_semiedges.remove(ek1prev)
    list_of_semiedges.remove(ek2prev)
    ek1prev.next = ek1
    ek2prev.next = ek2
    list_of_semiedges.append(ek1prev)
    list_of_semiedges.append(ek2prev)

    #primero encontramos el ciclo correspondiente a cada cara
    #para ello usamos el atributo cara_incidente de los semiedges
    cara_incidente_ea = ea.cara_incidente # la misma que eb pues por planteamiento son la misma cara
    print(f"{cara_incidente_ea.name} cara a borrar")
    print([i.name for i in list_faces])
    list_faces.remove([i for i in list_faces if i.name == cara_incidente_ea.name][0] )
    #list_faces.remove(cara_incidente_ea) #removemos la cara que se va a dividir
    #creamos las nuevas caras
    cara1 = Cara(name = f"f{k}1", exterior_frontier = ek1)
    cara2 = Cara(name = f"f{k}2", exterior_frontier = ek2) #usamos el k para el nombre de la cara pues este siempre será diferente

    list_of_semiedges_cara1 = []
    list_of_semiedges_cara2 = []
    #creamos los ciclos de cada cara TODO: aqui esta el error, pues no esta actualizandolos todos

    #Antes de meterme aquí quiero revisar que el next asignado si sea el correcto
    print("ek1",ek1.name, ek1.origin.name, ek1.next.name,ek1.next.next.name,ek1.next.next.next.name,ek1.previous.name)
    print("ek2",ek2.name, ek2.origin.name, ek2.next.name,ek2.next.next.name,ek2.next.next.next.name,ek2.previous.name)
    actual = ek1.next
    list_of_semiedges_cara1.append(ek1)
    while actual != ek1:#cuando se salga del if se encontrará con ek1 entonces ese es el primer ciclo
        list_of_semiedges_cara1.append(actual)
        print("SemiEdge corresp a cara 1 ",actual.name)
        actual = actual.next
    actual = ek2.next #reiniciamos el ciclo, para pararnos en el otro semiedge
    list_of_semiedges_cara2.append(ek2)
    while actual != ek2:#cuando se salga del if se encontrará con ek1 entonces ese es el primer ciclo
        print("SemiEdge corresp a cara 2 ",actual.name)
        list_of_semiedges_cara2.append(actual)
        actual = actual.next
    
    cara1.ciclo = list_of_semiedges_cara1
    cara2.ciclo = list_of_semiedges_cara2
    list_faces.append(cara1)
    list_faces.append(cara2)
    print([i.name for i in list_faces])
    for i in list_of_semiedges_cara1:
        print(f"posición {list_of_semiedges_cara1.index(i)}, {i.name} " )
        #tras actualizar los datos de los semiedges, los reemplazamos en la lista de semiedges
        if i in list_of_semiedges:
            print(f"{i.name} semiedge actualizado")
            list_of_semiedges.remove(i)
            i.cara_incidente = cara1 #actualizamos la cara incidente antes de agregarlo a la lista
            list_of_semiedges.append(i)
        else: #estamos en un ek
            i.cara_incidente = cara1
            list_of_semiedges.append(i)
    for i in list_of_semiedges_cara2:
        i.cara_incidente = cara2
        #tras actualizar los datos de los semiedges, los reemplazamos en la lista de semiedges
        if i in list_of_semiedges:#Si esta lo actualizamos
            print(f"{i.name} semiedge actualizado")
            list_of_semiedges.remove(i)
            list_of_semiedges.append(i)
        else:
            list_of_semiedges.append(i)
    #AHORA QUE SE CREO UNA NUEVA CARA, DEBEMOS REVISAR LOS CICLOS DE TODAS LAS DEMAS PARA QUE SIGAN SIENDO VALIDOS
    #TODO PASAR LISTA DE CARAS A FUNCION
    list_of_semiedges,list_faces = update_cycles(list_of_semiedges,list_faces) #estas caras ya estan modificadas por lo que no toca revisarlas

    print("#"*50, "After adding the diagonal", "#"*50)
    print_semiedges(list_of_semiedges)

    return list_of_semiedges, list_faces #ya esta modificado en la funcion


def update_cycles(list_of_semiedges,list_faces):
    for i in list_faces:
        print(i.name)
    copia = cp.deepcopy(list_faces)
    #cara11 = [i for i in copia if i.name == cara1.name][0]
    #cara22 = [i for i in copia if i.name == cara2.name][0]
    caraint = [i for i in copia if i.name == "f2"][0]
    #copia.remove(cara11)
    #copia.remove(cara22)
    copia.remove( caraint )
    for i in copia:
        print(f"Revisando cara {i.name}")
        #primero encontramos el ciclo correspondiente a cada cara
        #para ello usamos el atributo cara_incidente de los semiedges
        actual_cicle = []
        edge_carai = i.exterior_frontier
        #buscamos edge_carai en la lista de semiedges
        edge_carai_lista = [j for j in list_of_semiedges if j.name == edge_carai.name][0]
        actual_cicle.append(edge_carai_lista) #CICLOS SE HACEN CON LOS YA MODIFICADOS O NOS DA LA DEPRE HACK
        actual = edge_carai_lista.next #reiniciamos el ciclo, para pararnos en el otro semiedge
        while actual != edge_carai_lista:#cuando se salga del if se encontrará con ek1 entonces ese es el primer ciclo
            print("SemiEdge corresp a cara ",i.name,actual.name)
            actual_cicle.append(actual)
            actual = actual.next
        carai_update = [j for j in list_faces if j.name == i.name][0] #LA CARA A ACTUALIZAR
        list_faces.remove(carai_update)#removemos la cara que se va a actualizar
        carai_update.ciclo = actual_cicle #Actualizamos el ciclo de la cara i pues es la de list_faces
        #Tras actualizar lo metemos en list_faces
        list_faces.append(carai_update)
    
    print("###########################################################################################")  
    print("##############################printeando ciclo caras#######################################")  
    print_ciclos(list_faces)
    print("###########################################################################################")  
    return list_of_semiedges,list_faces

'''
#Testing
#Borramos el último elemento pq esta duplicado
hexagono = [(0,0),(-1,2),(-0.5,3.5),(0,4),(0.25,2.5),(1,1)]
list_of_semi_edges, list_of_vertex, list_of_twins_semi_edges, list_of_faces = create_semi_edges(hexagono)
print("Antes de agregar diago")
print_vertex(list_of_vertex)
print_semiedges(list_of_semi_edges)
print_semiedges(list_of_twins_semi_edges)

#list_of_semi_edges, list_faces = triangulate(list_of_semi_edges,list_of_twins_semi_edges,list_of_vertex,list_of_faces)
diag = [list_of_vertex[1],list_of_vertex[5]]
list_of_semi_edges, list_of_faces = addDiag(list_of_semi_edges,list_of_faces,diag)


#vamos a probar agregando más diagonales para ver en donde se esta rompiendo y arreglarlo

diag = [list_of_vertex[1],list_of_vertex[5]]
list_of_semi_edges, list_of_faces = addDiag(list_of_semi_edges,list_of_faces,diag)

#HACK TODO HACK se rompio accidentalmente al agregar una diagonal ya existente!!!!!!!!!!!!!!
diag = [list_of_vertex[4],list_of_vertex[1]]
list_of_semi_edges, list_of_faces = addDiag(list_of_semi_edges,list_of_faces,diag)

diag = [list_of_vertex[1],list_of_vertex[3]]
list_of_semi_edges, list_of_faces = addDiag(list_of_semi_edges,list_of_faces,diag)

diag = [list_of_vertex[1],list_of_vertex[2]]
list_of_semi_edges, list_of_faces = addDiag(list_of_semi_edges,list_of_faces,diag)

print("Despues de agregar diago")
print_vertex(list_of_vertex)
print_semiedges(list_of_semi_edges)
print_semiedges(list_of_twins_semi_edges)
print_faces(list_of_faces)

print_incident_faces(list_of_semi_edges)

plotSemiEdges(list_of_semi_edges)
plt.show()
print([i.name for i in list_of_faces])
for i in list_of_faces:
    if i.name != "f2":
        b = i.ciclo #lista de semiedges
        print(i.name,[j.name for j in b]) 

print("#################################################################################################################################################################################################################################")
print("FIN DE DIAGONAL")
print("#################################################################################################################################################################################################################################")

'''