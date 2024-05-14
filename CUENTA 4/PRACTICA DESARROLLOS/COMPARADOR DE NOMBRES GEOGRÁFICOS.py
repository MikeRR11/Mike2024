#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Diego Rugeles - Michael Rojas
import arcpy
import os

# Parámetros de entrada
Puntos1 = arcpy.GetParameterAsText(0)
Puntos2 = arcpy.GetParameterAsText(1)
Buffer = arcpy.GetParameterAsText(2)
Ruta_Salida = arcpy.GetParameterAsText(3)

#Se requiere comparar dos feature dataset de geometria tipo punto, los cuales contienen nombres 
#geograficos en uno de sus campos, se tienen que relacionar los puntos de ambos features para determinar su semejanza en al menos un 80%, en un radio de busqueda
#dinamico
#Libreria Rapid Fuzz
