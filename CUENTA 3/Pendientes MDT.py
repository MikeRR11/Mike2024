import arcpy
import os
arcpy.env.overwriteOutput = True
codigos = arcpy.GetParameter(0)
ruta = arcpy.GetParameterAsText(1)
codigos_tupla = tuple(codigos)

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
    MDT = r"C:\Users\yaritza.quevedo\Documents\Asignaciones\MDT_slope\Servicio-8137.tif"
#------------------------------------------------------




#Funcion para Seleccionar municipios
def seleccion_municipios(municipios, codigos_tupla):
    arcpy.env.workspace = municipios
    query = "MpCodigo = '{}'".format(codigos)
    #query_prueba = "MpCodigo in {}".format(codigos_tupla)
    arcpy.AddMessage(query)
    select = arcpy.SelectLayerByAttribute_management('Munpio', "NEW_SELECTION", query)
    return select

select = seleccion_municipios(municipios, codigos)

def clip(select, MDT):
    #Iterador para municipios
    arcpy.AddMessage("Procesando municipios")
    # #Hacer recorte del MDT
    clip_raster = arcpy.ia.Clip(MDT, select)
    clip_raster.save("Clip.tif")

clip(select, MDT)
       