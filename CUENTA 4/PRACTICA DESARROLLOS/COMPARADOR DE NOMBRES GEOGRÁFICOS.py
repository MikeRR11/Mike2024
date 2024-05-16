#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Diego Rugeles - Michael Rojas
import arcpy 
import os

#Parámetros de entrada
Puntos1 = arcpy.GetParameterAsText(0)
Puntos2 = arcpy.GetParameterAsText(1)
Buffer_Dist = arcpy.GetParameterAsText(2)
Ruta_Salida = arcpy.GetParameterAsText(3)

#Se requiere comparar dos feature dataset de geometria tipo punto, los cuales contienen nombres 
#geograficos en uno de sus campos, se tienen que relacionar los puntos de ambos features para determinar su semejanza en al menos un 80%, en un radio de busqueda
#dinamico, al final exportar una capa de puntos quew contenga los datos con semejanza mayor al 80%

#Libreria Rapid Fuzz

# Campo que contiene los nombres geográficos
campo_nombre = "NGNPrincip"  # Cambiar según el nombre del campo en tus datasets

# Crear un buffer alrededor de Puntos1
Buffer = arcpy.Buffer_analysis(Puntos1, os.path.join(str(Ruta_Salida), "Buffer.shp"), Buffer_Dist)

arcpy.SpatialJoin_analysis(Puntos2, buffers, puntos_cercanos, "JOIN_ONE_TO_MANY", "KEEP_COMMON")


