import arcpy
from arcpy.sa import *
import os

arcpy.env.overwriteOutput = True
#Llamar municipios y MDT

codigos = arcpy.GetParameter(0)
gdb = r"\\172.26.0.20\Elite_Sub_Geografia_Cartografia\Coberturas\GDB_FLET_Agosto_2023.gdb"
MDT = r"\\172.26.0.20\Elite_Sub_Geografia_Cartografia\MD\Proyectos\SRTM30_Origen_Unico\srtm_30_extend.img"
ruta_salida = arcpy.GetParameterAsText(1)
codigos_2 = []
for cod in codigos:
    codigos_2.append(cod)
cod_tup = tuple(codigos_2)
codigos_tupla = tuple(codigos)

#Funcion para Seleccionar municipios ------------------------------------------------------
def seleccion_municipios(gdb, codigos_tupla, ruta_salida):
    arcpy.AddMessage("Procesando municipios")
    arcpy.env.workspace = gdb
    query_prueba = "MpCodigo IN {}".format(codigos_tupla)
    select = arcpy.SelectLayerByAttribute_management('Munpio', "NEW_SELECTION", query_prueba)
    temp = arcpy.management.CopyFeatures (select, os.path.join(ruta_salida, "Mun.shp"))
    return temp      
             
#Funcion para clasificar pendientes ------------------------------------------------------
def clip(temp, MDT, ruta_salida):
    arcpy.AddMessage("Iniciando Clasificación")
    arcpy.env.workspace = ruta_salida
    #Iterador para municipios
    #Hacer recorte del MDT
    clip_raster = arcpy.management.Clip(MDT, temp, os.path.join(ruta_salida, "Clip.tif"), in_template_dataset=temp, clipping_geometry=True, maintain_clipping_extent="MAINTAIN_EXTENT")
    slope = arcpy.sa.Slope(clip_raster, output_measurement='PERCENT_RISE', method='PLANAR', analysis_target_device='GPU_THEN_CPU')
    slope.save(os.path.join(ruta_salida, "MDT_Slope.tif"))
    myRemapRange = RemapRange([[0, 10, 1], [10, 20, 2], [20, 35, 3], [35, 999999999999999, 4]])
    OutReclass = Reclassify(slope, "VALUE", myRemapRange)
    OutReclass.save(os.path.join(ruta_salida, "MDT_Reclass.tif"))
    arcpy.AddMessage("Clasificación Exitosa")
    shp = arcpy.conversion.RasterToPolygon(OutReclass, os.path.join(ruta_salida, "MDT_Shape.shp"), "NO_SIMPLIFY", "VALUE", "MULTIPLE_OUTER_PART")
    arcpy.Delete_management([OutReclass,slope,clip_raster])
    return shp

#Funcion para generar reporte ------------------------------------------------------
def Reporte(shp, ruta_salida, codigos_tupla):
    arcpy.AddMessage("Iniciando Reporte")
    espacios = "    "
    ruta_reporte = os.path.join(ruta_salida, 'Reporte de Área de Pendientes.txt')
    with open(ruta_reporte, "w") as archivo:
        archivo.write("REPORTE DE ÁREAS DE PENDIENTES\n")
        archivo.write("-----------------------------------------------------\n")
        archivo.write("Código Divipola de los Municipios Analizados {}\n".format(codigos_tupla))
        archivo.write("\n")
        archivo.write("PENDIENTE\t\t\tÁREA\t\t  PORCENTAJE\n")
        
        # Calcula el área total de todas las entidades en la capa
        total_area = 0
        with arcpy.da.SearchCursor(shp, ["SHAPE@AREA"]) as cursor:
            for row in cursor:
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
        
select = seleccion_municipios(gdb, cod_tup,ruta_salida)
shp =  clip(select, MDT, ruta_salida)
Reporte(shp, ruta_salida, codigos_tupla)
arcpy.Delete_management([select,shp])
