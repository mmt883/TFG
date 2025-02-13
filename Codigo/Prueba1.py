import csv
import os
from datetime import datetime

# Ejemplo de uso:

#Objetivo leer datos de csv y ir dividiendo segun hora inicial y final acorde a actividades
#Tenemos varios csv con datos: Date begin, Date End, Activity, Habitant
#Y otros con: TimeStamp, Object, State, Habitant

# Función para leer una columna específica de un archivo CSV
def leer_columna_csv(ruta_archivo, nombre_columna):
    """
    Lee una columna específica de un archivo CSV y devuelve una lista con los valores de esa columna.

    :param ruta_archivo: Ruta del archivo CSV.
    :param nombre_columna: Nombre de la columna que se desea leer.
    :return: Lista con los valores de la columna especificada.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo '{ruta_archivo}' no existe.")

    valores_columna = []

    try:
        with open(ruta_archivo, mode='r', newline='', encoding='utf-8') as archivo_csv:
            lector_csv = csv.DictReader(archivo_csv, delimiter=';')

            # Verificar si la columna existe en el archivo CSV
            if nombre_columna not in lector_csv.fieldnames:
                print(lector_csv.fieldnames)
                raise ValueError(f"La columna '{nombre_columna}' no existe en el archivo CSV.")

            # Leer y almacenar los valores
            for fila in lector_csv:
                valores_columna.append(fila[nombre_columna])

    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return []

    return valores_columna

def leer_todas_columnas_csv(ruta_archivo):
    """
    Lee todas las columnas de un archivo CSV y devuelve un diccionario con los datos.

    :param ruta_archivo: Ruta del archivo CSV.
    :return: Diccionario con los nombres de las columnas como claves y listas de valores como valores.
    """
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"El archivo '{ruta_archivo}' no existe.")

    datos = {}

    try:
        with open(ruta_archivo, mode='r', newline='', encoding='utf-8') as archivo_csv:
            lector_csv = csv.DictReader(archivo_csv, delimiter=';')

            # Inicializar listas para cada columna
            for nombre_columna in lector_csv.fieldnames:
                datos[nombre_columna] = []

            # Leer y almacenar los valores
            for fila in lector_csv:
                for nombre_columna in lector_csv.fieldnames:
                    datos[nombre_columna].append(fila[nombre_columna])

    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return {}

    return datos

# Ejemplo de uso
# ruta_archivo = 'C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/2017-10-31/2017-10-31-A/2017-10-31-A-sensors.csv'
# datos_csv = leer_todas_columnas_csv(ruta_archivo)

# Imprimir las primeras 5 filas de cada columna para verificar
# for columna, valores in datos_csv.items():
#     print(f"{columna}: {valores[:5]}")

# Función para subdividir los datos según una columna específica
def subdividir_datos(datos, nombre_columna):
    """
    Subdivide los datos en función de los valores de una columna específica.

    :param datos: Diccionario con los datos del CSV.
    :param nombre_columna: Nombre de la columna según la cual subdividir los datos.
    :return: Lista con los valores de la columna especificada en el orden original.
    """
    return datos[nombre_columna]

# Ejemplo de subdivisión de datos
# nombre_columna_para_subdividir = 'TIMESTAMP'  # Reemplazar con el nombre real de la columna
# subdivisiones = subdividir_datos(datos_csv, nombre_columna_para_subdividir)

# Imprimir las subdivisiones para verificar
# for valor, subdatos in subdivisiones.items():
#     print(f"Valor: {valor}")
#     for columna, valores in subdatos.items():
#         print(f"  {columna}: {valores[:5]}")

# Ejemplo de uso
# sensores = 'C:/Users/jesme/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/2017-10-31/2017-10-31-A/2017-10-31-A-sensors.csv'  
# actividades = 'C:/Users/jesme/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/2017-10-31/2017-10-31-A/2017-10-31-A-activity.csv'
sensores = 'C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/2017-10-31/2017-10-31-A/2017-10-31-A-sensors.csv'  
actividades = 'C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/2017-10-31/2017-10-31-A/2017-10-31-A-activity.csv'
nombre_columna = 'TIMESTAMP'  

# Leer los valores
# horas_inicio = subdividir_datos(leer_todas_columnas_csv(actividades), 'DATE BEGIN')
# horas_fin = subdividir_datos(leer_todas_columnas_csv(actividades), 'DATE END')
# act = subdividir_datos(leer_todas_columnas_csv(actividades), 'ACTIVITY')
# valores = leer_todas_columnas_csv(sensores)

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

# Filtrar los valores de los sensores por actividad
# filtrar_sensores_por_actividad(valores, horas_inicio, horas_fin, act, dictAct)

# print(dictAct)
# Imprimir las primeras 5 filas para verificar
#print(valores)  # Muestra solo las primeras 5 líneas



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
carpeta_base = r"C:/Users/Usuario/Desktop/TFG/UCAmI Cup/UCAmI Cup/Data/Training/"
recorrer_carpetas(carpeta_base, dictAct)
for key, value in dictAct.items():
    print(f"{key}: {len(value)}")