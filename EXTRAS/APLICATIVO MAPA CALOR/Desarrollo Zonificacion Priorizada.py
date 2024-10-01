import arcpy
import os
import datetime

# Configuración de entorno
arcpy.env.overwriteOutput = True

# Parámetros de entrada desde la toolbox
features = arcpy.GetParameterAsText(0)  # Entrada de features desde toolbox
campo_categoria = arcpy.GetParameterAsText(1)  # Campo para clasificar
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
nombre_gdb = f"Zonificacion_Priorizada.gdb"
gdb_temporal = os.path.join(ruta_salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb_temporal}")
arcpy.CreateFileGDB_management(ruta_salida, nombre_gdb)

# Función para generar shapefiles, aplicar Kernel Density y convertir a polígonos
def generar_shapefiles_y_kernel_density(layer, campo, output_gdb):
    categorias = list(set([row[0] for row in arcpy.da.SearchCursor(layer, [campo])]))  # Obtener categorías únicas
    Feature_Entrada = os.path.basename(layer)
    arcpy.AddMessage(espacio2)
    arcpy.AddMessage(f"PROCESANDO FEATURE CLASS: {Feature_Entrada}...")
    arcpy.AddMessage(f"Creando listas de categorías: {categorias}")
    arcpy.AddMessage(espacio2)
    for categoria in categorias:
        # Crear una query para seleccionar cada categoría
        query = f"{campo} = {categoria}"  # Campo numérico (Short)
        
        # Crear un feature layer temporal para la categoría
        categoria_layer = f"layer_{categoria}"
        arcpy.AddMessage(espacio)
        arcpy.AddMessage(f"Aplicando query: {query}")
        
        try:
            arcpy.management.MakeFeatureLayer(layer, categoria_layer, query)
        except arcpy.ExecuteError as e:
            arcpy.AddError(f"Error al crear el Feature Layer para la categoría {categoria}: {str(e)}")
            continue

        # Guardar dentro de la geodatabase (sin extensión .shp)
        output_feature_class = os.path.join(output_gdb, f"Priorizacion_{categoria}_Puntos")
        arcpy.management.CopyFeatures(categoria_layer, output_feature_class)
        arcpy.AddMessage(f"Feature class creado para priorización {categoria} creado en la GDB")
        
        # Generar Kernel Density dentro de la geodatabase
        output_kernel = os.path.join(output_gdb, f"Kernel_Priorizacion_{categoria}")
        kernel_density_raster = arcpy.sa.KernelDensity(categoria_layer, "NONE")
        kernel_density_raster.save(output_kernel)
        arcpy.AddMessage(f"Kernel Density para priorización {categoria} creado en la GDB")

        # Convertir valores del raster a enteros utilizando la función 'Int'
        arcpy.AddMessage(f"Convirtiendo el raster de Kernel Density a enteros para la priorización: {categoria}")
        raster_entero = arcpy.sa.Int(kernel_density_raster)
        raster_entero_path = os.path.join(output_gdb, f"Kernel_Priorizacion_{categoria}_Int")
        raster_entero.save(raster_entero_path)
        arcpy.AddMessage(f"Raster convertido a enteros guardado para la priorización: {categoria}")
        
        #Clasificar el raster con desviacion estandar
        natural_breaks = arcpy.management.ReclassifyField(raster_entero, "Value", "STANDARD_DEVIATION", standard_deviations = "QUARTER", output_field_name = f"Clasificación_Priorizacion_{categoria}")
        arcpy.AddMessage(f"Clasificación creada para la priorización: {categoria}")

        # Convertir el raster entero a polígonos
        output_polygon = os.path.join(output_gdb, f"Poligonos_Priorizacion_{categoria}")
        arcpy.AddMessage(f"Convirtiendo el raster a polígonos para la priorización {categoria}")
        arcpy.conversion.RasterToPolygon(raster_entero, output_polygon, "SIMPLIFY", f"Clasificación_Priorizacion_{categoria}_RANGE")
        #arcpy.AddMessage(f"Polígonos creados para la priorización {categoria} guardados en la GDB")

        #Exportar las clases superiores a la 5
        output_feature_select = os.path.join(output_gdb, f"Mapa_Prio_{categoria}")
        select = arcpy.management.SelectLayerByAttribute(output_polygon, "NEW_SELECTION", "gridcode > 10", invert_where_clause = False)
        arcpy.conversion.ExportFeatures(select, output_feature_select)

        #Unir los pologonos
        merged_output = os.path.join(output_gdb, f"Prio_{categoria}")
        arcpy.management.Dissolve(output_feature_select, merged_output, multi_part=False)

        # Definir la geodatabase de salida y el layer de entrada
        Feature_Entrada = os.path.basename(layer)
        out_name = f"Zonas_Calientes_{Feature_Entrada}"

        # Crear Feature Dataset en la geodatabase de salida (output_gdb)
        output_dataset = os.path.join(output_gdb, out_name)

        # Verificar si el Feature Dataset ya existe para evitar errores
        if not arcpy.Exists(output_dataset):
            spatial_ref = arcpy.SpatialReference(9377)
            arcpy.management.CreateFeatureDataset(output_gdb, out_name, spatial_ref)
            
        # Definir el nombre y la ruta del Feature Class suavizado
        output_feature_smooth = os.path.join(output_dataset, f"{Feature_Entrada}_Priorizacion_{categoria}")

        # Aplicar suavizado a los polígonos
        arcpy.cartography.SmoothPolygon(merged_output, output_feature_smooth, algorithm="PAEK", tolerance="1000 Meters",
                                                endpoint_option="FIXED_ENDPOINT", error_option="RESOLVE_ERRORS")

                
        # Agregar un nuevo campo para la categoría después del merge
        arcpy.management.AddField(output_feature_smooth, campo_categoria, "TEXT")
        arcpy.management.AddField(output_feature_smooth, "Zona_Priorizacion", "TEXT")

        #Eliminar campos sobrantes
        Campo1 = ["SmoPgnFlag"]
        Campo2= "InPoly_FID"

        # Llenar el nuevo campo con la categoría correspondiente
        with arcpy.da.UpdateCursor(output_feature_smooth, [campo_categoria, Campo2,"Zona_Priorizacion"]) as cursor:
            for row in cursor:
                row[0] = categoria  # Asignar la categoría
                row[2] = f"{categoria}_{row[1]}"
                cursor.updateRow(row)

        #Definir y crear  de Feature con todas las la categoria de priorizacion
        Feature_Final = os.path.join(output_dataset, f"Zonas_Calientes_{Feature_Entrada}")
        if not arcpy.Exists(Feature_Final):
        # Usar el esquema de uno de los polígonos suavizados para definir la estructura
            arcpy.management.CreateFeatureclass(output_dataset, f"Zonas_Calientes_{Feature_Entrada}", "POLYGON", 
                                            template=output_feature_smooth)

        # Insertar los polígonos suavizados en el Feature Class consolidado
        arcpy.management.Append([output_feature_smooth], Feature_Final, "NO_TEST")
        arcpy.management.DeleteField(output_feature_smooth, Campo1)
        arcpy.management.DeleteField(output_feature_smooth, Campo2)

        # Mensaje para indicar que el proceso ha terminado correctamente
        arcpy.AddMessage(f"Polígonos creados para la priorización {categoria} del Feature {Feature_Entrada}")


        #####################################################################################################
        #Insertar valores de zona en feature de puntos, primero crear una copia del layer de puntos

        zonas_puntos = os.path.join(output_dataset, f"Zonas_Priorizacion_{Feature_Entrada}_Puntos")
        if not arcpy.Exists(zonas_puntos):
            arcpy.management.CopyFeatures(layer, zonas_puntos)
            arcpy.management.AddField(zonas_puntos, "Zona_Priorizacion", "TEXT")

        # Seleccionar puntos que están dentro de los polígonos suavizados
        arcpy.management.SelectLayerByLocation(zonas_puntos, 'WITHIN', output_feature_smooth)

        # Crear un cursor de búsqueda para recorrer los polígonos suavizados
        with arcpy.da.SearchCursor(output_feature_smooth, ['SHAPE@', 'Zona_Priorizacion']) as poligonos_cursor:
            for poligono in poligonos_cursor:
                poligono_geom = poligono[0]  # Geometría del polígono
                zona_priorizacion_valor = poligono[1]  # Valor de la priorización

                # Crear un cursor de actualización para los puntos
                with arcpy.da.UpdateCursor(zonas_puntos, ['SHAPE@', 'Zona_Priorizacion','OID@', campo_categoria]) as puntos_cursor:
                    for punto in puntos_cursor:
                        punto_geom = punto[0]  # Geometría del punto
                        ID = punto[2]
                        punto_categoria = punto[3]
                        try:
                            # Verificar si el punto está dentro del polígono
                            if poligono_geom.contains(punto_geom) and punto_categoria == categoria:
                                # Asignar el valor de priorización
                                punto[1] = zona_priorizacion_valor
                                puntos_cursor.updateRow(punto)
                        except Exception as e:
                            arcpy.AddWarning(f"Error al actualizar el punto con ID {ID} del feature {Feature_Entrada}: Geometría invalida ... {str(e)}")
                            warning = True
                            # Continuar con el siguiente punto, no detener el script
                            continue

            
        arcpy.AddMessage(f"Puntos clasificados para priorización {categoria} del Feature {Feature_Entrada}")
        # Limpiar selección.
        arcpy.management.SelectLayerByAttribute(zonas_puntos, 'CLEAR_SELECTION')
        
        #Eliminar datos temporales
        Lista_Borrar = [output_kernel,
                        raster_entero_path,
                        output_polygon,
                        output_feature_select,
                        merged_output,
                        output_feature_class] 
        
        for temporal in Lista_Borrar:
             arcpy.management.Delete(temporal)
    if warning == True:
        arcpy.AddWarning(f"Se recomienda reparar geometrias para el feauture: {Feature_Entrada}")



# Procesar cada feature layer
for feature in features_Lista:
    generar_shapefiles_y_kernel_density(feature, campo_categoria, gdb_temporal)
    
arcpy.AddMessage(espacio2)
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO")
