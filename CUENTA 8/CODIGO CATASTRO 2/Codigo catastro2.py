#Desarrollo Transferencia de Datos Catastrales
#Desarrollado por : Michael Andres Rojas Rivera y Yaritza Dorely Quevedo Tovar
#Actualizado V2 13/09/2024
#Descripción: Script para la migración y transferencia de datos de una capa LADM a una base de datos con vacios de información catastral.

import arcpy
import os

# Parámetros de entrada
Base_Catastral = arcpy.GetParameterAsText(0)
Base_Vectorizada = arcpy.GetParameterAsText(1)
Ruta_Salida = os.path.dirname(Base_Catastral)

arcpy.env.overwriteOutput = True

# Convertir Base_Catastral a puntos conservando la información
featuretopoint = arcpy.management.FeatureToPoint(Base_Catastral, os.path.join(Ruta_Salida, 'Base_Catastral_Point'), "INSIDE")

# Asegurar la existencia de campos en Base_Vectorizada
fields_to_add = [("CODIGO", "TEXT"), ("CODIGO_ANT", "TEXT")]
existing_fields = [f.name for f in arcpy.ListFields(Base_Vectorizada)]
for field_name, field_type in fields_to_add:
    if field_name not in existing_fields:
        arcpy.management.AddField(Base_Vectorizada, field_name, field_type)
        arcpy.AddMessage(f"Campo '{field_name}' añadido a la capa de destino.")

# Crear una capa temporal para Base_Vectorizada
Base_Vectorizada_Layer = "Base_Vectorizada_Layer"
arcpy.MakeFeatureLayer_management(Base_Vectorizada, Base_Vectorizada_Layer)
arcpy.AddMessage("Capa temporal 'Base_Vectorizada_Layer' creada.")

arcpy.AddMessage("Procesando puntos y transfiriendo datos")

# Crear un diccionario para contar puntos por polígono
polygon_point_counts = {}

# Iterar sobre los puntos en featuretopoint
with arcpy.da.SearchCursor(featuretopoint, ["SHAPE@", "CODIGO", "CODIGO_ANT"]) as point_cursor:
    for point in point_cursor:
        # Realizar la selección por localización para encontrar el polígono correspondiente
        arcpy.management.SelectLayerByLocation(Base_Vectorizada_Layer, "CONTAINS", point[0])
        with arcpy.da.SearchCursor(Base_Vectorizada_Layer, ["OID@", "SHAPE@", "CODIGO", "CODIGO_ANT"]) as polygon_cursor:
            for polygon in polygon_cursor:
                polygon_id = polygon[0]
                # Inicializar o incrementar el contador de puntos para el polígono
                if polygon_id in polygon_point_counts:
                    polygon_point_counts[polygon_id]['count'] += 1
                else:
                    polygon_point_counts[polygon_id] = {'count': 1, 'CODIGO': point[1], 'CODIGO_ANT': point[2]}

# Actualizar los atributos en Base_Vectorizada donde hay exactamente un punto
with arcpy.da.UpdateCursor(Base_Vectorizada, ["OID@", "CODIGO", "CODIGO_ANT"]) as update_cursor:
    for row in update_cursor:
        polygon_id = row[0]
        if polygon_id in polygon_point_counts and polygon_point_counts[polygon_id]['count'] == 1:
            row[1] = polygon_point_counts[polygon_id]['CODIGO']
            row[2] = polygon_point_counts[polygon_id]['CODIGO_ANT']
            update_cursor.updateRow(row)
            arcpy.AddMessage(f"Polígono OID {polygon_id} actualizado con CODIGO {row[1]} y CODIGO_ANT {row[2]}.")

########### POLÍGONOS CON MAS DE UN CENTROIDE (pequeños) #########################


# Crear una capa temporal para Base_Catastral
Base_Catastral_Layer = "Base_Catastral_Layer"
arcpy.MakeFeatureLayer_management(Base_Catastral, Base_Catastral_Layer)
arcpy.AddMessage("Capa temporal 'Base_Catastral_Layer' creada.")

arcpy.AddMessage("Procesando y transfiriendo datos")

# Iterar sobre los polígonos en Base_Vectorizada
with arcpy.da.UpdateCursor(Base_Vectorizada, ["OID@", "SHAPE@", "CODIGO", "CODIGO_ANT"]) as vector_cursor:
    for vector_row in vector_cursor:
        vector_oid = vector_row[0]
        vector_shape = vector_row[1]
        vector_codigo = vector_row[2]
        vector_codigo_ant = vector_row[3]

        # Solo proceder si los campos CODIGO y CODIGO_ANT están vacíos
        if not vector_codigo or not vector_codigo_ant:
            # Mensaje de depuración
            #arcpy.AddMessage(f"Procesando polígono OID {vector_oid} en Base_Vectorizada.")

            # Verificar que vector_shape no sea None y que Base_Catastral_Layer exista
            if vector_shape is None:
                arcpy.AddWarning(f"Geometría del polígono OID {vector_oid} en Base_Vectorizada es None.")
                continue
            
            if arcpy.Exists(Base_Catastral_Layer):
                # Seleccionar los polígonos en Base_Catastral que contienen el polígono en Base_Vectorizada
                try:
                    arcpy.management.SelectLayerByLocation(Base_Catastral_Layer, "CONTAINS", vector_shape)
                except Exception as e:
                    arcpy.AddWarning(f"Error al seleccionar características GEOMETRIA NULA DE BASE VECTORIZADA EN OID {vector_row[0]} : {e}")
                    continue

                # Verificar si se seleccionaron resultados
                count = int(arcpy.management.GetCount(Base_Catastral_Layer).getOutput(0))
                if count > 0:
                    # Buscar la información del primer polígono en Base_Catastral que contiene el polígono en Base_Vectorizada
                    with arcpy.da.SearchCursor(Base_Catastral_Layer, ["OID@", "CODIGO", "CODIGO_ANT", "SHAPE@"]) as catastral_cursor:
                        for catastral_row in catastral_cursor:
                            catastral_oid = catastral_row[0]
                            catastral_codigo = catastral_row[1]
                            catastral_codigo_ant = catastral_row[2]
                            catastral_shape = catastral_row[3]
                            
                            # Asegurarse de que catastral_shape no sea None
                            if catastral_shape is None:
                                arcpy.AddError(f"Geometría del polígono OID {catastral_oid} en Base_Catastral es None.")
                                continue

                            if catastral_shape.contains(vector_shape):
                                vector_row[2] = catastral_codigo
                                vector_row[3] = catastral_codigo_ant
                                vector_cursor.updateRow(vector_row)
                                arcpy.AddMessage(f"Polígono OID {vector_oid} en Base_Vectorizada actualizado con CODIGO {vector_row[2]} y CODIGO_ANT {vector_row[3]}.")
                                break  # Salir del cursor una vez actualizado
                else:
                    pass
            else:
                arcpy.AddError(f"La capa {Base_Catastral_Layer} no existe.")

# Eliminar la capa temporal
arcpy.management.Delete(Base_Catastral_Layer)

arcpy.AddMessage("Proceso finalizado con éxito.")
