#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Michael Rojas
import arcpy
from arcpy.sa import *
import os
import math

arcpy.env.overwriteOutput = True
#Llamar municipios elite

# gdb = r"\\172.26.0.20\Elite_Sub_Geografia_Cartografia\Coberturas\GDB_FLET_Agosto_2023.gdb"
gdb = r"C:\Users\michael.rojas\Documents\CUENTA3\PENDIENTESMDT\Municipios_Agosto_2023.gdb\Limites_Entidades_Territoriales\Munpio"

codigos = arcpy.GetParameter(0) #Ingreso codigos Divipola
ORTO = arcpy.GetParameterAsText(1) #Imagenes de Entrada
Limite = arcpy.GetParameterAsText(2) #Límite del proyecto
ruta_salida = arcpy.GetParameterAsText(3) # Ruta Salida
Factor = arcpy.GetParameterAsText(4) #Incluir factor
Nubes = arcpy.GetParameterAsText(5) #Incluir Nubes
Lim = arcpy.GetParameterAsText(6) #Usar límite del proyecto


codigos_2 = []
for cod in codigos:
    codigos_2.append(cod)
cod_tup = tuple(codigos_2)
codigos_tupla = tuple(codigos)

#Funcion para Seleccionar municipios ------------------------------------------------------

def seleccion_municipios(gdb, codigos_tupla, ruta_salida, ORTO, Limite,Lim):
    if Lim == "true":
        arcpy.AddMessage("Procesando municipios con Límite del proyecto")
        arcpy.management.SelectLayerByLocation(ORTO, "INTERSECT", Limite)
        intersect = arcpy.management.CopyFeatures(ORTO, os.path.join(str(ruta_salida),'Imagenes_Divipola.shp'))
        return {'intersect': intersect, 'area_munpi': 0}
    else:
        arcpy.AddMessage("Procesando municipios con códigos Divipola")
        arcpy.env.workspace = gdb
        query_prueba = "MpCodigo IN {}".format(codigos_tupla)
        select = arcpy.SelectLayerByAttribute_management('Munpio', "NEW_SELECTION", query_prueba)
        temp = arcpy.management.CopyFeatures (select, os.path.join(ruta_salida, "Mun.shp"))
        global area_munpi
        area_munpi = 0
        with arcpy.da.SearchCursor(temp, ["SHAPE@AREA"]) as cursor:
            for row in cursor:
                    area_munpi = row[0] + area_munpi
                    
        area_munpi = round((area_munpi/10000), 2)
        arcpy.management.SelectLayerByLocation(ORTO, "INTERSECT", temp)
        intersect = arcpy.management.CopyFeatures(ORTO, os.path.join(str(ruta_salida),'Imagenes_Divipola.shp'))
        arcpy.Delete_management(temp)
        return {'intersect': intersect, 'area_munpi': area_munpi} # Devuelve un diccionario con intersect y area_munpi
             

#Funcion para generar reporte ------------------------------------------------------
def Reporte(shp, ruta_salida, codigos_tupla, ORTO, Limite, Lim, area_munpi):
    arcpy.AddMessage("Iniciando Reporte")
    espacios = "    "
    ruta_reporte = os.path.join(ruta_salida, 'Reporte de Áreas Evaluación de Imágenes.txt')
    with open(ruta_reporte, "w") as archivo:
        #Encabezado
        archivo.write("REPORTE DE ÁREAS IMGÁGENES DIVIPOLA\n")
        archivo.write("-----------------------------------------------------\n")

        if Lim == "false":
            desc = arcpy.Describe(ORTO)
            gdb_ruta = desc.path
            gdb_nombre = os.path.basename(gdb_ruta)  # Obtener solo el nombre de la GDB
            archivo.write("Código Divipola de los Municipios Analizados {}\n".format(codigos_tupla))
        else:
            desc = arcpy.Describe(Limite)
            gdb_nombre = desc.Name  # Obtener solo el nombre del Limite del proyecto
    
        archivo.write("PROYECTO: " + gdb_nombre + "\n")
        total_area = 0
        with arcpy.da.SearchCursor(shp, ["SHAPE@AREA"]) as cursor:
            for row in cursor:
                    total_area = row[0] + total_area

        total_area = round((total_area/10000), 2)
        archivo.write("\n")
        archivo.write("COBERTURA\tÁREA\t\tPORCENTAJE\n")
        # Calcula el área efectiva total de todas las entidades en la capa


        
        with arcpy.da.SearchCursor(shp, ["COBERTURA", "SHAPE@AREA"]) as cursor:
            area1 = 0
            area2 = 0
            area3 = 0
            area4 = 0
            area5 = 0
            for row in cursor:
                if row[0] == "1":
                    area1 = round(area1 + (row[1]/10000), 2)
                    Porcentaje1 = round((area1/total_area)*100, 2)
                elif row[0] == "2":
                    area2 = round(area2 + (row[1]/10000), 2)
                    Porcentaje2 = round((area2/total_area)*100, 2)
                elif row[0] == "3":
                    area3 = round(area3 + (row[1]/10000), 2)
                    Porcentaje3 = round((area3/total_area)*100, 2)
                elif row[0] == "4":
                    area4 = round(area4 + (row[1]/10000), 2)
                    Porcentaje4 = round((area4/total_area)*100, 2)
                elif row[0] == "5":
                    area5 = round(area5 + (row[1]/10000), 2)
                    Porcentaje5 = round((area5/total_area)*100, 2)

            if area1 > 0:
                archivo.write("HUELLA\t" + espacios + str(area1) + " Hectáreas\t" + espacios + str(Porcentaje1) + " %\n")
            else:
                pass
            if area2 > 0:
                archivo.write("NUBE\t" + espacios + str(area2) + " Hectáreas\t" + espacios + str(Porcentaje2) + " %\n")
            else:
                pass
            if area3 > 0:
                archivo.write("SOMBRA\t" + espacios + str(area3) + " Hectáreas\t" + espacios + str(Porcentaje3) + " %\n")
            else:
                pass
            if area4 > 0:
                archivo.write("SIN DATO\t" + espacios + str(area4) + " Hectáreas\t" + espacios + str(Porcentaje4) + " %\n")
            else:
                pass
            if area5 > 0:
                archivo.write("BRUMA\t" + espacios + str(area5) + " Hectáreas\t" + espacios + str(Porcentaje5) + " %\n")
            else:
                pass
        

        # sumar todas las areas
        archivo.write("\n")
        archivo.write("\n")
        n = str(arcpy.management.GetCount(shp))
        archivo.write("NÚMERO DE IMÁGENES = " + str(n)+"\n")
        if Nubes == "true":
            total_area1 = 0
            archivo.write("-Área Efectiva Excluyendo Sombras y Nubes-"+"\n")
            SQL1 = "Cobertura NOT IN ('2', '3')"
            with arcpy.da.SearchCursor(shp, ["SHAPE@AREA"],SQL1) as cursor:
                for row in cursor:
                        total_area1 = row[0] + total_area1
            total_area1 = round((total_area1/10000), 2)
            archivo.write("\n")
            archivo.write("ÁREA TOTAL EFECTIVA DE IMÁGENES = " + str(total_area1)+ " HECTÁREAS"+"\n")
            # sacar prom area imagenes
            prom = round(total_area1/float(n),2)
            archivo.write("ÁREA PROMEDIO DE IMÁGENES = " + str(prom)+ " HECTÁREAS"+"\n")
            #Factor usuario pórcentaje
            afactor = round((prom*(1-(float(Factor)/100))),2)
            archivo.write("ÁREA PROMEDIO DE IMÁGENES CON REDUCCIÓN DEL " + str(Factor) + " % = "  + str(afactor)+ " HECTÁREAS"+"\n")
            if Lim == "true":
                #Cantidad de imagenes
                area_lim = 0
                with arcpy.da.SearchCursor(Limite, ["SHAPE@AREA"]) as cursor:
                    for row in cursor:
                            area_lim = row[0] + area_lim
                area_lim = round((area_lim/10000), 2)
                archivo.write("ÁREA PROYECTO = " + str(area_lim)+ " HECTÁREAS"+"\n")           
                nimagenes = math.ceil(area_lim/afactor)
                archivo.write("CANTIDAD DE IMÁGENES PROMEDIO EN EL PROYECTO = " + str(nimagenes) +"\n")
            else:
                #Cantidad de imagenes
                archivo.write("ÁREA MUNICIPIOS = " + str(area_munpi)+ " HECTÁREAS"+"\n")           
                nimagenes = math.ceil(area_munpi/afactor)
                archivo.write("CANTIDAD DE IMÁGENES PROMEDIO EN LOS MUNICIPIOS = " + str(nimagenes) +"\n")

        else:
            archivo.write("ÁREA TOTAL EFECTIVA DE IMÁGENES = " + str(total_area)+ " HECTÁREAS"+"\n")
            # sacar prom area imagenes
            prom = round(total_area/float(n),2)
            archivo.write("ÁREA PROMEDIO DE IMÁGENES = " + str(prom)+ " HECTÁREAS"+"\n")
            #Factor usuario pórcentaje
            afactor = round((prom*(1-(float(Factor)/100))),2)
            archivo.write("ÁREA PROMEDIO DE IMÁGENES CON REDUCCIÓN DEL " + str(Factor) + " % = "  + str(afactor)+ " HECTÁREAS"+"\n")
            if Lim == "true":
                #Cantidad de imagenes
                area_lim = 0
                with arcpy.da.SearchCursor(Limite, ["SHAPE@AREA"]) as cursor:
                    for row in cursor:
                            area_lim = row[0] + area_lim
                area_lim = round((area_lim/10000), 2)
                archivo.write("ÁREA PROYECTO = " + str(area_lim)+ " HECTÁREAS"+"\n")           
                nimagenes = math.ceil(area_lim/afactor)
                archivo.write("CANTIDAD DE IMÁGENES PROMEDIO EN EL PROYECTO = " + str(nimagenes) +"\n")
            else:
                #Cantidad de imagenes
                archivo.write("ÁREA MUNICIPIOS = " + str(area_munpi)+ " HECTÁREAS"+"\n")           
                nimagenes = math.ceil(area_lim/afactor)
                archivo.write("CANTIDAD DE IMÁGENES PROMEDIO EN LOS MUNICIPIOS = " + str(nimagenes) +"\n")

select = seleccion_municipios(gdb, cod_tup,ruta_salida,ORTO, Limite, Lim)
Reporte(select['intersect'], ruta_salida, codigos_tupla, ORTO, Limite, Lim, select['area_munpi'])
arcpy.Delete_management(select['intersect'])
arcpy.AddMessage("Reporte generado con éxito")