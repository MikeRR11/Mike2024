import arcpy
import os

# Parámetros de entrada
Feature = arcpy.GetParameterAsText(0)
Ruta_Salida = arcpy.GetParameterAsText(1)
Buffer = arcpy.GetParameterAsText(2)

arcpy.env.overwriteOutput = True
arcpy.AddMessage("INICIANDO PROCESO")
arcpy.AddMessage(f"Validando feature class {os.path.basename(Feature)} con distancia de busqueda de {Buffer} metros")

# 1. Crear puntos en vértices de inicio y final, y dangles
arcpy.AddMessage("Generando puntos de dangles y extremos")
Dangles = arcpy.FeatureVerticesToPoints_management(Feature, "in_memory/Dangles", "DANGLE")
PInicioFin = arcpy.FeatureVerticesToPoints_management(Feature, "in_memory/PInicioFin", "BOTH_ENDS")

# 2. Filtrar y mantener solo los puntos con "dangle"
arcpy.AddMessage("Descartando Puntos")
arcpy.management.MakeFeatureLayer(PInicioFin, "PInicioFin_Layer")
arcpy.management.MakeFeatureLayer(Dangles, "Dangles_Layer")
arcpy.management.SelectLayerByLocation("PInicioFin_Layer", "INTERSECT", "Dangles_Layer")
Puntos = "in_memory/Puntos"
arcpy.management.CopyFeatures("PInicioFin_Layer", Puntos)

# 3. Crear nueva capa para puntos de desconexión
ruta_nueva_capa = os.path.join(Ruta_Salida, "Puntos_Desconexion_" + os.path.basename(Feature) + ".shp")
arcpy.CreateFeatureclass_management(os.path.dirname(ruta_nueva_capa), os.path.basename(ruta_nueva_capa), "POINT", spatial_reference=Puntos)

# Almacenar puntos de desconexión
arcpy.AddMessage("Identificando puntos de desconexión")
with arcpy.da.SearchCursor(Puntos, ["SHAPE@"]) as Scursor:
    with arcpy.da.InsertCursor(ruta_nueva_capa, ["SHAPE@"]) as Icursor:
        for punto in Scursor:
            # Seleccionar líneas que intersectan con el punto actual
            arcpy.management.SelectLayerByLocation(Feature, "INTERSECT", punto[0], search_distance=str(Buffer) + ' Meters')
            count = int(arcpy.GetCount_management(Feature).getOutput(0))
            if count > 1:
                Icursor.insertRow([punto[0]])

# Mensaje final con el número de puntos desconectados
arcpy.AddMessage(f"Se han detectado {arcpy.GetCount_management(ruta_nueva_capa).getOutput(0)} puntos desconectados en el feature class {os.path.basename(Feature)}")
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO.")

# Liberar recursos
arcpy.Delete_management("in_memory/Dangles")
arcpy.Delete_management("in_memory/PInicioFin")
arcpy.Delete_management("PInicioFin_Layer")
arcpy.Delete_management("Dangles_Layer")
arcpy.Delete_management(Puntos)
