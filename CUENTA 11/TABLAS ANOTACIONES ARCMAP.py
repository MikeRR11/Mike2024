import arcpy 
import os

#Feature clas

anotacion = arcpy.GetParameterAsText(0)
Ruta_Salida = arcpy.GetParameterAsText(1)

arcpy.AddMessage("INICIANDO PROCESO")

#with arcpy.SearchCursor(anotacion, [])

