import arcpy
import os

shp_limite = arcpy.GetParameterAsText(3)
escala = arcpy.GetParameterAsText(4)
ruta_salida = arcpy.GetParameterAsText(5)
