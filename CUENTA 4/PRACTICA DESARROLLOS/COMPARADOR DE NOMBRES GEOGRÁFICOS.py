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
campo_nombre = "Nombre_Geografico"  # Cambiar según el nombre del campo en tus datasets

# Crear un buffer alrededor de Puntos1
buffers = os.path.join("in_memory", "buffers")
arcpy.Buffer_analysis(Puntos1, buffers, Buffer_Dist)

# Seleccionar los puntos de Puntos2 que están dentro de los buffers
puntos_cercanos = os.path.join("in_memory", "puntos_cercanos")
arcpy.SpatialJoin_analysis(Puntos2, buffers, puntos_cercanos, "JOIN_ONE_TO_MANY", "KEEP_COMMON")

# Crear una tabla para los resultados
arcpy.CreateTable_management(Ruta_Salida, "resultados")
tabla_resultados = os.path.join(Ruta_Salida, "resultados")
arcpy.AddField_management(tabla_resultados, "Punto1_ID", "LONG")
arcpy.AddField_management(tabla_resultados, "Punto2_ID", "LONG")
arcpy.AddField_management(tabla_resultados, "Similaridad", "DOUBLE")

# Crear una feature class para los puntos que cumplen con el criterio de similitud
output_feature_class = os.path.join(Ruta_Salida, "Puntos_Semejanza_80")
arcpy.CreateFeatureclass_management(Ruta_Salida, "Puntos_Semejanza_80", "POINT", Puntos1)
arcpy.AddField_management(output_feature_class, "Punto2_ID", "LONG")
arcpy.AddField_management(output_feature_class, "Similaridad", "DOUBLE")

# Obtener cursores de los puntos originales y los puntos cercanos
resultados = []
with arcpy.da.SearchCursor(Puntos1, ["OID@", "SHAPE@", campo_nombre]) as cursor1:
    for row1 in cursor1:
        punto1_id, shape1, nombre1 = row1
        with arcpy.da.SearchCursor(puntos_cercanos, ["TARGET_FID", campo_nombre]) as cursor2:
            for row2 in cursor2:
                punto2_id, nombre2 = row2
                if punto1_id == row2[0]:  # Verificar si el punto en Puntos2 está dentro del buffer de Puntos1
                    similaridad = fuzz.ratio(nombre1, nombre2)
                    if similaridad >= 80:
                        resultados.append((punto1_id, shape1, punto2_id, similaridad))
            cursor2.reset()

# Insertar los resultados en la tabla de resultados y en la feature class de salida
with arcpy.da.InsertCursor(tabla_resultados, ["Punto1_ID", "Punto2_ID", "Similaridad"]) as cursor_table, \
     arcpy.da.InsertCursor(output_feature_class, ["SHAPE@", "Punto2_ID", "Similaridad"]) as cursor_fc:
    for resultado in resultados:
        punto1_id, shape1, punto2_id, similaridad = resultado
        cursor_table.insertRow((punto1_id, punto2_id, similaridad))
        cursor_fc.insertRow((shape1, punto2_id, similaridad))

arcpy.AddMessage(f"Proceso completado. Resultados guardados en {tabla_resultados} y {output_feature_class}")
