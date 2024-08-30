import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
GDB = arcpy.GetParameterAsText(0)
Ruta_Salida = arcpy.GetParameterAsText(1)

# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage("  ")

# Crear lista de feature classes de tipo polígono, excluyendo anotaciones
fc_list = []
for dirpath, dirnames, filenames in arcpy.da.Walk(GDB, datatype="FeatureClass", type="Polygon"):
    for filename in filenames:
        desc = arcpy.Describe(os.path.join(dirpath, filename))
        if desc.featureType not in ["Annotation", "CoverageAnnotation"]:
            fc_list.append(os.path.join(dirpath, filename))

# Total de feature classes
total_fc = len(fc_list)

# Procesamiento de intersecciones y relaciones espaciales adicionales
for i, fc1 in enumerate(fc_list):
    progreso = int((i / float(total_fc - 1)) * 100)
    arcpy.SetProgressorLabel(f"Analizando: {os.path.basename(fc1)}")
    arcpy.AddMessage(f"Progreso: {progreso}% - Analizando: {os.path.basename(fc1)}")
    
    # Verificación entre los polígonos de la misma capa
    oids_procesados = set()  # Conjunto para rastrear los pares de OID procesados
    with arcpy.da.SearchCursor(fc1, ["OID@", "SHAPE@"]) as cursor1:
        for row1 in cursor1:
            oid1, geom1 = row1
            with arcpy.da.SearchCursor(fc1, ["OID@", "SHAPE@"]) as cursor2:
                for row2 in cursor2:
                    oid2, geom2 = row2
                    if oid1 != oid2 and (oid2, oid1) not in oids_procesados:  # Evita la duplicación
                        if geom1.touches(geom2) or geom1.within(geom2) or geom1.overlaps(geom2):
                            nombre_salida = f"Rel_{os.path.basename(fc1)[:10]}_{oid1}_{oid2}.shp"
                            ruta_salida = os.path.join(Ruta_Salida, nombre_salida)
                            arcpy.management.CopyFeatures([geom1, geom2], ruta_salida)
                            arcpy.AddMessage(f"   - Relación espacial encontrada entre OID {oid1} y OID {oid2}")
                            
                            # Marcar este par de OIDs como procesados
                            oids_procesados.add((oid1, oid2))
    
    for j in range(i + 1, len(fc_list)):
        fc2 = fc_list[j]
        arcpy.AddMessage(f" - Comparando con: {os.path.basename(fc2)}")
        
        # Nombre de salida para el shapefile de intersección
        nombre_salida = f"Inter_{os.path.basename(fc1)[:10]}_{os.path.basename(fc2)[:10]}.shp"
        ruta_salida = os.path.join(Ruta_Salida, nombre_salida)
        
        # Realizar la intersección
        try:
            intersect_output = os.path.join("in_memory", "intersect_temp")
            arcpy.analysis.Intersect([fc1, fc2], intersect_output, "ONLY_FID", "", "INPUT")
            arcpy.SetProgressorLabel(f"Analizando: {os.path.basename(fc1)}")
            # Contar las entidades resultantes de la intersección
            conteo = int(arcpy.GetCount_management(intersect_output)[0])
            if conteo > 0:
                arcpy.AddMessage(f"   - Intersección encontrada con {conteo} entidades")
                
                # Exportar solo si hay intersección
                arcpy.management.CopyFeatures(intersect_output, ruta_salida)
                arcpy.AddMessage(f"   - Intersección exportada a: {ruta_salida}")
            else:
                arcpy.AddMessage(f"   - No se encontraron intersecciones")
        
        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as e:
            arcpy.AddError(f"Error no esperado: {e}")
        
        # Limpiar la memoria
        arcpy.management.Delete(intersect_output)
        arcpy.SetProgressorLabel(f"Analizando: {os.path.basename(fc1)}")

# Resetear el progressor al finalizar
arcpy.ResetProgressor()
arcpy.AddMessage("Proceso completado.")
