import os
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from LecturasCSV import leer_todas_columnas_csv, subdividir_datos, leer_columna_csv



# Ejemplo de uso:

#Objetivo leer datos de csv y ir dividiendo segun hora inicial y final acorde a actividades
#Tenemos varios csv con datos: Date begin, Date End, Activity, Habitant
#Y otros con: TimeStamp, Object, State, Habitant

# OBJETIVO A SIGUIENTE:
# ALMACENAR TODOS LOS SENSORES DE UNA ACTIVIDAD, filtrando segun hora inicial y final y
# Busco en valores los sensores que se dieron en una actividad, filtrando por hora inicial y final,
# y almaceno en el diccionario con key = Act1, Act2, Act3, etc

def inicializarDict():
    dictAct = {}
    for i in range(1, 25):
        dictAct[f"Act{i:02d}"] = []  # Formato con dos dígitos
    return dictAct

dictAct = inicializarDict()
dictSec = inicializarDict()



def filtrar_sensores_por_actividad(valores, horas_inicio, horas_fin, act, dictAct):
    """
    Filtra los valores de los sensores según la hora de inicio y final de cada actividad y los almacena en un diccionario.

    :param valores: Diccionario con los datos de los sensores.
    :param horas_inicio: Diccionario con las horas de inicio de las actividades.
    :param horas_fin: Diccionario con las horas de finalización de las actividades.
    :param act: Diccionario con las actividades.
    :return: Diccionario con los valores de los sensores filtrados por actividad.
    """
    

    
    for i in range(len(horas_inicio)):
        sensores_por_actividad = []
        hora_inicio = datetime.strptime(horas_inicio[i], '%Y/%m/%d %H:%M:%S.%f')
        hora_fin = datetime.strptime(horas_fin[i], '%Y/%m/%d %H:%M:%S.%f')
        actividad_nombre = act[i]

        clave_tiempo = "TIMESTAMP" if "TIMESTAMP" in valores else "DATE" if "DATE" in valores else None

        if clave_tiempo is None:
            raise KeyError("Ni 'TIMESTAMP' ni 'DATE' están presentes en el diccionario 'valores'.")

        # Ahora usamos clave_tiempo dinámicamente en el bucle
        for j in range(len(valores[clave_tiempo])):
            hora_sensor = datetime.strptime(valores[clave_tiempo][j], '%Y/%m/%d %H:%M:%S.%f')
            if hora_inicio <= hora_sensor <= hora_fin:
                sensores_por_actividad.append(valores['OBJECT'][j])
        sensorActividad = sensores_por_actividad.copy()
        dictAct[actividad_nombre].append(sensorActividad)
        print("Se ha añadido la actividad: "+actividad_nombre)





def procesar_archivo_csv(ruta_Act, ruta_Sen, dictAct):
    """
    Procesa un archivo CSV según su tipo.

    :param ruta_archivo: Ruta completa del archivo CSV.
    :param tipo: Tipo de archivo basado en su nombre.
    """
     
    print(f"Ejecutando acción para tipo A en {ruta_Act}")
    horas_inicio = subdividir_datos(leer_todas_columnas_csv(ruta_Act), 'DATE BEGIN')
    horas_fin = subdividir_datos(leer_todas_columnas_csv(ruta_Act), 'DATE END')
    act = subdividir_datos(leer_todas_columnas_csv(ruta_Act), 'ACTIVITY')
   
    print(f"Ejecutando acción para tipo B en {ruta_Sen}")
    valores = leer_todas_columnas_csv(ruta_Sen)

    filtrar_sensores_por_actividad(valores, horas_inicio, horas_fin, act, dictAct)


def recorrer_carpetas(base_path, dictAct):
    """
    Recorre todas las subcarpetas desde la carpeta base y procesa archivos CSV según su nombre.

    :param base_path: Ruta de la carpeta base.
    """
    if not os.path.exists(base_path):
        print(f"Error: La carpeta '{base_path}' no existe.")
        return
    
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
                print(f"Procesando archivo: {ruta_completa}")
                
                # Comprobación del nombre del archivo
                if "activity" in archivo:
                    rutaAct = ruta_completa
                elif "sensor" in archivo:
                    rutaSen = ruta_completa
                else:
                    print(f"Omitiendo archivo: {ruta_completa}")
        if rutaAct and rutaSen:
            print(f"\nArchivos emparejados:\n - Activity: {rutaAct}\n - Sensor: {rutaSen}\n")
            procesar_archivo_csv(rutaAct, rutaSen, dictAct)

# Ejecutar la función con la carpeta base
# carpeta_base = r"C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"
carpeta_base = r"C:/Users/jesme/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"
recorrer_carpetas(carpeta_base, dictAct)
for key, value in dictAct.items():
    print(f"{key}: {len(value)}")



def construir_automata(secuencias):
    G = nx.DiGraph()
    
    for secuencia in secuencias:
        for i in range(len(secuencia) - 1):
            origen = secuencia[i]
            destino = secuencia[i + 1]
            if G.has_edge(origen, destino):
                G[origen][destino]['weight'] += 1
            else:
                G.add_edge(origen, destino, weight=1)
    
    return G

def calcular_probabilidades(G):
    for nodo in G.nodes:
        total_salidas = sum(G[nodo][vecino]['weight'] for vecino in G.successors(nodo))
        for vecino in G.successors(nodo):
            G[nodo][vecino]['label'] = f"{G[nodo][vecino]['weight']}/{total_salidas}"

def dibujar_automata(G):
    pos = nx.spring_layout(G, seed=5)  # Para un layout estable
    labels = {edge: G[edge[0]][edge[1]]['label'] for edge in G.edges}
    
    plt.figure(figsize=(10, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightgray', edge_color='black', node_size=2000, font_size=10)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()


secuenciaMañana, secuenciaTarde, secuenciaNoche = [], [], []

def generaSecuencias(base_path, secuenciaMañana, secuenciaTarde, secuenciaNoche):
    if not os.path.exists(base_path):
        print(f"Error: La carpeta '{base_path}' no existe.")
        return
    
    for carpeta_actual, _, archivos in os.walk(base_path):
        print(f"Entrando en carpeta: {carpeta_actual}")

        rutaAct =""

        if not archivos:
            print(f"No se encontraron archivos en {carpeta_actual}")

        for archivo in archivos:
            if archivo.endswith(".csv"):  # Solo considerar archivos CSV
                archivo_lower = archivo.lower()  # Convertir a minúsculas
                ruta_completa = os.path.normpath(os.path.join(carpeta_actual, archivo_lower))
                print(f"Procesando archivo: {ruta_completa}")
                
                # Comprobación del nombre del archivo
                if "activity" in archivo:
                    rutaAct = ruta_completa
                else:
                    print(f"Omitiendo archivo: {ruta_completa}")
        if rutaAct:
            print(f"\nArchivos emparejados:\n - Activity: {rutaAct}\n")
            procesar_secuencias(rutaAct, secuenciaMañana, secuenciaTarde, secuenciaNoche)

      
    grafoMañana = construir_automata(secuenciaMañana)
    calcular_probabilidades(grafoMañana)
    dibujar_automata(grafoMañana)

    grafoTarde = construir_automata(secuenciaTarde)
    calcular_probabilidades(grafoTarde)
    dibujar_automata(grafoTarde)

    grafoNoche = construir_automata(secuenciaNoche)
    calcular_probabilidades(grafoNoche)
    dibujar_automata(grafoNoche)

    return grafoMañana, grafoTarde, grafoNoche


def procesar_secuencias(ruta_Act, secuenciaMañana, secuenciaTarde, secuenciaNoche):
    act = subdividir_datos(leer_todas_columnas_csv(ruta_Act), 'ACTIVITY')
   
    if "b-activity" in ruta_Act:
        secuenciaTarde.append(act)
    elif "c-activity" in ruta_Act:
        secuenciaNoche.append(act)
    else:
        secuenciaMañana.append(act)

grafoMañana, grafoTarde, grafoNoche = generaSecuencias(carpeta_base, secuenciaMañana, secuenciaTarde, secuenciaNoche)

def construir_automata_actividades(secuencias):
    G = nx.DiGraph()
    
    for secuencia in secuencias:
        historial = "[]"  # Nodo inicial vacío
        if historial not in G:
            G.add_node(historial)
        
        for sensor in secuencia:
            nuevo_nodo = f"{historial[:-1]} {sensor}]" if historial != "[]" else f"[{sensor}]"
            if not G.has_node(nuevo_nodo):
                G.add_node(nuevo_nodo)
            
            if G.has_edge(historial, nuevo_nodo):
                G[historial][nuevo_nodo]['weight'] += 1
            else:
                G.add_edge(historial, nuevo_nodo, weight=1, label=sensor)  # Guardar sensor como etiqueta
            
            historial = nuevo_nodo
    
    return G

def dibujar_automata_actividades(G, titulo):
    pos = nx.spring_layout(G, seed=5)  # Para un layout estable
    labels = {edge: G[edge[0]][edge[1]]['label'] for edge in G.edges}
    plt.figure(figsize=(12, 8))
    plt.title(titulo)
    nx.draw(G, pos, with_labels=True, node_color='lightgray', edge_color='black', node_size=2000, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

def generaAutomataActividades(dictAct, dictSec):
    for key, value in dictAct.items():
        print(f"Actividad: {key}")
        dictSec[key] = construir_automata_actividades(value)
        

generaAutomataActividades(dictAct, dictSec)
for key in dictSec.keys():
    dibujar_automata_actividades(dictSec[key], key)
