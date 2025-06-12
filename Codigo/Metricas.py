import numpy as np
import os
import csv
from datetime import datetime, timedelta
from InferenciaActividades import obtenerActividadesDocumento

def redondear_a_30_segundos(fecha_hora):
    # Dividir la fecha en partes
    segundos = fecha_hora.second

    # Ver si los segundos están más cerca de 00 o de 30
    if segundos < 15:
        # Redondear hacia abajo a 00 segundos
        redondeado = fecha_hora.replace(second=0, microsecond=0)
    elif segundos >= 15 and segundos < 45:
        # Redondear a 30 segundos
        redondeado = fecha_hora.replace(second=30, microsecond=0)
    else:
        # Redondear al siguiente minuto (es decir, incrementar minuto y poner segundos a 00)
        if fecha_hora.minute == 59:
            # Si el minuto es 59, tenemos que incrementar la hora y poner minuto y segundo a 00
            redondeado = fecha_hora.replace(second=0, minute=0) + timedelta(hours=1)
        else:
            redondeado = fecha_hora.replace(second=0, minute=fecha_hora.minute + 1, microsecond=0)

    return redondeado

def procesar_tests(base_path, pathTraining, pathTrainingEscribir, grafoMañana, grafoTarde, grafoNoche, dictRegex):

    # Comprobar si la carpeta base existe
    if not os.path.exists(base_path):
        return
        
    # Comprobar si la carpeta base existe
    if not os.path.exists(pathTraining):
        return
        
    # Comprobar si la carpeta base existe
    if not os.path.exists(pathTrainingEscribir):
        return

    with open(pathTraining, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        

        with open(pathTrainingEscribir, mode='w', newline='', encoding='utf-8') as outcsv:
            writer = csv.writer(outcsv, delimiter=';')
            

            for row in reader:
                filename = row[0]
                # print("Filename: ", filename)
                if filename.split(";")[0] == "":
                    writer.writerow([""])
                    continue
                if "activity" in filename:
                    filename = filename.replace(";", "")
                    writer.writerow([filename])
                    filename = filename.replace("activity", "sensors")
                    # filename = filename.lower()
                    # Recorrer todas las subcarpetas
                    Encontrado = False
                    for carpeta_actual, _, archivos in os.walk(base_path):


                        rutaArchivo =""

                        for archivo in archivos:
                            if archivo.endswith(".csv"):  # Solo considerar archivos CSV
                                archivo_lower = archivo.lower()  # Convertir a minúsculas
                                ruta_completa = os.path.normpath(os.path.join(carpeta_actual, archivo_lower))
                                
                                if filename in archivo:
                                    rutaArchivo = ruta_completa
                                    # print(f"\nArchivos emparejados:\n - Activity: {rutaArchivo}\n")
                                    Encontrado = True
                                    break
                        if Encontrado:
                            break
                    # print("Ruta Archivo: ", rutaArchivo)
                    if rutaArchivo == "":
                        print(filename)
                    actividades = obtenerActividadesDocumento(rutaArchivo, grafoMañana, grafoTarde, grafoNoche, dictRegex)
                if "Time" in filename:
                    
                    nombresActividades = []
                    for actividad in actividades:
                        nombresActividades.append(actividad[0])
                    nombresActividades = list(dict.fromkeys(nombresActividades))
                    
                    fila = ["Timestamp"]
                    fila.extend(nombresActividades)
                    writer.writerow(fila)
                    continue
                if ":" in filename:
                    timestamp = filename.split(";")[0]
                    # print("Timestamp: ", timestamp)
                    # print("Fila: ", filename)
                    
                    hora = datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S') #Tomamos la hora de inicio de la actividad
                    # print("Hora obtenida")
                    salida = [None] * (len(nombresActividades) + 1)
                    # print("Salida: ", salida)
                    # print("filename: ", filename)
                    salida[0] = timestamp
                    for actividad, hora_inicio, hora_fin in actividades:
                        # print("Actividad: ", actividad, "Hora inicio: ", hora_inicio, "Hora fin: ", hora_fin)
                        hora_inicio = datetime.strptime(hora_inicio, '%Y/%m/%d %H:%M:%S.%f') #Tomamos la hora de inicio de la actividad
                        hora_inicio = redondear_a_30_segundos(hora_inicio)
                        # print("Hora inicio: ")

                        hora_fin = datetime.strptime(hora_fin, '%Y/%m/%d %H:%M:%S.%f') #Tomamos la hora de fin de la actividad
                        hora_fin = redondear_a_30_segundos(hora_fin)
                        # print("Hora fin: ")
                        indice = nombresActividades.index(actividad) #Obtenemos el indice de la actividad en la fila
                        if hora_inicio <= hora <= hora_fin:
                            if "results" in pathTrainingEscribir:
                                salida[indice+1] = "VERDADERO" 
                            else:
                                salida[indice+1] = "TRUE" 
                        else:
                            if "results" in pathTrainingEscribir:
                                salida[indice+1] = "FALSO" 
                            else:
                                salida[indice+1] = "FALSE" 

                    writer.writerow(salida)

def hacerColumnaLateral(pathTraining, pathTrainingNuevo):
    # Comprobar si la carpeta base existe
    if not os.path.isdir(os.path.dirname(pathTraining)):
        return
        
    # Comprobar si la carpeta base existe
    if not os.path.isdir(os.path.dirname(pathTrainingNuevo)):
        return

    with open(pathTraining, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        
        with open(pathTrainingNuevo, mode='w', newline='', encoding='utf-8') as outcsv:
            writer = csv.writer(outcsv, delimiter=';')
            

            for row in reader:
                filename = row[0]
                elementos = filename.split(";")
                # print("Filename: ", filename)
                if elementos[0] == "":
                    writer.writerow([""])
                    continue
                if "activity" in elementos[0]:
                    filename = filename.replace(";", "")
                    writer.writerow([filename])
                    continue
                    
                    
                if "Time" in elementos[0]:
                    writer.writerow(["Inicio"])
                    actividades = filename.split(";")[1:]
                    continue

                if ":" in elementos[0]:
                    escribir = []
                    escribir.append(elementos[0])
                    actividadAEscribir = []
                    if "results" in pathTraining:
                        verdadero = "VERDADERO"
                        falso = "FALSO"
                    else:
                        verdadero = "TRUE"
                        falso = "FALSE"
                    
                    for i in range(len(actividades)):
                        if elementos[i+1] == verdadero:
                            #actividadAEscribir.append(actividades[i]) si hay varuas actividades
                            actividadAEscribir = actividades[i]
                            
                    if not verdadero in elementos:
                        actividadAEscribir = "Ninguna"

                    escribir.append(actividadAEscribir)
                    writer.writerow(escribir)
                    continue


def distancia_levenshtein_lista(lista1, lista2):
    len1, len2 = len(lista1), len(lista2)
    dp = np.zeros((len1 + 1, len2 + 1), dtype=int)

    for i in range(len1 + 1):
        dp[i][0] = i
    for j in range(len2 + 1):
        dp[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if lista1[i - 1] == lista2[j - 1]:
                costo = 0
            else:
                costo = 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # eliminar
                dp[i][j - 1] + 1,      # insertar
                dp[i - 1][j - 1] + costo  # sustituir
            )

    return dp[len1][len2]

def obtenerMetricas(archivoBase, archivoMio):
    
     # Comprobar si la carpeta base existe
    if not os.path.isdir(os.path.dirname(archivoBase)):
        return
        
    # Comprobar si la carpeta base existe
    if not os.path.isdir(os.path.dirname(archivoMio)):
        return

    actividadesCorrectas = 0
    actividadesTotales = 0
    dictSecuencias = dict()
    dictSecuencias2 = dict()
    secuencias = 0
    

    with open(archivoBase, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.reader(csvfile))

        with open(archivoMio, newline='', encoding='utf-8') as csvfile2:
            reader2 = list(csv.reader(csvfile2))

            for i, row in enumerate(reader):
                filename = row[0]
                elementos = filename.split(";")
                filename2 = reader2[i][0]
                elementos2 = filename2.split(";")
                

                if elementos[0] == "":
                    if listaBase and listaPred:
                        distancia = distancia_levenshtein_lista(listaBase, listaPred)
                        
                        dictSecuencias2[nombre] = [distancia, len(listaBase)]
                        dictSecuencias[nombre] = distancia/len(listaBase)

                    continue
                if "activity" in elementos[0]:
                    secuencias += 1
                    nombre = elementos[0]
                    listaBase = list()
                    listaPred = list()
                    elemBaseAnterior = ""
                    elemPredAnterior = ""
                    continue
                if "Inicio" in elementos[0]:
                    continue
                if ":" in elementos[0]:
                    if not "Ninguna" in elementos[1] and not elemBaseAnterior == elementos[1]:
                        listaBase.append(elementos[1])
                        elemBaseAnterior = elementos[1]
                    if not "Ninguna" in elementos2[1] and not elemPredAnterior == elementos2[1]:
                        listaPred.append(elementos2[1])
                        elemPredAnterior = elementos2[1]
                    datos1 = elementos[1]
                    datos2 = elementos2[1]
                    
                    actividadesTotales += 1
                    if datos1 == datos2:
                        actividadesCorrectas += 1

            #Añadimos el ultimo elemento
            distancia = distancia_levenshtein_lista(listaBase, listaPred)
            
            dictSecuencias2[nombre] = [distancia, len(listaBase)]
            dictSecuencias[nombre] = distancia/len(listaBase)
    distanciasNorm = []
    distanciaTotal = 0
    for (key, value), (key2, value2) in zip(dictSecuencias.items(), dictSecuencias2.items()):
        print("Actividad:", key, "Distancia:", value2[0], "Longitud:", value2[1], "Normalizada:", value)
        distanciasNorm.append(value)
        distanciaTotal += value2[0]
    print("Media distancias normalizadas: ", sum(distanciasNorm)/secuencias)
    print("Distancia total: ", distanciaTotal, "Distancia media: ", distanciaTotal/secuencias)
    print("Actividades correctas: ", actividadesCorrectas, "Actividades totales: ", actividadesTotales)
    print("Porcentaje de actividades correctas: ", actividadesCorrectas/actividadesTotales*100, "%")