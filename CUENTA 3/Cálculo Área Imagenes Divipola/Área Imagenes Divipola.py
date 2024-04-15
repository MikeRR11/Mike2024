# Seleccionar por atributos uno o mas municipios saber cuantas imagenes municipios
# sacar prom area imagenes
# sumar todas las areas y factor 70%
# ese num multiplar prom imagenes y factor
# saber cuanto se paga

# reporte

# cuantas imagenes netas caben y ya, poner dinamico el factor de traslap


# no tiene resolucion con la que se rija 

# sacar el area total de area de las imagenes, sacar overlap 70%
# sacar promedio de todas las imagenes 

# #dentro de las bases hay un campo nubes y sombras, al calculo tener en cuenta nubes y sombras, si se tienen en cuenta se resta al área efectiva del proyecto, poner boton


import arcpy
from arcpy.sa import *
import os

arcpy.env.overwriteOutput = True
#Llamar municipios elite

# gdb = r"\\172.26.0.20\Elite_Sub_Geografia_Cartografia\Coberturas\GDB_FLET_Agosto_2023.gdb"

codigos = arcpy.GetParameter(0) #Ingreso codigos Divipola
gdb = r"C:\Users\michael.rojas\Documents\CUENTA3\PENDIENTESMDT\Municipios_Agosto_2023.gdb\Limites_Entidades_Territoriales\Munpio" 
ORTO = arcpy.GetParameterAsText(1) #Imagenes de Entrada
ruta_salida = arcpy.GetParameterAsText(2) # Ruta Salida
Nubes = arcpy.GetParameterAsText(3) #Incluir Nubes

codigos_2 = []
for cod in codigos:
    codigos_2.append(cod)
cod_tup = tuple(codigos_2)
codigos_tupla = tuple(codigos)

#Funcion para Seleccionar municipios ------------------------------------------------------
def seleccion_municipios(gdb, codigos_tupla, ruta_salida, ORTO):
    arcpy.AddMessage("Procesando municipios")
    arcpy.env.workspace = gdb
    query_prueba = "MpCodigo IN {}".format(codigos_tupla)
    select = arcpy.SelectLayerByAttribute_management('Munpio', "NEW_SELECTION", query_prueba)
    temp = arcpy.management.CopyFeatures (select, os.path.join(ruta_salida, "Mun.shp"))
    arcpy.management.SelectLayerByLocation(ORTO, "INTERSECT", temp)
    intersect = arcpy.management.CopyFeatures(ORTO, os.path.join(str(ruta_salida),'Imagenes_Divipola.shp'))
    return intersect
             

#Funcion para generar reporte ------------------------------------------------------
def Reporte(shp, ruta_salida, codigos_tupla):
    arcpy.AddMessage("Iniciando Reporte")
    espacios = "    "
    ruta_reporte = os.path.join(ruta_salida, 'Reporte de Área de Pendientes.txt')
    #Encabezado
    with open(ruta_reporte, "w") as archivo:
        archivo.write("REPORTE DE ÁREAS DE PENDIENTES\n")
        archivo.write("-----------------------------------------------------\n")
        archivo.write("Código Divipola de los Municipios Analizados {}\n".format(codigos_tupla))
        archivo.write("\n")
        archivo.write("PENDIENTE\t\t\tÁREA\t\t  PORCENTAJE\n")
        
        # Calcula el área efectiva total de todas las entidades en la capa
        total_area = 0
        with arcpy.da.SearchCursor(shp, ["SHAPE@AREA"]) as cursor:
            for row in cursor:
                if Nubes == True:
                    total_area = row[0] + total_area
                    
                else:
                    total_area = row[0] + total_area

        total_area = round((total_area/10000), 2)

        with arcpy.da.SearchCursor(shp, ["gridcode", "SHAPE@AREA"]) as cursor:
            for row in cursor:
                if row[0] == 1:
                    Pendiente1 = round((row[1]/10000), 2)
                    Porcentaje1 = round((Pendiente1/total_area)*100, 2)
                    archivo.write("Pendiente 0-10 %\t" + espacios + str(Pendiente1) + " Hectáreas\t" + espacios + str(Porcentaje1) + " %\n")
                elif row[0] == 2:
                    Pendiente2 = round((row[1]/10000), 2)
                    Porcentaje2 = round((Pendiente2/total_area)*100, 2)
                    archivo.write("Pendiente 10-20 %\t" + espacios + str(Pendiente2) + " Hectáreas\t" + espacios + str(Porcentaje2) + " %\n")
                elif row[0] == 3:
                    Pendiente3 = round((row[1]/10000), 2)
                    Porcentaje3 = round((Pendiente3/total_area)*100, 2)
                    archivo.write("Pendiente 20-35 %\t" + espacios + str(Pendiente3) + " Hectáreas\t" + espacios + str(Porcentaje3) + " %\n")
                elif row[0] == 4:
                    Pendiente4 = round((row[1]/10000), 2)
                    Porcentaje4 = round((Pendiente4/total_area)*100, 2)
                    archivo.write("Pendiente >35 %\t\t" + espacios + str(Pendiente4) + " Hectáreas\t" + espacios + str(Porcentaje4) + " %\n")
                
        # Encuentra el máximo de las variables Pendiente
        max_pendiente = max(Pendiente1, Pendiente2, Pendiente3, Pendiente4)
        archivo.write("\n")
        # Encuentra cuál variable es la mayor
        if max_pendiente == Pendiente1:
            archivo.write("La mayor pendiente es 0-10 % ------ {0} hectáreas.\n".format(str(max_pendiente)))
        elif max_pendiente == Pendiente2:
            archivo.write("La mayor pendiente es 10-20 % ------ {0} hectáreas.\n".format(str(max_pendiente)))
        elif max_pendiente == Pendiente3:
            archivo.write("La mayor pendiente es 20-35 % ------ {0} hectáreas.\n".format(str(max_pendiente)))
        elif max_pendiente == Pendiente4:
            archivo.write("La mayor pendiente es >35 % ------ {0} hectáreas.\n".format(str(max_pendiente)))


select = seleccion_municipios(gdb, cod_tup,ruta_salida,ORTO)
Reporte(select, ruta_salida, codigos_tupla)