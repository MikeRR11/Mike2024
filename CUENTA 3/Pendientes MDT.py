
import arcpy
import os
from arcpy.sa import *

arcpy.env.overwriteOutput = True
codigos = arcpy.GetParameter(0)
ruta = arcpy.GetParameterAsText(1)
gdb = arcpy.GetParameterAsText(2)
ruta_salida = arcpy.GetParameterAsText(3)
MDT = arcpy.GetParameterAsText(4)
codigos_2 = []
for cod in codigos:
    codigos_2.append(cod)

cod_tup = tuple(codigos_2)

codigos_tupla = tuple(codigos)
arcpy.AddMessage(codigos_tupla)
arcpy.AddMessage(type(codigos_tupla))

arcpy.env.overwriteOutput = True

#Llamar municipios y MDT

# municipios = r"\\172.26.0.20\Elite_Sub_Geografia_Cartografia\Coberturas\GDB_FLET_Agosto_2023.gdb\Limites_Entidades_Territoriales\Munpio"
# MDT = r""

#-----------------------------------------------------

if ruta == True:
    municipios = r"C:\Users\michael.rojas\Documents\CUENTA3\PENDIENTESMDT\Municipios_Agosto_2023.gdb\Limites_Entidades_Territoriales\Munpio"
    arcpy.AddMessage(municipios)
    MDT = r"C:\Users\michael.rojas\Documents\CUENTA 3\PENDIENTES MDT\SRTM30\SRTM_30_Col1.tif"


else:
    municipios = r"C:\Users\yaritza.quevedo\Documents\Asignaciones\MDT_slope\Municipios_Agosto_2023.gdb\Limites_Entidades_Territoriales\Munpio"
    #MDT = r"C:\Users\yaritza.quevedo\Documents\Asignaciones\MDT_slope\Servicio-8137.tif"
#------------------------------------------------------


#Funcion para Seleccionar municipios
def seleccion_municipios(gdb, codigos_tupla, ruta_salida):
    arcpy.env.workspace = gdb
    #query = "MpCodigo = '{}'".format(codigos)
    query_prueba = "MpCodigo IN {}".format(codigos_tupla)
    arcpy.AddMessage(query_prueba)
    select = arcpy.SelectLayerByAttribute_management('Munpio', "NEW_SELECTION", query_prueba)
    temp = arcpy.management.CopyFeatures (select, os.path.join(ruta_salida, "Mun.shp"))
    return temp                          

select = seleccion_municipios(municipios, cod_tup,ruta_salida)

                  

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
    return shp

def Reporte(shp, ruta_salida, codigos_tupla):
    arcpy.AddMessage("Iniciando Reporte")
    espacios = "    "
    ruta_reporte = os.path.join(ruta_salida, 'Reporte de Área de Pendientes.txt')
    with open(ruta_reporte, "w") as archivo:
        archivo.write("REPORTE DE ÁREAS DE PENDIENTES\n")
        archivo.write("-----------------------------------------------------\n")
        archivo.write("PENDIENTE \t\tÁREA\t\tPORCENTAJE\n")
        archivo.write("Código Divipola de los Municipios Analizados {}\n".format(codigos_tupla))

        # Calcula el área total de todas las entidades en la capa
        Total_area = 0
        with arcpy.da.SearchCursor(shp, ["SHAPE@AREA"]) as cursor:
            for row in cursor:
                total_area = row[0] + Total_area

        Total_area = round((total_area/10000), 2)
        
        with arcpy.da.SearchCursor(shp, ["gridcode", "SHAPE@AREA"]) as cursor:
            for row in cursor:
                Total_area += row[1]
                if row[0] == 1:
                    Pendiente1 = round((row[1]/10000), 2)
                    Porcentaje1 = round((Pendiente1/Total_area)*100, 2)
                    archivo.write("Pendiente 0-10 %\t" + espacios + str(Pendiente1) + " Hectáreas\t" + espacios + str(Porcentaje1) + " %\n")
                elif row[0] == 2:
                    Pendiente2 = round((row[1]/10000), 2)
                    Porcentaje2 = round((Pendiente2/Total_area)*100, 2)
                    archivo.write("Pendiente 10-20 %\t" + espacios + str(Pendiente2) + " Hectáreas\t" + espacios + str(Porcentaje2) + " %\n")
                elif row[0] == 3:
                    Pendiente3 = round((row[1]/10000), 2)
                    Porcentaje3 = round((Pendiente3/Total_area)*100, 2)
                    archivo.write("Pendiente 20-35 %\t" + espacios + str(Pendiente3) + " Hectáreas\t" + espacios + str(Porcentaje3) + " %\n")
                elif row[0] == 4:
                    Pendiente4 = round((row[1]/10000), 2)
                    Porcentaje4 = round((Pendiente4/Total_area)*100, 2)
                    archivo.write("Pendiente >35 %\t\t" + espacios + str(Pendiente4) + " Hectáreas\t" + espacios + str(Porcentaje4) + " %\n")
                
        # Encuentra el máximo de las variables Pendiente
        max_pendiente = max(Pendiente1, Pendiente2, Pendiente3, Pendiente4)
        # Encuentra cuál variable es la mayor
        if max_pendiente == Pendiente1:
            archivo.write("La mayor pendiente es 0-10 % ------ {0} hectáreas.\n".format(str(max_pendiente)))
        elif max_pendiente == Pendiente2:
            archivo.write("La mayor pendiente es 10-20 % ------ {0} hectáreas.\n".format(str(max_pendiente)))
        elif max_pendiente == Pendiente3:
            archivo.write("La mayor pendiente es 20-35 % ------ {0} hectáreas.\n".format(str(max_pendiente)))
        elif max_pendiente == Pendiente4:
            archivo.write("La mayor pendiente es >35 % ------ {0} hectáreas.\n".format(str(max_pendiente)))
            archivo.close()
   


select = seleccion_municipios(gdb, cod_tup,ruta_salida)
shp =  clip(select, MDT, ruta_salida)
Reporte(shp, ruta_salida,codigos_tupla)