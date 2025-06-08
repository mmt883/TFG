import networkx as nx
from collections import Counter
import matplotlib.pyplot as plt

from SecuenciasAutomatas import construir_automata_actividades

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
        # print(f"Procesando actividad: {key}")

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
    # #Caso especial
    if nodo1 == nodo2:
        # print("C")
        # Eliminamos arcos duplicados sumando los weights
        # Contador para contar cuántas veces aparece cada destino por label
        conteo = {}
        for _, destino, data in grafo.edges(nodo1, data=True):
            label = data.get("label")  # Suponiendo que el atributo es "label"             
            if label:
                if label not in conteo:
                    conteo[label] = list()                   
                conteo[label].append(destino)  # Cuenta las repeticiones
        # Filtrar solo los destinos que aparecen al menos 2 veces
        for label in conteo:
            repetidos = [dest for dest in conteo[label] if len(conteo[label]) >= 2]
            if repetidos:
                # Sumar los pesos de todas las aristas con label "A" y conservar solo una
                weights = []
                keys_to_remove = []
                keep_key = None  # Clave de la arista que conservaremos

                # print(grafo.nodes(data=True))
                # print("\n")
                # print(nodo1, nodo2)
                # print(grafo.edges(nodo1, data=True))

                # Identificar las aristas con label "A"
                if grafo.has_edge(nodo1, nodo1):
                    for key in list(grafo[nodo1][nodo1]):
                        if grafo[nodo1][nodo2][key].get('label') == label:
                            weights.append(grafo[nodo1][nodo2][key].get("weight"))
                            if keep_key is None:
                                keep_key = key  # La primera arista será la que conservemos
                            else:
                                keys_to_remove.append(key)  # Las demás se eliminarán

                # Sumar los pesos y actualizar la arista que conservamos
                if keep_key is not None:
                    grafo[nodo1][nodo2][keep_key]["weight"] = sum(weights)

                # Eliminar las otras aristas con label "A"
                for key in keys_to_remove:
                    grafo.remove_edge(nodo1, nodo2, key=key)

        return grafo


    # Comprobar y mantener la etiqueta 'Positivo' si hay conflicto
    # print(f"Combinando nodos {nodo1} y {nodo2}")
    # print(grafo.nodes(data=True))
    label_nodo1 = grafo.nodes[nodo1].get('label')
    label_nodo2 = grafo.nodes[nodo2].get('label')
    
    # print(nodo1, nodo2, grafo.edges(nodo1, data=True), grafo.edges(nodo2, data=True))
    
    if label_nodo1 != label_nodo2:
        # if 'Positivo' in [label_nodo1, label_nodo2]:
        #     grafo.nodes[nodo1]['label'] = 'Positivo'
        raise ValueError(f"Conflicto de etiquetas: {label_nodo1} y {label_nodo2}")
    
    # Combinar nodo2 en nodo1
    for _, destino, data in grafo.edges(nodo2, data=True):
        if grafo.has_edge(nodo1, destino):
            new_key = max(grafo[nodo1][destino].keys(), default=-1) + 1
        else:
            new_key = 0
        grafo.add_edge(nodo1, destino, key=new_key, **data)    
    grafo.remove_node(nodo2)
    
    return grafo

def evaluar_secuencias(grafo, secuencias):
    """
    Procesa las secuencias y verifica si terminan en nodos con label 'Negativo'.
    
    :param grafo: Un objeto MultiDiGraph de NetworkX.
    :param secuencias: Lista de secuencias de sensores.
    :return: True si todas las secuencias terminan en nodos con label 'Negativo', False en caso contrario.
    """
    for secuencia in secuencias:
        nodo_actual = '[]'  # Nodo inicial
        sensores = secuencia.strip('[]').split()
        
        for sensor in sensores:
            encontrado = False
            for _, nodo_destino, data in grafo.out_edges(nodo_actual, data=True):
                if data.get('label') == sensor:
                    nodo_actual = nodo_destino
                    encontrado = True
                    break
            
            if not encontrado:
                break  # Se detiene si no hay transición válida
        
        if nodo_actual in grafo.nodes:
            label = grafo.nodes[nodo_actual].get('label')
            if label != 'Negativo':
                # print(f"Secuencia {sensores} termina en nodo {nodo_actual} con label {label}")
                return False
        else:
            # print(f"Secuencia {sensores} termina en nodo {nodo_actual} con label {label}")
            return False  # Si el nodo final no existe en el grafo
    
    return True

def rpni_aux(grafo, nodoAMirar, nodoAnterior, negativos):

    # Si uno es positivo y el otro es negativo, pasar
    if grafo.nodes[nodoAMirar]['label'] != grafo.nodes[nodoAnterior]['label']:
        return False, None

    # Crear una copia del grafo para trabajar
    grafoNuevo = grafo.copy()

    # Elimino los arcos salientes de nodoAMirar y los añado a nodoAnterior, finalmente elimino nodoAMirar en el nuevo grafo
    for _, destino, data in grafo.edges(nodoAMirar, data=True):
        grafoNuevo.add_edge(nodoAnterior, destino, **data)
    grafoNuevo.remove_node(nodoAMirar)

    # Si hay un arco de nodoAnterior a nodoAMirar, eliminarlo y añadir uno de nodoAnterior a nodoAnterior con el mismo símbolo
    if grafo.has_edge(nodoAnterior, nodoAMirar):
        for _, attributes in grafo[nodoAnterior][nodoAMirar].items():
            if nodoAnterior in grafoNuevo and grafoNuevo.has_edge(nodoAnterior, nodoAnterior):
                new_key = max(grafoNuevo[nodoAnterior][nodoAnterior].keys(), default=-1) + 1
            else:
                new_key = 0  # Si no existe, empieza en 0
            grafoNuevo.add_edge(nodoAnterior, nodoAnterior, key=new_key, **attributes)
    else: #Añadir los arcos que iban originalmente a nodoAMirar a nodoAnterior   #Esta dividido con un else porque es un arbol y daria igual
        for nodo in grafo.nodes():
            if grafo.has_edge(nodo, nodoAMirar):
                for _, attributes in grafo[nodo][nodoAMirar].items():
                    if nodo == nodoAMirar: #Si hay un arco de nodoAMirar a nodoAMirar, añadirlo de nodoAnterior a nodoAnterior
                        if nodoAnterior in grafoNuevo and grafoNuevo.has_edge(nodoAnterior, nodoAnterior):
                            new_key = max(grafoNuevo[nodoAnterior][nodoAnterior].keys(), default=-1) + 1
                        else:
                            new_key = 0
                        grafoNuevo.add_edge(nodoAnterior, nodoAnterior, key=new_key, **attributes)
                    else:
                        if nodo in grafoNuevo and grafoNuevo.has_edge(nodo, nodoAnterior):
                            new_key = max(grafoNuevo[nodo][nodoAnterior].keys(), default=-1) + 1
                        else:
                            new_key = 0
                        grafoNuevo.add_edge(nodo, nodoAnterior, key=new_key, **attributes)


    # Combina nodos a los que se llega con el mismo símbolo desde cualquier nodo
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
            for label in conteo:
                repetidos = [dest for dest in conteo[label] if len(conteo[label]) >= 2]
                if repetidos:
                    duplicados = sorted(repetidos, key=lambda x: (len(x), x))
                    for i in range(1, len(duplicados)):
                        if duplicados[i] in grafoCambios.nodes() and duplicados[0] in grafoCambios.nodes():
                            grafoCambios = combinar_nodos(grafoCambios, duplicados[0], duplicados[i])
                            combinacion_realizada = True
                            # print("Nodos combinados")
                            # print(duplicados[0], duplicados[i])
        grafoNuevo = grafoCambios
        # print("BB")

    #Evaluar las secuencias
    if evaluar_secuencias(grafoNuevo, negativos):
        # print("Todo correcto")
        return True, grafoNuevo
    else:
        # print("No se acepta")
        return False, None


def rpni(grafo, key):
    # print(f"Procesando {key}")
    positivos = [nodo for nodo in grafo.nodes if grafo.nodes[nodo]['label'] == "Positivo"]
    negativos = [nodo for nodo in grafo.nodes if grafo.nodes[nodo]['label'] == "Negativo"]

    nodosOrdenados = extraerNodosOrdenados(grafo)

    estado = 0

    cambioHecho = True
    while cambioHecho:
        cambioHecho = False
        for i, nodoAMirar in enumerate(nodosOrdenados):
            # print(f"Procesando nodo {nodoAMirar}")
            nodosAnteriores = nodosOrdenados[:i]
            if(not nodosAnteriores):
                pass

            for nodoAnterior in nodosAnteriores:
                # print(f"Procesando nodo anterior {nodoAnterior}")
                try:
                    resultado, grafoNuevo = rpni_aux(grafo, nodoAMirar, nodoAnterior, negativos)
                except ValueError as e:
                    # print(f"Error: {e}")
                    resultado = False
                    grafoNuevo = None
                # print(resultado)

                if(resultado):
                    # print("\n")
                    # print(grafoNuevo.nodes(data=True))
                    # print(grafoNuevo.edges(data=True))
                    cambioHecho = True
                    break
            if(cambioHecho):
                break
        if(cambioHecho):
            grafo = grafoNuevo
            nodosOrdenados = extraerNodosOrdenados(grafo)
            estado  += 1
            #dibujar_automata(grafo, f"{key} Estado {estado}")
            # print("\n")
    
    return grafo



