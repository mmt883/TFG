import os
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from LecturasCSV import leer_todas_columnas_csv, leer_columna_csv



# Ejemplo de uso:

#Objetivo leer datos de csv y ir dividiendo segun hora inicial y final acorde a actividades
#Tenemos varios csv con datos: Date begin, Date End, Activity, Habitant
#Y otros con: TimeStamp, Object, State, Habitant

# OBJETIVO A SIGUIENTE:
# ALMACENAR TODOS LOS SENSORES DE UNA ACTIVIDAD, filtrando segun hora inicial y final y
# Busco en valores los sensores que se dieron en una actividad, filtrando por hora inicial y final,
# y almaceno en el diccionario con key = Act1, Act2, Act3, etc


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


def recorrer_carpetas(base_path, dictAct):
    """
    Recorre todas las subcarpetas desde la carpeta base y procesa archivos CSV según su nombre.

    :param base_path: Ruta de la carpeta base.
    :param dictAct: Diccionario que recogera las listas de sensores que se dan en cada actividad.
    """

    # Comprobar si la carpeta base existe
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
    Función que construye un autómata a partir de una lista de secuencias de actividades.(DiGraph)

    :param secuencias: Lista de secuencias de actividades.
    """
    
    G = nx.DiGraph() # Inicializar grafo dirigido
    
    for secuencia in secuencias: # Recorrer cada secuencia

        for i in range(len(secuencia) - 1): # Recorro cada actividad de la secuencia, uniendo cada actividad con la siguiente
            origen = secuencia[i]
            destino = secuencia[i + 1]

            # Si ya existe la arista, apunto 1 al peso, si no, la creo con peso 1
            if G.has_edge(origen, destino):
                G[origen][destino]['weight'] += 1
            else:
                G.add_edge(origen, destino, weight=1)
    
    return G

def calcular_probabilidades(G):
    """
    Calcula las probabilidades de transición de cada arista del grafo.

    :param G: Grafo dirigido.
    """

    for nodo in G.nodes: # Recorrer cada nodo
        total_salidas = sum(G[nodo][vecino]['weight'] for vecino in G.successors(nodo)) # Sumar los pesos de las aristas salientes
        for vecino in G.successors(nodo): # Recorrer cada vecino
            G[nodo][vecino]['label'] = f"{G[nodo][vecino]['weight']}/{total_salidas}" # Calcular la probabilidad de transición Arista saliente / Total salidas

def dibujar_automata(G, titulo = ""):
    """
    Dibuja el autómata en un gráfico con un título.

    :param G: Grafo dirigido.
    :param titulo: Título del gráfico.
    """
    pos = nx.spring_layout(G, seed=5, k=0.4)  # Para un layout estable
    labels = {edge: G[edge[0]][edge[1]]['label'] for edge in G.edges}
    plt.figure(figsize=(12, 8))
    plt.title(titulo)
    nx.draw(G, pos, with_labels=True, node_color='lightgray', edge_color='black', node_size=2000, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

def generaSecuencias(base_path, secuenciaMañana, secuenciaTarde, secuenciaNoche):
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
    Funcion que construye un autómata a partir de una lista de secuencias de actividades con sensores.(DiGraph)
    También se añade el sensor como etiqueta de la arista.
    El nombre de los nodos es una lista de sensores dados separados por espacios.

    :param secuencias: Lista de secuencias de actividades con sensores.
    """
    G = nx.DiGraph()
    
    # Recorrer cada secuencia
    for secuencia in secuencias:
        historial = "[]"  # Nodo inicial vacío
        if historial not in G: # Si no existe el nodo, lo añadimos
            G.add_node(historial)
        
        # Recorrer cada sensor de la secuencia
        for sensor in secuencia:
            nuevo_nodo = f"{historial[:-1]} {sensor}]" if historial != "[]" else f"[{sensor}]" # Añadir sensor al historial (historial[:-1] quita el ] final)

            # Si no existe el nodo, lo añadimos
            if not G.has_node(nuevo_nodo):
                G.add_node(nuevo_nodo)
            
            # Si ya existe la arista, apuntamos 1 al peso, si no, la creamos con peso 1
            if G.has_edge(historial, nuevo_nodo):
                G[historial][nuevo_nodo]['weight'] += 1
            else:
                G.add_edge(historial, nuevo_nodo, weight=1, label=sensor)  # Guardar sensor como etiqueta
            
            # Actualizamos el historial
            historial = nuevo_nodo
    
    return G

def generaAutomataActividades(dictAct, dictSec):
    for key, value in dictAct.items():
        print(f"Actividad: {key}")
        dictSec[key] = construir_automata_actividades(value)


# carpeta_base = r"C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"
carpeta_base = r"C:/Users/jesme/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"

dictAct = inicializarDict()
dictSec = inicializarDict()

recorrer_carpetas(carpeta_base, dictAct)
for key, value in dictAct.items():
    print(f"{key}: {len(value)}")

secuenciaMañana, secuenciaTarde, secuenciaNoche = [], [], []

grafoMañana, grafoTarde, grafoNoche = generaSecuencias(carpeta_base, secuenciaMañana, secuenciaTarde, secuenciaNoche)
   
generaAutomataActividades(dictAct, dictSec)
for key in dictSec.keys():
    dibujar_automata(dictSec[key], key)
