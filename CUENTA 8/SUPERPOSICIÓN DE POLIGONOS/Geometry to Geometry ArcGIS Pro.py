# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Geometry To Geometry - Feature on Feature Check
# Dirección de Gestión de Información Geográfica
# Grupo de desarrollo IGAC
# Elaboró / Modificó: Michael Andres Rojas
# Fecha: 2024-09-03
# -----------------------------------------------------------------------------

import arcpy
import os
import datetime

# Configuración de entorno
arcpy.env.overwriteOutput = True

def get_geometry_area(geom):
    """Devuelve el área de una geometría."""
    if geom:
        return geom.area
    return 0

def main():
    try:
        # Parámetros de entrada desde la toolbox
        shp1 = arcpy.GetParameterAsText(0)
        shp2 = arcpy.GetParameterAsText(1)
        relaciones_input = arcpy.GetParameterAsText(2)
        ruta_salida = arcpy.GetParameterAsText(3)

        # Validación de entradas
        if not arcpy.Exists(shp1):
            arcpy.AddError(f"La capa de entrada Feature 1 no existe: {shp1}")
            return
        if not arcpy.Exists(shp2):
            arcpy.AddError(f"La capa de entrada Feature 2 no existe: {shp2}")
            return
        if not relaciones_input:
            arcpy.AddError("No se ha especificado ninguna relación espacial.")
            return
        if not os.path.exists(ruta_salida):
            arcpy.AddError(f"La ruta de salida no existe: {ruta_salida}")
            return

        # Procesamiento de las relaciones espaciales seleccionadas
        relaciones = [rel.strip() for rel in relaciones_input.split(";")]

        # Crear una Geodatabase temporal para almacenar los resultados
        timestamp = f"{os.path.basename(shp1)}_{os.path.basename(shp2)}"
        nombre_gdb = f"Resultados_Relaciones_{timestamp}.gdb"
        gdb_temporal = os.path.join(ruta_salida, nombre_gdb)
        arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb_temporal}")
        arcpy.CreateFileGDB_management(ruta_salida, nombre_gdb)

        # Diccionario para mapear las relaciones espaciales
        relaciones_dict = {
            "Intersects": lambda g1, g2: g1.overlaps(g2) or g1.touches(g2) or g1.contains(g2),
            "Within": lambda g1, g2: g1.within(g2),
            "Within": lambda g1, g2: g1.within(g2),
            "Contains": lambda g1, g2: g1.contains(g2),
            "Touches": lambda g1, g2: g1.touches(g2),
            "Overlaps": lambda g1, g2: g1.overlaps(g2)
        }

        # Iterar sobre cada relación seleccionada
        for relacion in relaciones:
            if relacion in relaciones_dict:
                arcpy.AddMessage(f"Procesando relación espacial: {relacion}")

                # Crear un nombre único para la salida
                nombre_salida = f"{os.path.splitext(os.path.basename(shp1))[0]}_{relacion}"
                salida_fc = os.path.join(gdb_temporal, nombre_salida)

                # Crear capas temporales para cada feature class
                arcpy.MakeFeatureLayer_management(shp1, "layer1")
                arcpy.MakeFeatureLayer_management(shp2, "layer2")

                # Lista para almacenar las entidades que cumplen con la relación espacial
                features_to_export = []

                # Iterar sobre cada entidad en shp1
                with arcpy.da.SearchCursor("layer1", ["OID@", "SHAPE@"]) as cursor1:
                    for row1 in cursor1:
                        oid1, geom1 = row1
                        with arcpy.da.SearchCursor("layer2", ["OID@", "SHAPE@"]) as cursor2:
                            for row2 in cursor2:
                                oid2, geom2 = row2
                                if oid1 != oid2:  # Evitar comparación consigo mismo
                                    if relaciones_dict[relacion](geom1, geom2):
                                        if relacion == "Touches":
                                            # Exportar solo la geometría más pequeña en caso de 'Touches'
                                            area1 = get_geometry_area(geom1)
                                            area2 = get_geometry_area(geom2)
                                            if area1 < area2:
                                                features_to_export.append(geom1)
                                            else:
                                                features_to_export.append(geom2)
                                        else:
                                            features_to_export.append(geom1)
                                        break  # No es necesario continuar comparando si ya cumple la relación

                # Crear un feature class temporal para almacenar las entidades que cumplen la relación
                arcpy.CreateFeatureclass_management(gdb_temporal, nombre_salida, "POLYGON", spatial_reference=shp1)
                
                # Insertar las entidades que cumplen la relación en el nuevo feature class
                with arcpy.da.InsertCursor(salida_fc, ["SHAPE@"]) as cursor:
                    for feature in features_to_export:
                        cursor.insertRow([feature])

                # Añadir campo de relación
                arcpy.management.AddField(salida_fc, "Relacion", "TEXT", field_length=20)
                arcpy.management.CalculateField(salida_fc, "Relacion", f'"{relacion}"', "PYTHON3")

                # Agregar el resultado al mapa actual
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                mapa = aprx.activeMap
                if mapa:
                    mapa.addDataFromPath(salida_fc)
                    arcpy.AddMessage(f"Resultado añadido al mapa: {nombre_salida}")
                else:
                    arcpy.AddWarning("No se encontró un mapa activo para añadir los resultados.")
            else:
                arcpy.AddWarning(f"Relación espacial no válida o no soportada: {relacion}")

        arcpy.AddMessage("Proceso completado exitosamente.")

    except Exception as e:
        arcpy.AddError(f"Ocurrió un error durante la ejecución: {e}")
        arcpy.AddError(arcpy.GetMessages(2))

if __name__ == "__main__":
    main()
    