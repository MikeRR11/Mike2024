import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
shp = arcpy.GetParameterAsText(0)
xlx = arcpy.GetParameterAsText(1)
Ruta_Salida = arcpy.GetParameterAsText(2)
zona = arcpy.GetParameterAsText(3)

# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage("  ")

arcpy.AddMessage(f"Cálculando parametros para zona {zona}.")


