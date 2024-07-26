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
arcpy.management.MakeFeatureLayer(PInicioFin, "PInicioFin_Layer")
arcpy.management.MakeFeatureLayer(Dangles, "Dangles_Layer")

# Selección para encontrar puntos en PInicioFin que no sean también dangles
arcpy.management.SelectLayerByLocation("PInicioFin_Layer", "INTERSECT", "Dangles_Layer", invert_spatial_relationship="NOT_INVERT")
Puntos = "in_memory/Puntos"
arcpy.management.CopyFeatures("PInicioFin_Layer", Puntos)

# 3. Crear nueva capa para puntos de desconexión
ruta_nueva_capa = os.path.join(Ruta_Salida, f"Puntos_Validar_{os.path.basename(Feature).replace('.shp', '')}.shp")
arcpy.CreateFeatureclass_management(os.path.dirname(ruta_nueva_capa), os.path.basename(ruta_nueva_capa), "POINT", spatial_reference=Puntos)

# Insertar puntos de desconexión en la nueva capa
arcpy.AddMessage("Verificando puntos de desconexión")
arcpy.SetProgressor("step", "Verificando puntos de desconexión...", 0, int(arcpy.GetCount_management(Puntos).getOutput(0)), 1)

with arcpy.da.SearchCursor(Puntos, ["OID@", "SHAPE@"]) as Scursor:
    with arcpy.da.InsertCursor(ruta_nueva_capa, ["SHAPE@"]) as Icursor:
        for row in Scursor:
            oid = row[0]
            point = row[1]

            # Si el conteo de intersecciones es mayor a 1, insertar en la nueva capa
            arcpy.management.SelectLayerByLocation(Feature, "INTERSECT", point, search_distance=f"{Buffer} Meters", selection_type="NEW_SELECTION")
            count = int(arcpy.GetCount_management(Feature).getOutput(0))

            if count > 1:
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

# Limpiar la selección
arcpy.management.SelectLayerByAttribute(Feature, "CLEAR_SELECTION")
