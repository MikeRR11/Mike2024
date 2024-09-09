#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico:  Michael Andres Rojas - Diego Rugeles
#09/09/2024
 
import arcpy
from arcpy.sa import *
import os
 
#Llamar municipios y MDT
codigos = arcpy.GetParameter(0)
ruta_salida = arcpy.GetParameterAsText(1)
zona = arcpy.GetParameterAsText(2)
arcpy.env.overwriteOutput = True
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
def Reporte(shp, ruta_salida, codigos_tupla, zona):
    arcpy.AddMessage("Iniciando Reporte")
    ruta_reporte = os.path.join(ruta_salida, 'Reporte de Área de Pendientes.txt')
 
    # Inicializar variables de pendiente y porcentaje
    Pendiente1 = Pendiente2 = Pendiente3 = Pendiente4 = 0
    Porcentaje1 = Porcentaje2 = Porcentaje3 = Porcentaje4 = 0
 
    with open(ruta_reporte, "w") as archivo:
        archivo.write("REPORTE DE ÁREAS DE PENDIENTES\n")
        archivo.write("-----------------------------------------------------\n")
        archivo.write(f"Códigos Divipola Analizados en Área {zona}: {codigos_tupla}\n")
        archivo.write("\n")
        archivo.write("-----------------------------------------------------\n")
        archivo.write("| PENDIENTE        | ÁREA (Hectáreas) | PORCENTAJE  |\n")
        archivo.write("-----------------------------------------------------\n")
        # Calcula el área total de todas las entidades en la capa
        total_area = 0
        with arcpy.da.SearchCursor(shp, ["SHAPE@AREA"]) as cursor:
            for row in cursor:
                total_area += row[0]
 
        total_area = round((total_area / 10000), 2)
 
        # Calcular áreas y porcentajes por pendiente
        with arcpy.da.SearchCursor(shp, ["gridcode", "SHAPE@AREA"]) as cursor:
            for row in cursor:
                area = round((row[1] / 10000), 2)
                if row[0] == 1:
                    Pendiente1 += area
                elif row[0] == 2:
                    Pendiente2 += area
                elif row[0] == 3:
                    Pendiente3 += area
                elif row[0] == 4:
                    Pendiente4 += area
 
        if total_area > 0:
            Porcentaje1 = round((Pendiente1 / total_area) * 100, 2)
            Porcentaje2 = round((Pendiente2 / total_area) * 100, 2)
            Porcentaje3 = round((Pendiente3 / total_area) * 100, 2)
            Porcentaje4 = round((Pendiente4 / total_area) * 100, 2)
 
        # Escribir los valores en el archivo con formato
        archivo.write("| 0 - 10 %         | {:>10}         | {:>7} % |\n".format(Pendiente1, Porcentaje1))
        archivo.write("| 10 - 20 %        | {:>10}         | {:>7} % |\n".format(Pendiente2, Porcentaje2))
        archivo.write("| 20 - 35 %        | {:>10}         | {:>7} % |\n".format(Pendiente3, Porcentaje3))
        archivo.write("| > 35 %           | {:>10}         | {:>7} % |\n".format(Pendiente4, Porcentaje4))
        archivo.write("-----------------------------------------------------\n")
        # Encuentra la mayor pendiente
        max_pendiente = max(Pendiente1, Pendiente2, Pendiente3, Pendiente4)
        archivo.write("\n")
        if max_pendiente == Pendiente1:
            archivo.write("La mayor área de pendiente corresponde a: 0 - 10 % ({0} hectáreas)\n".format(max_pendiente))
        elif max_pendiente == Pendiente2:
            archivo.write("La mayor área de pendiente corresponde a: 10 - 20 % ({0} hectáreas)\n".format(max_pendiente))
        elif max_pendiente == Pendiente3:
            archivo.write("La mayor área de pendiente corresponde a: 20 - 35 % ({0} hectáreas)\n".format(max_pendiente))
        elif max_pendiente == Pendiente4:
            archivo.write("La mayor área de pendiente corresponde a: > 35 % ({0} hectáreas)\n".format(max_pendiente))
 
 
if zona == "Rural":
 
    gdb = r"\\repositorio\DirGesInfGeo\2410SCG\H_Informacion_Consulta\Coberturas\GDB_FLET_Junio_2024.gdb"
    MDT = r"\\repositorio\84RPCartograficos\8MDTerreno\0Mapas\MDE_COLOMBIA_ALOS_PLASAR\MDE12_5_COLOMBIA_ALOS_PALSAR.tif"
 
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
    select = seleccion_municipios(gdb, cod_tup,ruta_salida)
    shp =  clip(select, MDT, ruta_salida)
    Reporte(shp, ruta_salida, codigos_tupla, zona)
    arcpy.Delete_management([select,shp])
else:
    gdb = r"\\repositorio\DirGesInfGeo\2410SCG\H_Informacion_Consulta\Coberturas\Area_Urbana_DANE_Clase1CM_Clase2CP_V2023\MGN_URB_ZONA_URBANA.shp"
    MDT = r"\\repositorio\84RPCartograficos\8MDTerreno\0Mapas\MDE_COLOMBIA_ALOS_PLASAR\MDE12_5_COLOMBIA_ALOS_PALSAR.tif"
 
    codigos_2 = []
    for cod in codigos:
        codigos_2.append(cod)
    cod_tup = tuple(codigos_2)
    codigos_tupla = tuple(codigos)
 
            #Funcion para Seleccionar municipios ------------------------------------------------------
    def seleccion_municipios(gdb, codigos_tupla, ruta_salida):
        arcpy.AddMessage("Procesando municipios")
        arcpy.env.workspace = gdb
        query_prueba = "setr_ccnct IN {}".format(codigos_tupla)
        select = arcpy.SelectLayerByAttribute_management(gdb, "NEW_SELECTION", query_prueba)
        temp = arcpy.management.CopyFeatures (select, os.path.join(ruta_salida, "Mun.shp"))
        return temp     
    select = seleccion_municipios(gdb, cod_tup,ruta_salida)
    shp =  clip(select, MDT, ruta_salida)
    Reporte(shp, ruta_salida, codigos_tupla, zona)
    arcpy.Delete_management([select,shp])