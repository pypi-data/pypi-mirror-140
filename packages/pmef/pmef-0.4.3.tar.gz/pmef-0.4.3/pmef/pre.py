from numpy import zeros, array, linspace, delete, append, unique
from numpy import dot, sin, arccos, arctan2
from numpy.linalg import norm

# Funciones para generar Mesh
def LinearMesh(L,Ne,x0=0):
    '''
    Función que retorna nodos y conexiones para elementos finitos en 1D.

    Donde:
            L:      Longitud total de la barra.
            Ne:     Número de elementos a crear.
            x0:     Posición del primer nodo.
    '''
    # Crea arreglo de nodos
    x = linspace(x0,x0+L,Ne+1)
    # Crea arreglo de conexiones
    cnx = zeros((Ne,2),'int')
    cnx[:,0],cnx[:,1] = range(Ne), range(1,Ne+1)
    class Mesh:
        NN = len(x)
        Nodos = x
        NC = len(cnx)
        Conex = cnx
    return Mesh

def founMesh(Lx1,Ly1,Lx2,Ly2,mz1):
    '''
    Función que genera Mesh tipo U para cimentaciones.

    Donde:
            Lx1, Ly1:       Longitud en X y Y de la zona convexa o interior.
            Lx2, Ly2:       Longitud en X y Y de la zona exterior.
    '''
    coor = zeros((10000,2))
    ni, nj = int(2*Lx2/mz1), int(Ly2/mz1)
    k = 0
    for j in range(nj+1):
        for i in range(ni+1):
            if (mz1*i-Lx2)>=-Lx1 and (mz1*i-Lx2)<=Lx1 and -mz1*j>=-Ly1:
                continue
            coor[k] = [mz1*i-Lx2,-mz1*j]
            k = k + 1 
    coor = coor[:k]
    return coor

def load_obj(fileName):
    '''
    Función que lee archivos tipo obj para generar crear arreglos\
    de coordenadas, elementos triangulares y rectangules (tri, quad).
    '''
    vertices, tri, quad = [], [], []
    f = open(fileName)
    for line in f:
        if line[:2] == "v ":
            vertex = line[2:].split()
            vertices.append(vertex)
        elif line[:2] == "f ":
            face = line[2:].split()
            if len(face) == 3:
                tri.append(face)
            else:
                quad.append(face)
    vertices = array(vertices, dtype=float)
    tri = array(tri, dtype=int)
    quad = array(quad, dtype=int)
    f.close()

    return vertices, tri, quad

def GenBrickMesh_3D(L, B, H, lc):
    '''Crea la malla de un elemento rectangular con códigos programados en Python.

    L  : Longitud o base del elemento  en metros
    H  : Altura del elemento en metros
    lc : Número de elementos en la dirección más corta entre L o H.
    '''
    # Lectura del archivo data
    # Define la cantidad de elementos y sus dimensiones en ambas direcciones.

    if min((L, B, H)) == L:
        nx = lc
        ms_x = L / nx
        ny = round(B / ms_x)
        ms_y = B / ny
        nz = round(H / ms_x)
        ms_z = H / nz

    elif min((L, B, H)) == B:
        ny = lc
        ms_y = B / ny
        nx = round(L / ms_y)
        ms_x = L / nx
        nz = round(H / ms_y)
        ms_z = H / nz

    else:
        nz = lc
        ms_z = H / nz
        ny = round(B / ms_z)
        ms_y = B / ny
        nx = round(L / ms_z)
        ms_x = L / nx

    # Imprime los resultados
    print('=' * 16 + 'Mesh' + '=' * 16)
    print("nx = {}, dx = {:.2f}, ny = {}, dy = {:.2f}, nz = {}, dz = {:.2f}".
          format(nx, ms_x, ny, ms_y, nz, ms_z))

    # Define los nodos de la malla
    noNodes = (nx + 1) * (ny + 1) * (nz + 1)
    Nodes = zeros((noNodes, 3),'float64')

    ni = 0
    for i in range(nz + 1):
        for j in range(ny + 1):
            for k in range(nx + 1):
                Nodes[ni] = (ms_x * k, ms_y * j, ms_z * i)
                ni = ni + 1

    # Se establecen las conexiones entre los nodos de la malla para definir los elementos finitos
    noElem = nx * ny * nz
    connect = zeros((noElem, 8), 'int')

    cont = 0
    for k in range(0, nz):
        for i in range(0, ny):
            for j in range(0, nx):

                connect[cont, 0] = j + (i * (nx + 1)) + (k * (nx + 1) * (ny + 1))
                connect[cont, 1] = j + (i * (nx + 1)) + (k * (nx + 1) * (ny + 1)) + 1
                connect[cont, 2] = j + ((i + 1) * (nx + 1)) + ((k) * (nx + 1) * (ny + 1)) + 1
                connect[cont, 3] = j + ((i + 1) * (nx + 1)) + ((k) * (nx + 1) * (ny + 1))
                connect[cont, 4] = j + (i * (nx + 1)) + ((k + 1) * (nx + 1) * (ny + 1))
                connect[cont, 5] = j + (i * (nx + 1)) + ((k + 1) * (nx + 1) * (ny + 1)) + 1
                connect[cont, 6] = j + ((i + 1) * (nx + 1)) + ((k + 1) * (nx + 1) * (ny + 1)) + 1
                connect[cont, 7] = j + ((i + 1) * (nx + 1)) + ((k + 1) * (nx + 1) * (ny + 1))
                cont += 1

    # Se agrega los parámetros calculados al diccionario Data
    class Mesh:
        NN = noNodes
        Nodos = Nodes
        NC = noElem
        Conex = connect

    return Mesh

# Fuciones para crear condiciones de borde
def BC_2Dx(X,dy,x,tipo,gdl,val):
    ''' Función que busca el nodo donde se aplicará las CB, especificando
    una distancia Y y el intervalo en x.

    Input:
            dy:			Ordenada o distancia en y donde se aplicaran CB.
            x:          Intervalo de X donde se aplicaran CB [x1,x2].
            X:          Matriz que contiene las coordenadas de los nodos.
    Output:
            BC_data:    Matriz que define las condiciones de borde (las \
                        columnas corresponden a: Nodo, Tipo de CB, GDL y Valor)
    '''
    NN,k=len(X),0
    BC_data = zeros((10000,4),dtype='float64')
    x1,x2 = x[0],x[1]
    k= 0
    for i in range(NN):
        if abs(X[i,1]-dy)<=10e-6:
            if X[i,0]>=x1 and X[i,0]<=x2:
                for g in gdl:
                    BC_data[k] = [i,tipo,g,val]
                    # print('Applying BC:',i,tipo,g,val)
                    k = k + 1
            else: continue
        else: continue
    BC_data = BC_data[:k]
    n = len(BC_data)
    for i in range(n): # si es CB tipo Neumann distribuye val en los nodos
        if BC_data[i,1]==0: BC_data[i,3] = val/n
    print('Se crearon %i condiciones de Borde.'%n)
    return BC_data

def BC_2Dy(X,dx,y,tipo,gdl,val):
    ''' Función que busca el nodo donde se aplicará las CB, especificando
    una distancia X y el intervalo en y.

    Input:
            dx:			Ordenada o distancia en x donde se aplicaran CB.
            y:          Intervalo de Y donde se aplicaran CB [y1,y2].
            X:          Matriz que contiene las coordenadas de los nodos.
    Output:
            BC_data:    Matriz que define las condiciones de borde (las \
                        columnas corresponden a: Nodo, Tipo de CB, GDL y Valor)
    '''
    NN,k=len(X),0
    BC_data = zeros((10000,4),dtype='float32')
    y1,y2 = y[0],y[1]
    k= 0
    for i in range(NN):
        if abs(X[i,0]-dx)<=10e-6:
            if X[i,1]>=y1 and X[i,1]<=y2:
                for g in gdl:
                    BC_data[k] = [i,tipo,g,val]
                    k = k + 1
            else: continue
        else: continue
    BC_data = BC_data[:k]
    n = len(BC_data)
    for i in range(n): # si es CB tipo Neumann distribuye val en los nodos
        if BC_data[i,1]==0: BC_data[i,3] = val/n
    print('Se crearon %i condiciones de Borde.'%n)
    return BC_data


# Funciones para delaunay triangulation
def circumcenter(tri):
    '''
    Función que encuentra el  circumcentro (xo,yo) y su radio ro \
    dada tres coordenadas.
    '''
    s = zeros(3)
    pts = [2,0,1,2,0]
    for i in range(1,4):
        r1 = tri[pts[i-1]]-tri[pts[i]]
        r2 = tri[pts[i+1]]-tri[pts[i]]
        s[i-1]=sin(2*arccos(dot(r1,r2)/(norm(r1)*norm(r2))))
    xo = dot(tri[:,0],s)/sum(s)
    yo = dot(tri[:,1],s)/sum(s)
    r = sum((tri[2]-[xo,yo])**2)**0.5
    return xo,yo,r

def getPolygon(xyo,elems,xd):
    '''
    Función que genera un poligono uniendo elementos triangulares.

    Donde:
            xyo:        Circumcentro
            elems:      Arreglo relacionados al circumcentro que contiene \
                        la conexión de los elementos a unir.
            xd:         Arreglo que contiene las coordenadas de todos los nodos.  
            pol:        Arreglo que contiene los nodos del polígono generado.  
    '''
    pol = elems[0]
    for e in elems[1:]:
        pol = append(pol,e)
    pol = unique(pol)
    ang = zeros(len(pol))
    for i in range(len(pol)):
        x1,y1 = xd[pol[i]]
        ang[i]=arctan2(y1-xyo[1],x1-xyo[0])
    args = ang.argsort()
    pol = pol[args]
    return append(pol,pol[0])

def updateMesh(xyo,xd,elems,selec):
    '''
    Función que actualiza el Mesh (agrega elementos y nodos).
    '''
    local_elems = elems[selec]
    if len(local_elems)==0: print('*'*20+'No triangle found!'+'*'*20)
    else: pol = getPolygon(xyo,local_elems,xd)
    elems2 =delete(elems, selec, axis=0)
    xd = append(xd,[xyo],axis=0)
    for i in range(len(pol)-1):
        temp = [len(xd)-1,pol[i],pol[i+1]]
        elems2 = append(elems2,[temp],axis=0)
    return xd,elems2

def delaunay(coor):
    '''
    Función que genera un Mesh uniforme basado en la triangulación de Delaunay \
    a partir de coordenadas.
    '''
    print("Triangulación de Delaunay ...")
    maxX,maxY = max(coor[:,0]),max(coor[:,1])
    minX,minY = min(coor[:,0]),min(coor[:,1])

    xi = minX - 0.1*(maxX-minX)
    yi = minY - 0.1*(maxY-minY)
    xf = maxX + 0.1*(maxX-minX)
    yf = maxY + 0.1*(maxY-minY)

    x = array([[xi,yi],[xf,yi],[xf,yf],[xi,yf]])
    cnx = array([[0,1,2],[0,2,3]])

    for i in range(len(coor)):
        # print('node %i: (%8.5f,%8.5f)'%(i,coor[i,0],coor[i,1]))
        ie = 0
        selec =[]
        for e in cnx:
            xe = x[e]
            xo,yo,r = circumcenter(xe)
            d = sum((coor[i]-[xo,yo])**2)**0.5
            if d <= 1.000001*r: 
                selec.append(ie)
                # print('The point %i is inside circle of element %i :D'%(i,ie))
            else:
                pass
                # print('The point %i is out of circle of element %i :('%(i,ie))
            ie += 1
        x,cnx = updateMesh(coor[i],x,cnx,selec)
    x = coor
    selec = []
    for ie in range(len(cnx)):
        for n in cnx[ie]:
            if n<=3:
                selec.append(ie)
                break
    cnx =delete(cnx, selec, axis=0)-4
    print("Terminó la triangulación.")
    return cnx




