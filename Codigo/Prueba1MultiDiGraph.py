import os
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
import re

from LecturasCSV import leer_todas_columnas_csv, leer_columna_csv
from ObtenerRegex import dfa_to_regex
from RPNI import rpni



def inicializarDict():
    """
    Inicializa diccionarios con keys de Act01 a Act24.
    """
    dictAct = {}
    for i in range(1, 25):
        dictAct[f"Act{i:02d}"] = []  # Formato con dos dígitos
    return dictAct

def filtrar_sensores_por_actividad(valores, horas_inicio, horas_fin, act, dictAct):
    """
    Filtra los valores de los sensores según la hora de inicio y final de cada actividad y los almacena en un diccionario.

    :param valores: Tabla csv que contiene los sensores y la hora a la que se activaron.
    :param horas_inicio: Lista con las horas de inicio de las actividades.
    :param horas_fin: Lista con las horas de fin de las actividades.
    :param act: Lista con los nombres de las actividades dadas.
    :return: Diccionario con los valores de los sensores filtrados por actividad.
    """
       
    for i in range(len(horas_inicio)):
        sensores_por_actividad = [] #Lista para almacenar los sensores de cada actividad
        hora_inicio = datetime.strptime(horas_inicio[i], '%Y/%m/%d %H:%M:%S.%f') #Tomamos la hora de inicio de la actividad
        hora_fin = datetime.strptime(horas_fin[i], '%Y/%m/%d %H:%M:%S.%f') #Tomamos la hora de fin de la actividad
        actividad_nombre = act[i] #Tomamos el nombre de la actividad

        
        for j in range(len(valores['TIMESTAMP'])): #Recorremos la tabla de los sensores
            hora_sensor = datetime.strptime(valores['TIMESTAMP'][j], '%Y/%m/%d %H:%M:%S.%f') #Tomamos la hora de activación del sensor
            if hora_inicio <= hora_sensor <= hora_fin:
                sensores_por_actividad.append(valores['OBJECT'][j]) #Si la hora de activacion del sensor está entre la hora de inicio y fin de la actividad, añadimos el sensor a la lista de sensores de la actividad
        sensorActividad = sensores_por_actividad.copy()
        dictAct[actividad_nombre].append(sensorActividad) #Añadimos la lista de sensores de la actividad al diccionario con la key de la actividad
        print("Se ha añadido la actividad: "+actividad_nombre)

def procesar_archivo_csv(ruta_Act, ruta_Sen, dictAct):
    """
    Procesa un archivo CSV según su tipo.

    :param ruta_Act: Ruta completa del archivo de actividades CSV.
    :param ruta_Sen: Ruta completa del archivo de sensores CSV.
    :param dictAct: Diccionario que recogera las listas de sensores que se dan en cada actividad.
    """
     
    # Para los archivos de actividades recogemos las horas de inicio y fin y el nombre de cada actividad
    print(f"Ejecutando acción para tipo A en {ruta_Act}")
    horas_inicio = leer_columna_csv(ruta_Act, 'DATE BEGIN')
    horas_fin = leer_columna_csv(ruta_Act, 'DATE END')
    act = leer_columna_csv(ruta_Act, 'ACTIVITY')
   
    # Para los archivos de sensores recogemos toda la tabla
    print(f"Ejecutando acción para tipo B en {ruta_Sen}")
    valores = leer_todas_columnas_csv(ruta_Sen)

    filtrar_sensores_por_actividad(valores, horas_inicio, horas_fin, act, dictAct)

def recorrer_carpetas(base_path, base_path_aux, dictAct):
    """
    Recorre todas las subcarpetas desde la carpeta base y procesa archivos CSV según su nombre.

    :param base_path: Ruta de la carpeta base.
    :param dictAct: Diccionario que recogera las listas de sensores que se dan en cada actividad.
    """

    # Comprobar si la carpeta base existe
    if not os.path.exists(base_path):
        print(f"Error: La carpeta '{base_path}' no existe.")
        base_path = base_path_aux

        if not os.path.exists(base_path):
            print(f"Error: La carpeta '{base_path}' no existe.")

            return
    
    # Recorrer todas las subcarpetas
    for carpeta_actual, _, archivos in os.walk(base_path):
        print(f"Entrando en carpeta: {carpeta_actual}")

        rutaAct =""
        rutaSen =""

        if not archivos:
            print(f"No se encontraron archivos en {carpeta_actual}")

        for archivo in archivos:
            if archivo.endswith(".csv"):  # Solo considerar archivos CSV
                archivo_lower = archivo.lower()  # Convertir a minúsculas
                ruta_completa = os.path.normpath(os.path.join(carpeta_actual, archivo_lower))
                # print(f"Procesando archivo: {ruta_completa}")
                
                # Filtramos los archivos según su tipo
                if "activity" in archivo:
                    rutaAct = ruta_completa
                elif "sensor" in archivo:
                    rutaSen = ruta_completa
                # else:
                    # print(f"Omitiendo archivo: {ruta_completa}")
        if rutaAct and rutaSen:
            print(f"\nArchivos emparejados:\n - Activity: {rutaAct}\n - Sensor: {rutaSen}\n")
            procesar_archivo_csv(rutaAct, rutaSen, dictAct)

def construir_automata(secuencias):
    """
    Construye un autómata a partir de una lista de secuencias de actividades (MultiDiGraph).

    :param secuencias: Lista de secuencias de actividades.
    :return: Un MultiDiGraph con nodos etiquetados como "Inicial", "Intermedio" o "Final".
    """

    G = nx.MultiDiGraph()  # Inicializar grafo dirigido

    for secuencia in secuencias:  # Recorrer cada secuencia
        for i in range(len(secuencia)):
            origen = secuencia[i]
            destino = secuencia[i + 1] if i < len(secuencia) - 1 else None

            # Si la arista existe, aumentar el peso; si no, crearla con peso 1
            if destino:
                if G.has_edge(origen, destino):
                    for key in G[origen][destino]:
                        G[origen][destino][key]['weight'] += 1
                else:
                    G.add_edge(origen, destino, weight=1)

            # Si el nodo no existe, añadirlo con la etiqueta "Intermedio"
            if origen not in G.nodes:
                G.add_node(origen, label="Intermedio")
            if destino and destino not in G.nodes:
                G.add_node(destino, label="Intermedio")

            # Obtener la etiqueta actual del nodo (si no existe, asignar "Intermedio")
            etiqueta_actual = G.nodes[origen].get('label', "Intermedio")

            # Reglas de prioridad para etiquetas
            if i == 0:
                G.nodes[origen]['label'] = "Inicial"  # Siempre gana "Inicial"
            elif i == len(secuencia) - 1:
                if etiqueta_actual != "Inicial":  # No sobreescribir si ya es "Inicial"
                    G.nodes[origen]['label'] = "Final"

    return G

def calcular_probabilidades(G):
    """
    Calcula las probabilidades de transición de cada arista del grafo.

    :param G: Grafo dirigido.
    """

    for nodo in G.nodes: # Recorrer cada nodo
        total_salidas = sum(G[nodo][vecino][key]['weight'] for vecino in G.successors(nodo) for key in G[nodo][vecino]) # Sumar los pesos de las aristas salientes
        for vecino in G.successors(nodo): # Recorrer cada vecino
            for key in G[nodo][vecino]:
                G[nodo][vecino][key]['label'] = f"{G[nodo][vecino][key]['weight']}/{total_salidas}" # Calcular la probabilidad de transición Arista saliente / Total salidas

def dibujar_automata(G, titulo = ""):
    """
    Dibuja el autómata en un gráfico con un título.

    :param G: Grafo dirigido.
    :param titulo: Título del gráfico.
    """
    pos = nx.spring_layout(G, seed=5, k=0.4)  # Para un layout estable
    labels = {(u, v, k): data['label'] for u, v, k, data in G.edges(data=True, keys=True)}

    # Colores de los nodos según su etiqueta
    node_colors = [
        'green' if G.nodes[node].get('label') in ['Inicial', 'Positivo']
        else 'red' if G.nodes[node].get('label') == 'Final'
        else 'blue' if G.nodes[node].get('label') == 'Negativo'
        else 'lightgray'
        for node in G.nodes
    ]
    plt.figure(figsize=(12, 8))
    plt.title(titulo)
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='black', node_size=2000, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

def generaSecuencias(base_path, base_path_aux, secuenciaMañana, secuenciaTarde, secuenciaNoche):
    """
    Genera las secuencias de actividades y construye los autómatas correspondientes.
    
    :param base_path: Ruta de la carpeta base.
    :param secuenciaMañana: Lista de secuencias de actividades de la mañana.
    :param secuenciaTarde: Lista de secuencias de actividades de la tarde.
    :param secuenciaNoche: Lista de secuencias de actividades de la noche.
    """

    # Comprobar si la carpeta base existe
    if not os.path.exists(base_path):
        print(f"Error: La carpeta '{base_path}' no existe.")
        base_path = base_path_aux

        if not os.path.exists(base_path):
            print(f"Error: La carpeta '{base_path}' no existe.")

            return
    
    # Recorrer todas las subcarpetas
    for carpeta_actual, _, archivos in os.walk(base_path):
        print(f"Entrando en carpeta: {carpeta_actual}")

        rutaAct =""

        if not archivos:
            print(f"No se encontraron archivos en {carpeta_actual}")

        for archivo in archivos:
            if archivo.endswith(".csv"): # Solo considerar archivos CSV
                archivo_lower = archivo.lower() # Convertir a minúsculas
                ruta_completa = os.path.normpath(os.path.join(carpeta_actual, archivo_lower)) # Convertir a minúsculas
                # print(f"Procesando archivo: {ruta_completa}")
                
                # Comprobación del nombre del archivo
                if "activity" in archivo:
                    rutaAct = ruta_completa
                else:
                    print(f"Omitiendo archivo: {ruta_completa}")

        if rutaAct: # Si se ha encontrado un archivo de actividades
            print(f"\nArchivos emparejados:\n - Activity: {rutaAct}\n")
            procesar_secuencias(rutaAct, secuenciaMañana, secuenciaTarde, secuenciaNoche)

      
    #Al final de todos los archivos se construyen los autómatas de secuencias de mañana, tarde y noche
    grafoMañana = construir_automata(secuenciaMañana)
    calcular_probabilidades(grafoMañana)
    dibujar_automata(grafoMañana, "Secuencia Mañana")

    grafoTarde = construir_automata(secuenciaTarde)
    calcular_probabilidades(grafoTarde)
    dibujar_automata(grafoTarde, "Secuencia Tarde")

    grafoNoche = construir_automata(secuenciaNoche)
    calcular_probabilidades(grafoNoche)
    dibujar_automata(grafoNoche, "Secuencia Noche")

    return grafoMañana, grafoTarde, grafoNoche

def procesar_secuencias(ruta_Act, secuenciaMañana, secuenciaTarde, secuenciaNoche):
    """
    Procesa un archivo CSV de actividades según su horario.

    :param ruta_Act: Ruta completa del archivo de actividades CSV.
    :param secuenciaMañana: Lista de secuencias de actividades de la mañana.
    :param secuenciaTarde: Lista de secuencias de actividades de la tarde.
    :param secuenciaNoche: Lista de secuencias de actividades de la noche.
    """
    act = leer_columna_csv(ruta_Act, 'ACTIVITY') # Extraer las actividades del archivo
   
    # Filtrar las actividades según su horario y se añaden a la secuencia correspondiente
    if "b-activity" in ruta_Act:
        secuenciaTarde.append(act)
    elif "c-activity" in ruta_Act:
        secuenciaNoche.append(act)
    else:
        secuenciaMañana.append(act)

def construir_automata_actividades(secuencias):
    """
    Funcion que construye un autómata a partir de una lista de secuencias de actividades con sensores.(MultiDiGraph)
    También se añade el sensor como etiqueta de la arista.
    El nombre de los nodos es una lista de sensores dados separados por espacios.

    :param secuencias: Lista de secuencias de actividades con sensores.
    """
    G = nx.MultiDiGraph()
    
    # Recorrer cada secuencia
    for secuencia in secuencias:
        historial = "[]"  # Nodo inicial vacío
        if historial not in G: # Si no existe el nodo, lo añadimos
            G.add_node(historial)
            G.nodes[historial]['label'] = "Negativo"
        
        # Recorrer cada sensor de la secuencia
        for i, sensor in enumerate(secuencia):
            nuevo_nodo = f"{historial[:-1]} {sensor}]" if historial != "[]" else f"[{sensor}]" # Añadir sensor al historial (historial[:-1] quita el ] final)

            # Si no existe el nodo, lo añadimos
            if not G.has_node(nuevo_nodo):
                G.add_node(nuevo_nodo)
                G.nodes[nuevo_nodo]['label'] = "Negativo"
            
            # Si ya existe la arista, apuntamos 1 al peso, si no, la creamos con peso 1
            if G.has_edge(historial, nuevo_nodo):
                for key in G[historial][nuevo_nodo]:
                    G[historial][nuevo_nodo][key]['weight'] += 1
            else:
                G.add_edge(historial, nuevo_nodo, weight=1, label=sensor)  # Guardar sensor como etiqueta
            
            # Actualizamos el historial
            historial = nuevo_nodo

        G.nodes[historial]['label'] = "Positivo"
    
    return G

def  es_sensor_SM(sensor):
    """
    Verifica si un sensor es del tipo 'SM'.
    
    :param sensor: Nombre del sensor.
    :return: True si el sensor empieza por 'SM', False en caso contrario.
    """
    return sensor.startswith("SM")

def generaAutomataActividades(dictAct, dictSec):
    """
    Genera un autómata para cada actividad, eliminando los sensores que empiezan por 'SM' si es posible.

    :param dictAct: Diccionario con las listas de sensores de cada actividad.
    :param dictSec: Diccionario que recogerá un automata con los sensores de cada actividad.
    """

    for key, value in dictAct.items():
        print(f"Procesando actividad: {key}")

        # Verificar si todas las listas tienen al menos un sensor que no empieza por "SM"
        existe_sensor_no_sm = all(
            any(not es_sensor_SM(sensor) for sensor in lista) for lista in value
        )

        if existe_sensor_no_sm:
            # Si hay algún sensor distinto de "SM...", eliminamos todos los "SM..."
            sensores_a_eliminar = {sensor for lista in value for sensor in lista if es_sensor_SM(sensor)}

            # Guardamos los sensores eliminados en dictSec
            dictSec[key] = list(sensores_a_eliminar)

            # Eliminamos sensores SM de cada sublista en dictAct
            value2 = []
            for lista in value:
                lista2 = lista.copy()
                lista2[:] = [sensor for sensor in lista2 if sensor not in sensores_a_eliminar]
                value2.append(lista2)
        else:
            # Si todos los sensores son "SM...", no eliminamos nada
            value2 = value.copy()
            
        dictSec[key] = construir_automata_actividades(value2)  # No se eliminó ningún sensor





def pintar_multigrafo(grafoNuevo):
    plt.figure(figsize=(6, 4))
    pos = nx.spring_layout(grafoNuevo)  # Posiciones de los nodos
    # Colores de los nodos según su etiqueta
    node_colors = [
        'green' if grafoNuevo.nodes[node].get('label') in ['Inicial', 'Positivo']
        else 'red' if grafoNuevo.nodes[node].get('label') == 'Final'
        else 'lightgray'
        for node in grafoNuevo.nodes
    ]
    nx.draw(grafoNuevo, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=2000, font_size=12)

    # Dibujar los labels de las aristas
    edge_labels = {(u, v, k): d["label"] for u, v, k, d in grafoNuevo.edges(keys=True, data=True) if "label" in d}
    nx.draw_networkx_edge_labels(grafoNuevo, pos, edge_labels=edge_labels, font_color='red')

    plt.show()

def obtenerActividadesPosibles(grafo_A_Mirar, actividadAnterior, actividadesAnteriores):
    """
    En funcion del nombre del documento(mañana, tarde o noche) se obtienen las actividades posibles en funcion de la actividad anterior.
    :param nombreDocumento: Nombre del documento CSV.
    :param actividadAnterior: Actividad anterior.
    
    :return: Lista de actividades posibles.
    """

    actividadesPosibles = []
    PosiblesEnCualquierMomento = ["Act11", "Act09", "Act14", "Act18", "Act12"]
    if actividadAnterior in PosiblesEnCualquierMomento and not any(actividad in grafo_A_Mirar.nodes() for actividad in PosiblesEnCualquierMomento):
        return actividadesAnteriores
    
    if actividadAnterior == "":
        print("A")
        # Cojo los nodos iniciales del grafo
        nodos_iniciales = [nodo for nodo in grafo_A_Mirar.nodes() if grafo_A_Mirar.nodes[nodo].get('label') == 'Inicial']   
        actividadesPosibles = nodos_iniciales
    else:    
        destinos_con_peso = [
            (destino, data['weight'])
            for _, destino, key, data in grafo_A_Mirar.out_edges(actividadAnterior, keys=True, data=True)
            if 'weight' in data
        ]

        # Ordenar por peso
        destinos_ordenados = [destino for destino, peso in sorted(destinos_con_peso, key=lambda x: x[1])]
        actividadesPosibles = destinos_ordenados

    #Por último, añadimos distintas actividades a mano que podrian ocurrir en cualquier momento
    print("Actividades Posibles sin extras: ", actividadesPosibles)
    actividadesPosibles.extend(PosiblesEnCualquierMomento)

    print("Actividades posibles: ", actividadesPosibles)

    # Filtrar actividades posibles para que no se repitan
    actividadesPosibles = list(dict.fromkeys(actividadesPosibles))

    print("Actividades posibles Sin Duplicar: ", actividadesPosibles)

    return actividadesPosibles


def obtenerActividadesDocumento(direccionDocumento):
    """
    Lee un documento de sensores extrayendo tuplas Sensor, Tiempo y luego procesa los sensores sobre los regex de las actividades posibles en funcion de los grafos de cada tiempo.
    :param nombre_documento: Nombre del documento CSV.
    :return: Lista de (actividades, tiempo-inicio, tiempo-fin).
    """
    
    sensores = leer_columna_csv(direccionDocumento, 'OBJECT')
    tiempos = leer_columna_csv(direccionDocumento, 'TIMESTAMP')

    if "a-sensors" in direccionDocumento:
        print("A")
        grafo_A_Mirar = grafoMañana
    elif "b-sensors" in direccionDocumento:
        print("B")
        grafo_A_Mirar = grafoTarde
    else:
        print("C")
        grafo_A_Mirar = grafoNoche

    actividades = []
    regexSensor = ""
    regexSensorNoSM = ""
    tiempoInicial = None
    tiempoInicialNoSM = None
    tiempoFinal = None
    actividadAnterior = ""
    actividadesAnteriores = []
    for i in range(len(sensores)):
        regexSensor = regexSensor + sensores[i]
        if not es_sensor_SM(sensores[i]):
            regexSensorNoSM = regexSensorNoSM + sensores[i]
            if tiempoInicialNoSM is None:
                tiempoInicialNoSM = tiempos[i]
        if tiempoInicial is None:
            tiempoInicial = tiempos[i]
            actividadesPosibles = obtenerActividadesPosibles(grafo_A_Mirar, actividadAnterior, actividadesAnteriores)
        
        tiempoFinal = tiempos[i]
        print(regexSensor, regexSensorNoSM, actividadesPosibles)
        for actividad in actividadesPosibles:
            print(actividad)
            if re.match(dictRegex[actividad], regexSensor):
                print("HA MATCHEADO CON SM")
                print(actividad, tiempoInicialNoSM, tiempoFinal)
                actividades.append((actividad, tiempoInicial, tiempoFinal))
                actividadAnterior = actividad

                actividadesAnteriores = actividadesPosibles.copy()
                tiempoInicial = None
                tiempoInicialNoSM = None
                tiempoFinal = None
                regexSensor = ""
                regexSensorNoSM = ""
                break

            if re.match(dictRegex[actividad], regexSensorNoSM):
                print("HA MATCHEADO SIN SM")
                print(actividad, tiempoInicialNoSM, tiempoFinal)
                actividades.append((actividad, tiempoInicialNoSM, tiempoFinal))
                actividadAnterior = actividad

                actividadesAnteriores = actividadesPosibles.copy()
                tiempoInicial = None
                tiempoInicialNoSM = None
                tiempoFinal = None
                regexSensor = ""
                regexSensorNoSM = ""
                break
            
def procesar_tests(base_path, base_path_aux):

    # Comprobar si la carpeta base existe
    if not os.path.exists(base_path):
        print(f"Error: La carpeta '{base_path}' no existe.")
        base_path = base_path_aux

        if not os.path.exists(base_path):
            print(f"Error: La carpeta '{base_path}' no existe.")
            return
    
    # Recorrer todas las subcarpetas
    for carpeta_actual, _, archivos in os.walk(base_path):
        print(f"Entrando en carpeta: {carpeta_actual}")

        rutaSen =""

        if not archivos:
            print(f"No se encontraron archivos en {carpeta_actual}")

        for archivo in archivos:
            if archivo.endswith(".csv"):  # Solo considerar archivos CSV
                archivo_lower = archivo.lower()  # Convertir a minúsculas
                ruta_completa = os.path.normpath(os.path.join(carpeta_actual, archivo_lower))
                # print(f"Procesando archivo: {ruta_completa}")
                
                # Filtramos los archivos según su tipo
                if "sensor" in archivo:
                    rutaSen = ruta_completa
                # else:
                    # print(f"Omitiendo archivo: {ruta_completa}")
        if rutaSen:
            print(f"Sensor: {rutaSen}\n")
            actividades = obtenerActividadesDocumento(rutaSen)
            for (actividad, tiempo_inicio, tiempo_fin) in actividades:
                print(f"Actividad: {actividad}, Tiempo de inicio: {tiempo_inicio}, Tiempo de fin: {tiempo_fin}")
            print("\n")

    



carpeta_base = r"C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"
carpeta_base_aux = r"C:/Users/jesme/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"
carpeta_base_test = r"C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Test/"
carpeta_base_test_aux = r"C:/Users/jesme/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Test/"


dictAct = inicializarDict()
dictSec = inicializarDict()
dictGrafoMin = inicializarDict()
dictRegex = inicializarDict()

recorrer_carpetas(carpeta_base, carpeta_base_aux, dictAct)
for key, value in dictAct.items():
    print(f"{key}: {len(value)}")

secuenciaMañana, secuenciaTarde, secuenciaNoche = [], [], []

grafoMañana, grafoTarde, grafoNoche = generaSecuencias(carpeta_base, carpeta_base_aux, secuenciaMañana, secuenciaTarde, secuenciaNoche)
   
generaAutomataActividades(dictAct, dictSec)

# for key in dictSec.keys():
#     dibujar_automata(dictSec[key], key)


for key, value in dictSec.items():
    
    # print("===================")
    # print(f"Automata de {key}")
    # dibujar_automata(value, key)
    # print("\n")
    # print("===================")
    
    dictGrafoMin[key] = rpni(value, key)
    # print("\n")
    # print("===================")
    # print(f"Automata minimizado de {key}")
    
    # # print("\n")
    # print(f"Expresion regular de {key}")
    nodosFinales = [nodo for nodo in dictGrafoMin[key].nodes() if dictGrafoMin[key].nodes[nodo]['label'] == "Positivo"]
    nodoInicial = '[]'
    regex = dfa_to_regex(dictGrafoMin[key], nodoInicial, nodosFinales)
    # print(regex)
    # print(dictGrafoMin[key].nodes())
    # print(dictGrafoMin[key].edges(data=True))
    # dibujar_automata(dictGrafoMin[key], key + " minimizado")
    dictRegex[key] = regex
    # print("\n")
    print("===================")
print(dictRegex["Act24"])
procesar_tests(carpeta_base, carpeta_base_aux)


    #re.griddy
    #ocw teoria lenguajes formales tirnauca
    #metodologia mas teorico
            
