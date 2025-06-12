from ObtenerRegex import dfa_to_regex
from RPNI import rpni, generaAutomataActividades
from SecuenciasAutomatas import recorrer_carpetas, generaSecuencias
from Metricas import obtenerMetricas, procesar_tests, hacerColumnaLateral

def inicializarDict():
    """
    Inicializa diccionarios con keys de Act01 a Act24.
    """
    dictAct = {}
    for i in range(1, 25):
        dictAct[f"Act{i:02d}"] = []  # Formato con dos dígitos
    return dictAct
            
carpeta_base = r"./../UCAmI Cup/UCAmI Cup/Data/Training/"
carpeta_base_test = r"./../UCAmI Cup/UCAmI Cup/Data/Test/"

pathTraining = r"./../UCAmI Cup/UCAmI Cup/time-slots training.csv"
pathTrainingNuevo = r"./../UCAmI Cup/UCAmI Cup/time-slotstrainingnuevo.csv"
pathTrainingEscribir = r"./../UCAmI Cup/UCAmI Cup/time-slots training escribir.csv"
pathTrainingEscribirNuevo = r"./../UCAmI Cup/UCAmI Cup/time-slots training escribir nuevo.csv"

pathTest = r"./../UCAmI Cup/UCAmI Cup/resultsComprobar.csv"
pathTestNuevo = r"./../UCAmI Cup/UCAmI Cup/resultsComprobarNuevo.csv"
pathTestEscribir = r"./../UCAmI Cup/UCAmI Cup/results.csv"
pathTestEscribirNuevo = r"./../UCAmI Cup/UCAmI Cup/results nuevo.csv"

dictAct = inicializarDict()
dictSec = inicializarDict()
dictGrafoMin = inicializarDict()
dictRegex = inicializarDict()

recorrer_carpetas(carpeta_base, dictAct)

secuenciaMañana, secuenciaTarde, secuenciaNoche = [], [], []

print("RECORDATORIO: ABRIR LA CARPETA DEL CODIGO PARA QUE FUNCIONE")

grafoMañana, grafoTarde, grafoNoche = generaSecuencias(carpeta_base, secuenciaMañana, secuenciaTarde, secuenciaNoche)
generaAutomataActividades(dictAct, dictSec)

# Generar autómatas mínimos y regex para cada actividad
for key, value in dictSec.items():    
    dictGrafoMin[key] = rpni(value, key)
    nodosFinales = [nodo for nodo in dictGrafoMin[key].nodes() if dictGrafoMin[key].nodes[nodo]['label'] == "Positivo"]
    nodoInicial = '[]'
    regex = dfa_to_regex(dictGrafoMin[key], nodoInicial, nodosFinales)
    dictRegex[key] = regex

print("TEST")
procesar_tests(carpeta_base_test, pathTest, pathTestEscribir, grafoMañana, grafoTarde, grafoNoche, dictRegex)
hacerColumnaLateral(pathTest, pathTestNuevo)
hacerColumnaLateral(pathTestEscribir, pathTestEscribirNuevo)
obtenerMetricas(pathTestNuevo, pathTestEscribirNuevo)
print("TRAINING")
procesar_tests(carpeta_base, pathTraining, pathTrainingEscribir, grafoMañana, grafoTarde, grafoNoche, dictRegex)
hacerColumnaLateral(pathTraining, pathTrainingNuevo)
hacerColumnaLateral(pathTrainingEscribir, pathTrainingEscribirNuevo)
obtenerMetricas(pathTrainingNuevo, pathTrainingEscribirNuevo)

print("Para las expresiones regulares de los ganadores")
# Para las expresiones regulares de los ganadores, se pueden usar las siguientes líneas:
dictRegex['Act01'] = "^(D04)+(C01|C05|D04|D05)*"
dictRegex['Act02'] = "^(D01|D02|D04|D10|H01)+"
dictRegex['Act03'] = "^(C04|D01|D02|D04|D08|D10)+"
dictRegex['Act04'] = "^(C04|D01|D02|D04|D08|D10)+"
dictRegex['Act08'] = "^(C02|D10)+"
dictRegex['Act09'] = "^(TV0|S09)*TV0"
dictRegex['Act10'] = "^(M01)+"
dictRegex['Act11'] = "^(TV0C07|C07TV0)(S09)*(TV0C07|C07TV0)"
dictRegex['Act13'] = "^(M01)+"
dictRegex['Act14'] = "^(M01)+"
dictRegex['Act15'] = "^(C01|C08)*(M01)+"
dictRegex['Act16'] = "^(C09)+"
dictRegex['Act17'] = "^(C09)+"
dictRegex['Act18'] = "^(C10|D07)+(C08|C10|D07)*"
dictRegex['Act19'] = "^(D05)+"
dictRegex['Act20'] = "^D09(C12|D09)*"
dictRegex['Act22'] = "^D03(C12|C13|D03)*"
dictRegex['Act23'] = "^C14(C13|C14)+"
dictRegex['Act24'] = "^(C14)+"
dictRegex['Act05'] = "^(SM1)+"
dictRegex['Act06'] = "^(SM1)+"
dictRegex['Act07'] = "^(SM1)+"
dictRegex['Act12'] = "^(S09|SM4|SM5)*SM5(S09|SM4|SM5)*"
dictRegex['Act21'] = "^(SM4)+"

print("TEST")
procesar_tests(carpeta_base_test, pathTest, pathTestEscribir, grafoMañana, grafoTarde, grafoNoche, dictRegex)
hacerColumnaLateral(pathTest, pathTestNuevo)
hacerColumnaLateral(pathTestEscribir, pathTestEscribirNuevo)
obtenerMetricas(pathTestNuevo, pathTestEscribirNuevo)
print("TRAINING")
procesar_tests(carpeta_base, pathTraining, pathTrainingEscribir, grafoMañana, grafoTarde, grafoNoche, dictRegex)
hacerColumnaLateral(pathTraining, pathTrainingNuevo)
hacerColumnaLateral(pathTrainingEscribir, pathTrainingEscribirNuevo)
obtenerMetricas(pathTrainingNuevo, pathTrainingEscribirNuevo)


print("Fin del programa")
