import os
import csv

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

def subdividir_datos(datos, nombre_columna):
    """
    Subdivide los datos en función de los valores de una columna específica.

    :param datos: Diccionario con los datos del CSV.
    :param nombre_columna: Nombre de la columna según la cual subdividir los datos.
    :return: Lista con los valores de la columna especificada en el orden original.
    """
    return datos[nombre_columna]