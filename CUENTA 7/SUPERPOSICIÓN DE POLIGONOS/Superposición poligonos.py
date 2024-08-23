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

# Procesamiento de intersecciones
for i, fc1 in enumerate(fc_list):
    # Calcular el progreso como un porcentaje
    progreso = int((i / float(total_fc - 1)) * 100)
    arcpy.SetProgressorLabel(f"Analizando: {os.path.basename(fc1)}")
    arcpy.AddMessage(f"Progreso: {progreso}% - Analizando: {os.path.basename(fc1)}")
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
