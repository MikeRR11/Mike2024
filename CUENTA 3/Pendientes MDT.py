
import arcpy
import os
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
    #Iterador para municipios
    arcpy.AddMessage("Procesando municipios")
    # #Hacer recorte del MDT
    clip_raster= arcpy.management.Clip(MDT, temp, os.path.join(ruta_salida, "Clip.tif"))
    slope = arcpy.sa.Slope(clip_raster, output_measurement = 'PERCENT_RISE', method = 'PLANAR', analysis_target_device = 'GPU_THEN_CPU')
    #slope.save(os.path.join(ruta_salida,"MDT_Slope"))
    return slope

clip(select, MDT, ruta_salida)