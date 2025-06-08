import re
from LecturasCSV import leer_columna_csv
from RPNI import es_sensor_SM

def obtenerActividadesPosibles(grafo_A_Mirar, actividadAnterior, actividadesAnteriores):
    """
    En funcion del nombre del documento(mañana, tarde o noche) se obtienen las actividades posibles en funcion de la actividad anterior.
    :param nombreDocumento: Nombre del documento CSV.
    :param actividadAnterior: Actividad anterior.
    
    :return: Lista de actividades posibles.
    """

    actividadesPosibles = []
    PosiblesEnCualquierMomento = ["Act11", "Act09", "Act14", "Act18", "Act12"]
    #if actividadAnterior in PosiblesEnCualquierMomento and not any(actividad in grafo_A_Mirar.nodes() for actividad in PosiblesEnCualquierMomento):
    if actividadAnterior in PosiblesEnCualquierMomento and actividadesAnteriores.index(actividadAnterior) > actividadesAnteriores.index("Act11"):
        
        return actividadesAnteriores
    
    if actividadAnterior == "": #Si son iniciales no pueden tener EXTRAS
        # Cojo los nodos iniciales del grafo
        nodos_iniciales = [nodo for nodo in grafo_A_Mirar.nodes() if grafo_A_Mirar.nodes[nodo].get('label') == 'Inicial']   
        actividadesPosibles = nodos_iniciales
        # print("Actividades Posibles: ", actividadesPosibles)
        return actividadesPosibles
    else:    
        destinos_con_peso = [
            (destino, data['label'])
            for _, destino, key, data in grafo_A_Mirar.out_edges(actividadAnterior, keys=True, data=True)
            if 'label' in data
        ]

        if not destinos_con_peso:
            # Si no hay destinos, no se puede hacer nada
            return []

        # print("Destinos con peso: ", destinos_con_peso)

        # Ordenar por peso
        destinos_ordenados = [destino for destino, peso in sorted(destinos_con_peso, key=lambda x: x[1], reverse=True)]
        actividadesPosibles = destinos_ordenados

    #Por último, añadimos distintas actividades a mano que podrian ocurrir en cualquier momento
    actividadesPosibles.extend(PosiblesEnCualquierMomento)

    # Filtrar actividades posibles para que no se repitan
    actividadesPosibles = list(dict.fromkeys(actividadesPosibles))

    return actividadesPosibles


def obtenerActividadesDocumento(direccionDocumento, grafoMañana, grafoTarde, grafoNoche, dictRegex):
    """
    Lee un documento de sensores extrayendo tuplas Sensor, Tiempo y luego procesa los sensores sobre los regex de las actividades posibles en funcion de los grafos de cada tiempo.
    :param nombre_documento: Nombre del documento CSV.
    :return: Lista de (actividades, tiempo-inicio, tiempo-fin).
    """
    
    sensoresBase = leer_columna_csv(direccionDocumento, 'OBJECT')
    sensoresNoSM = [(sensor, i) for i, sensor in enumerate(sensoresBase) if not es_sensor_SM(sensor)]
    sensores = [(sensor, i) for i, sensor in enumerate(sensoresBase)]

    tiempos = leer_columna_csv(direccionDocumento, 'TIMESTAMP')

    if "a-sensors" in direccionDocumento:
        grafo_A_Mirar = grafoMañana
    elif "b-sensors" in direccionDocumento:
        grafo_A_Mirar = grafoTarde
    else:
        grafo_A_Mirar = grafoNoche

    actividades = []

    actividadAnterior = ""
    actividadesAnteriores = []
    FIN = False
    while not FIN:
        actividadesPosibles = obtenerActividadesPosibles(grafo_A_Mirar, actividadAnterior, actividadesAnteriores)
        sensoresString = "".join([x[0] for x in sensores])
        sensoresNoSMString = "".join([x[0] for x in sensoresNoSM])
        matcheado = False
        for actividad in actividadesPosibles:
            expresionReg = dictRegex[actividad]

            match = re.search(expresionReg,sensoresString)
            matchNoSM = re.search(expresionReg,sensoresNoSMString)
            
            if matchNoSM:
                inicio = matchNoSM.start()//3
                fin = matchNoSM.end()//3
                if fin <= 0:
                    fin = 0
                
                
                actividades.append((actividad, tiempos[sensoresNoSM[inicio][1]], tiempos[sensoresNoSM[fin-1][1]]))
                # print("================")
                # print("Actividad NO SM: ", actividad, "Tiempo Inicio: ", tiempos[sensores[inicio][1]], "Tiempo Fin: ", tiempos[sensores[fin][1]])
                # print("================")
                transicion = sensoresNoSM[fin-1][1]
                sensoresNoSM = sensoresNoSM[fin:] # Actualizamos la lista de sensores a partir del último encontrado
                sensores = [(sensor, i) for i, sensor in enumerate(sensoresBase) if i > transicion] # Actualizamos la lista de sensores a partir del último encontrado
                actividadesAnteriores = actividadesPosibles.copy()
                actividadAnterior = actividad
                matcheado = True
            elif match:
                inicio = match.start()//3
                fin = match.end()//3
                # print("¡Encontrado!")
                actividades.append((actividad, tiempos[sensores[inicio][1]], tiempos[sensores[fin-1][1]]))
                # print("================")
                # print("Actividad: ", actividad, "Tiempo Inicio: ", tiempos[sensores[inicio][1]], "Tiempo Fin: ", tiempos[sensores[fin][1]])
                # print("================")
                # print("Sensores: ", sensores[inicio][0], " ", sensores[fin][0])
                sensores = sensores[fin:] # Actualizamos la lista de sensores a partir del último encontrado
                sensoresNoSM = [(sensor, i) for sensor, i in sensores if not es_sensor_SM(sensor)]
                actividadesAnteriores = actividadesPosibles.copy()
                actividadAnterior = actividad
                matcheado = True
                
            if matcheado:
                # Si hemos matcheado, salimos del bucle de actividades posibles
                break
                
        if not matcheado:
            if len(sensores) == 0:
                # Si no hay más sensores, salimos del bucle
                # print("No hay más sensores")
                FIN = True
            
            elif actividadesPosibles == []:
                # Si no hay actividades posibles, salimos del bucle
                # print("No hay actividades posibles")
                FIN = True
            else:
                if sensoresNoSM == [] or sensores[0][1] < sensoresNoSM[0][1]:
                    #Quitamos el primer sensor de la lista sensores
                    sensores = sensores[1:]
                else:
                    #Quitamos el primer sensor de la lista sensoresNoSM
                    sensoresNoSM = sensoresNoSM[1:]
                    sensores = sensores[1:]

    return actividades