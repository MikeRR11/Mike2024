import arcpy
import os

# Parámetros de entrada
Feature = arcpy.GetParameterAsText(0)
Ruta_Salida = arcpy.GetParameterAsText(1)
Buffer = arcpy.GetParameterAsText(2)

arcpy.env.overwriteOutput = True
arcpy.AddMessage("INICIANDO PROCESO")
arcpy.AddMessage(f"Validando feature class {os.path.basename(Feature)} con distancia de búsqueda de {Buffer} metros")

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

# Crear un diccionario para almacenar los conteos de intersección
arcpy.AddMessage("Calculando intersecciones")
intersections_dict = {}

# Establecer el progresor de barra
num_puntos = int(arcpy.GetCount_management(Puntos).getOutput(0))
arcpy.SetProgressor("step", "Procesando puntos de desconexión...", 0, num_puntos, 1)

# Almacenar puntos de desconexión
with arcpy.da.SearchCursor(Puntos, ["OID@", "SHAPE@"]) as Scursor:
    for row in Scursor:
        oid = row[0]
        point = row[1]

        # Seleccionar líneas que intersectan con el punto actual
        arcpy.management.SelectLayerByLocation(Feature, "INTERSECT", point, search_distance=f"{Buffer} Meters")
        count = int(arcpy.GetCount_management(Feature).getOutput(0))
        intersections_dict[oid] = count

        # Actualizar el progreso
        arcpy.SetProgressorPosition()

# 3. Crear nueva capa para puntos de desconexión
ruta_nueva_capa = os.path.join(Ruta_Salida, "Puntos_Desconexion_" + os.path.basename(Feature) + ".shp")
arcpy.CreateFeatureclass_management(os.path.dirname(ruta_nueva_capa), os.path.basename(ruta_nueva_capa), "POINT", spatial_reference=Puntos)

# Insertar puntos de desconexión en la nueva capa
arcpy.SetProgressor("step", "Insertando puntos de desconexión...", 0, num_puntos, 1)
with arcpy.da.SearchCursor(Puntos, ["OID@", "SHAPE@"]) as Scursor:
    with arcpy.da.InsertCursor(ruta_nueva_capa, ["SHAPE@"]) as Icursor:
        for row in Scursor:
            oid = row[0]
            point = row[1]

            # Si el conteo de intersecciones es mayor a 1, insertar en la nueva capa
            if intersections_dict[oid] > 1:
                Icursor.insertRow([point])

            # Actualizar el progreso
            arcpy.SetProgressorPosition()

# Mensaje final con el número de puntos desconectados
arcpy.AddMessage(f"Se han detectado {arcpy.GetCount_management(ruta_nueva_capa).getOutput(0)} puntos desconectados en el feature class {os.path.basename(Feature)}")
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO.")

# Liberar recursos
arcpy.Delete_management("in_memory/Dangles")
arcpy.Delete_management("in_memory/PInicioFin")
arcpy.Delete_management("PInicioFin_Layer")
arcpy.Delete_management("Dangles_Layer")
arcpy.Delete_management(Puntos)
