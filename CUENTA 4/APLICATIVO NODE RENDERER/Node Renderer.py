#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Diego Rugeles - Michael Rojas
import arcpy
import os

# Parámetros de entrada
Feature = arcpy.GetParameterAsText(0)
Ruta_Salida = arcpy.GetParameterAsText(1)
nombre_feature = os.path.basename(Feature)

arcpy.env.overwriteOutput = True
arcpy.env.workspace = Feature
arcpy.AddMessage("INICIANDO PROCESO")

#1 HACER CAPA DE PUNTOS DE INICIO Y FINAL
PInicioFin = arcpy.FeatureVerticesToPoints_management(Feature,os.path.join(str(Ruta_Salida),'PInicioFin.shp'), "BOTH_ENDS")
collect = arcpy.stats.CollectEvents(PInicioFin, os.path.join(str(Ruta_Salida),'collect.shp'))
Select = arcpy.management.SelectLayerByAttribute(collect, 'NEW_SELECTION', "ICOUNT >= 3")

nombre_salida = nombre_feature + '_Node_Renderer.shp'
Puntos = arcpy.management.CopyFeatures(Select, os.path.join(str(Ruta_Salida), nombre_salida))

# Imprimir un mensaje con el número de puntos insertados
arcpy.AddMessage(f"Se han detectado {arcpy.GetCount_management(Puntos)} puntos con 3 o más conexiones")

# Finalizar con un mensaje de éxito
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO.")
arcpy.Delete_management(PInicioFin)
arcpy.Delete_management(collect)