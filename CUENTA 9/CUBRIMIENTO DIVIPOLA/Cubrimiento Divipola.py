import arcpy
import os

# Configuración de entorno
arcpy.env.overwriteOutput = True

# Parámetros de entrada desde la toolbox
Munpi = arcpy.GetParameterAsText(0)  # Entrada de features desde toolbox
features = arcpy.GetParameterAsText(1)  # Campo para clasificar
ruta_salida = arcpy.GetParameterAsText(2)  # Ruta de salida para los resultados
espacio = ".                                                                   ."
espacio2 = "-------------------------------------------------------------------------------------------------------"

# Validación de entradas
if not os.path.exists(ruta_salida):
    arcpy.AddError(f"La ruta de salida no existe: {ruta_salida}")
    raise ValueError("Ruta de salida inválida")

# Procesamiento de los shapes de puntos originales
if features:
    features_Lista = [rel.strip() for rel in features.split(";")]  # Se dejan en una lista separados por punto y coma las rutas
else:
    arcpy.AddError("No se ha proporcionado ninguna capa de entrada.")
    raise ValueError("No se han proporcionado features de entrada")

# Crear una Geodatabase temporal para almacenar los resultados
nombre_gdb = f"Cubrimiento_Munpi.gdb"
gdb_temporal = os.path.join(ruta_salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb_temporal}")
arcpy.CreateFileGDB_management(ruta_salida, nombre_gdb)

def curbrimiento(Munpi, features, gdb_temporal):
    


for feature in features_Lista:
    curbrimiento(Munpi, features, gdb_temporal)

arcpy.AddMessage(espacio2)
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO")
