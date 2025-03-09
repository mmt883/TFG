import os
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from LecturasCSV import leer_todas_columnas_csv, leer_columna_csv
from collections import Counter



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
    Construye un autómata a partir de una lista de secuencias de actividades (DiGraph).

    :param secuencias: Lista de secuencias de actividades.
    :return: Un DiGraph con nodos etiquetados como "Inicial", "Intermedio" o "Final".
    """

    G = nx.DiGraph()  # Inicializar grafo dirigido

    for secuencia in secuencias:  # Recorrer cada secuencia
        for i in range(len(secuencia)):
            origen = secuencia[i]
            destino = secuencia[i + 1] if i < len(secuencia) - 1 else None

            # Si la arista existe, aumentar el peso; si no, crearla con peso 1
            if destino:
                if G.has_edge(origen, destino):
                    G[origen][destino]['weight'] += 1
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

    # Colores de los nodos según su etiqueta
    node_colors = [
        'green' if G.nodes[node].get('label') in ['Inicial', 'Positivo']
        else 'red' if G.nodes[node].get('label') == 'Final'
        else 'lightgray'
        for node in G.nodes
    ]
    plt.figure(figsize=(12, 8))
    plt.title(titulo)
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='black', node_size=2000, font_size=8)
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
                G[historial][nuevo_nodo]['weight'] += 1
            else:
                G.add_edge(historial, nuevo_nodo, weight=1, label=sensor)  # Guardar sensor como etiqueta
            
            # Actualizamos el historial
            historial = nuevo_nodo

        G.nodes[historial]['label'] = "Positivo"
    
    return G

# def generaAutomataActividades(dictAct, dictSec):
#     for key, value in dictAct.items():
#         print(f"Actividad: {key}")
#         dictSec[key] = construir_automata_actividades(value)

def es_sensor_SM(sensor):
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

        # Verificar si existe al menos un sensor NO SM en alguna lista
        existe_sensor_no_sm = any(
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

def extraerNodosOrdenados(grafo):
    listaNodos = list(grafo.nodes())

    # # Eliminar corchetes y dividir elementos en listas ordenables
    # listaLimpia = [elem.strip('[]').split() for elem in listaNodos]

    # Ordenar por número de palabras, luego alfabéticamente, luego numéricamente
    listaOrdenada = sorted(listaNodos, key=lambda x: (len(x), x))

    # Convertir de vuelta a strings sin corchetes
    # nodosOrdenados = [' '.join(elem) for elem in listaOrdenada]

    return listaOrdenada

def combinar_nodos(grafo, nodo1, nodo2):
    # Combinar nodo2 en nodo1
    for _, destino, data in grafo.edges(nodo2, data=True):
        grafo.add_edge(nodo1, destino, **data)
    grafo.remove_node(nodo2)
    return grafo

def rpni_aux(grafo, nodoAMirar, nodoAnterior, positivos, negativos):


    #Si uno es positivo y el otro es negativo pasar
    # Combino nodoAnterior con nodo para ello 
    # Elimino los arcos de nodoAMirar y los añado a nodoAnterior
    # Si hay un arco de nodoAnterior a nodoAMirar, lo elimino y lo añado de nodoAnterior a nodoAnterior con el mismo simbolo
    # Si desde nodoAnterior hay mas de un arco con el simbolo de nodoAMirar a otro nodo, Esos nodos tambien se deben combinar con nodoAnterior y hacer las mismas comprobaciones
    # Si desde nodoAnterior hay mas de un arco con la misma etiqueta a nodos distintos esos dos nodos se deben combinar y hacer las mismas comprobaciones
    # Por ultimo mirar si se acepta una combinacion negativa, si es asi, volver a estado seguro y pasar de nodoAnterior, Si no acepta ninguna combinacion negativa, guardar nuevo estado seguro

    #Si va a guardar estado seguro, devolver True, grafoResultante
    #Si no va a guardar estado seguro, devolver False, none

    # Si uno es positivo y el otro es negativo, pasar
    if (nodoAMirar in positivos and nodoAnterior in negativos) or (nodoAMirar in negativos and nodoAnterior in positivos):
        return False, None

    # Crear una copia del grafo para trabajar
    grafoNuevo = grafo.copy()

    # Eliminar los arcos de nodoAMirar y añadirlos a nodoAnterior
    for _, destino, data in grafo.edges(nodoAMirar, data=True):
        grafoNuevo.add_edge(nodoAnterior, destino, **data)
    grafoNuevo.remove_node(nodoAMirar)

    print("ELIMINAR LOS ARCOS DE NODOAMIRAR Y AÑADIRLOS A NODOANTERIOR")
    print(grafoNuevo.nodes())
    print(grafoNuevo.edges())
    print("\n")

    dataAnteriorAMirar = grafo[nodoAnterior][nodoAMirar].get('label')

    # Si hay un arco de nodoAnterior a nodoAMirar, eliminarlo y añadir uno de nodoAnterior a nodoAnterior con el mismo símbolo
    if grafo.has_edge(nodoAnterior, nodoAMirar):
        data = grafo[nodoAnterior][nodoAMirar]
        grafoNuevo.add_edge(nodoAnterior, nodoAnterior, **data)
        # grafoNuevo.remove_edge(nodoAnterior, nodoAMirar)

    print("SI HAY UN ARCO DE NODOANTERIOR A NODOAMIRAR, ELIMINARLO Y AÑADIR UNO DE NODOANTERIOR A NODOANTERIOR CON EL MISMO SÍMBOLO")
    print(grafoNuevo.nodes())
    print(grafoNuevo.edges())
    print(grafoNuevo[nodoAnterior][nodoAnterior].get('label'))
    print("\n")

    # Comprobar si hay más de un arco con el símbolo de nodoAMirar a otro nodo desde nodoAnterior
    combinacion_realizada = True
    while combinacion_realizada:
        combinacion_realizada = False
        grafoCambios = grafoNuevo.copy()
        for _, destino, data in grafoNuevo.edges(nodoAnterior, data=True):
            if grafoCambios[nodoAnterior][destino].get('label') == dataAnteriorAMirar and destino != nodoAnterior:
                print("A")
                print(nodoAnterior, destino)
                grafoCambios = combinar_nodos(grafoCambios, nodoAnterior, destino)
                combinacion_realizada = True
        grafoNuevo = grafoCambios

    print("Comprobar si hay más de un arco con el símbolo de nodoAMirar a otro nodo desde nodoAnterior")
    print(grafoNuevo.nodes())
    print(grafoNuevo.edges())
    print("\n")

    # Comprobar si hay más de un arco con el símbolo de nodoAMirar a otro nodo desde nodoAnterior
    combinacion_realizada = True
    while combinacion_realizada:
        combinacion_realizada = False
        grafoCambios = grafoNuevo.copy()
        for nodo in sorted(list(grafoNuevo.nodes()), key=lambda x: (len(x), x)):

            # Contador para contar cuántas veces aparece cada destino por label
            conteo = {}

            for _, destino, data in grafoCambios.edges(nodo, data=True):
                label = data.get("label")  # Suponiendo que el atributo es "label"
                
                if label:
                    if label not in conteo:
                        conteo[label] = list()
                    
                    conteo[label].append(destino)  # Cuenta las repeticiones

            # Filtrar solo los destinos que aparecen al menos 2 veces
            print("CONTEO")
            print(nodo)
            print(conteo)
            for label in conteo:
                repetidos = [dest for dest in conteo[label] if len(conteo[label]) >= 2]
                if repetidos:
                    duplicados = sorted(repetidos, key=lambda x: (len(x), x))
                    print("Duplicados")
                    print(duplicados)
                    for i in range(1, len(duplicados)):
                        grafoCambios = combinar_nodos(grafoCambios, duplicados[0], duplicados[i])
                        combinacion_realizada = True
                        print("Nodos combinados")
                        print(duplicados[0], duplicados[i])
        grafoNuevo = grafoCambios
        print("BB")

                    
            
                

        # # Comprobar si hay más de un arco con la misma etiqueta a nodos distintos desde nodoAnterior
        # etiquetas = {}
        # for _, destino, data in grafo.edges(nodoAnterior, data=True):
        #     etiqueta = data.get('label')
        #     if etiqueta in etiquetas:
        #         grafoNuevo = combinar_nodos(grafoNuevo, etiquetas[etiqueta], destino, positivos, negativos)
        #         combinacion_realizada = True
        #     else:
        #         etiquetas[etiqueta] = destino

        # # Volver a comprobar lo mismo para el nodo resultante
        # for _, destino, data in list(grafoNuevo.edges(nodoAnterior, data=True)):
        #     etiqueta = data.get('label')
        #     if etiqueta in etiquetas:
        #         grafoNuevo = combinar_nodos(grafoNuevo, etiquetas[etiqueta], destino, positivos, negativos)
        #         combinacion_realizada = True
        #     else:
        #         etiquetas[etiqueta] = destino

    print("DUPLICADOS ELIMINADOS")
    print(grafoNuevo.nodes())
    print(grafoNuevo.edges())
    print("\n")
    # Comprobar si se acepta una combinación negativa
    # for nodo in negativos:
    #     if not any(grafoNuevo.has_edge(nodo, destino) and grafoNuevo.nodes[destino]['label'] == "Negativo" for destino in grafoNuevo.successors(nodo)):
            
    #         return False, None

    # Guardar nuevo estado seguro
    return True, grafoNuevo


def rpni(grafo):
    positivos = [nodo for nodo in grafo.nodes if grafo.nodes[nodo]['label'] == "Positivo"]
    negativos = [nodo for nodo in grafo.nodes if grafo.nodes[nodo]['label'] == "Negativo"]

    nodosOrdenados = extraerNodosOrdenados(grafo)
    
    print(nodosOrdenados)
    estadoSeguro = (grafo.copy(), nodosOrdenados.copy())
    print(estadoSeguro)

    cambioHecho = True
    while cambioHecho:
        cambioHecho = False
        for i, nodoAMirar in enumerate(nodosOrdenados):
            print(f"Procesando nodo {nodoAMirar}")
            nodosAnteriores = nodosOrdenados[:i]
            if(not nodosAnteriores):
                pass

            for nodoAnterior in nodosAnteriores:
                print(f"Procesando nodo anterior {nodoAnterior}")
                resultado, grafoNuevo = rpni_aux(grafo, nodoAMirar, nodoAnterior, positivos, negativos)

                if(resultado):
                    print(grafoNuevo.nodes())
                    print(grafoNuevo.edges())
                    cambioHecho = True
                    break
            if(cambioHecho):
                break
        if(cambioHecho):
            grafo = grafoNuevo
            nodosOrdenados = extraerNodosOrdenados(grafo)
            

        





# def minimizar_automatas_RPNI(dictSec):
#     """
#     Minimiza los autómatas de las actividades con el algoritmo RPNI.

#     Intento de Fusión de Estados: Se prueba combinar estados del autómata, asegurando que la fusión no genere una contradicción con los ejemplos de entrenamiento.

#     Validación: Si la fusión respeta la clasificación de ejemplos positivos y negativos, se acepta la unión; de lo contrario, se rechaza.

#     Minimización: Se repite el proceso hasta que no haya más fusiones posibles.

#     :param dictSec: Diccionario que contiene los autómatas de las actividades.

#     """
#     pass






carpeta_base = r"C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"
# carpeta_base = r"C:/Users/jesme/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"

dictAct = inicializarDict()
dictSec = inicializarDict()

recorrer_carpetas(carpeta_base, dictAct)
for key, value in dictAct.items():
    print(f"{key}: {len(value)}")

secuenciaMañana, secuenciaTarde, secuenciaNoche = [], [], []

grafoMañana, grafoTarde, grafoNoche = generaSecuencias(carpeta_base, secuenciaMañana, secuenciaTarde, secuenciaNoche)
   
generaAutomataActividades(dictAct, dictSec)

# for key in dictSec.keys():
#     dibujar_automata(dictSec[key], key)

rpni(dictSec["Act15"])
    
# dibujar_automata(rpni(dictSec["Act15"]), "Act 15 minimizada")

# Proparamos el RPNI para minimizar los autómatas


