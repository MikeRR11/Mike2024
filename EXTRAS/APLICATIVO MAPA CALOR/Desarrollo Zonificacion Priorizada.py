# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Desarrollo Zonificación Priorizada V1
# Elaboró / Modificó: Michael Andres Rojas
# Fecha: 27/09/2024
# ----------------------------------------------------------------------

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
# Validación de entradas
if not os.path.exists(ruta_salida):
    arcpy.AddError(f"La ruta de salida no existe: {ruta_salida}")


# Procesamiento de los shapes de puntos originales
features_Lista = [rel.strip() for rel in features.split(";")]  # Se dejan en una lista separados por punto y coma las rutas

# Crear una Geodatabase temporal para almacenar los resultados
nombre_gdb = f"Zonificacion_Priorizada.gdb"
gdb_temporal = os.path.join(ruta_salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb_temporal}")
arcpy.CreateFileGDB_management(ruta_salida, nombre_gdb)


# Función para generar shapefiles y aplicar Kernel Density, todo dentro de la geodatabase
def generar_shapefiles_y_kernel_density(layer, campo, output_gdb):
    categorias = list(set([row[0] for row in arcpy.da.SearchCursor(layer, [campo])]))  # Obtener categorías únicas
    arcpy.AddMessage(f"Creando listas de categorías: {categorias}")

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
        output_feature_class = os.path.join(output_gdb, f"Pririzacion_{categoria}_Puntos")
        arcpy.management.CopyFeatures(categoria_layer, output_feature_class)
        arcpy.AddMessage(f"Feature class creado para priorización {categoria} creado en la GDB")
        
        # Generar Kernel Density dentro de la geodatabase
        output_kernel = os.path.join(output_gdb, f"Kernel_Priorizacion_{categoria}")
        arcpy.sa.KernelDensity(categoria_layer, "NONE").save(output_kernel)
        arcpy.AddMessage(f"Kernel Density para priorización {categoria} creado en la GDB")


# Procesar cada feature layer
for feature in features_Lista:
    generar_shapefiles_y_kernel_density(feature, campo_categoria, gdb_temporal)

arcpy.AddMessage("Proceso completado.")



##########
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Desarrollo Zonificación Priorizada V1
# Elaboró / Modificó: Michael Andres Rojas
# Fecha: 27/09/2024
# ----------------------------------------------------------------------

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

# Validación de entradas
if not os.path.exists(ruta_salida):
    arcpy.AddError(f"La ruta de salida no existe: {ruta_salida}")

# Procesamiento de los shapes de puntos originales
features_Lista = [rel.strip() for rel in features.split(";")]  # Se dejan en una lista separados por punto y coma las rutas

# Crear una Geodatabase temporal para almacenar los resultados
nombre_gdb = f"Zonificacion_Priorizada.gdb"
gdb_temporal = os.path.join(ruta_salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb_temporal}")
arcpy.CreateFileGDB_management(ruta_salida, nombre_gdb)


# Función para generar shapefiles, aplicar Kernel Density y convertir a polígonos
def generar_shapefiles_y_kernel_density(layer, campo, output_gdb):
    categorias = list(set([row[0] for row in arcpy.da.SearchCursor(layer, [campo])]))  # Obtener categorías únicas
    arcpy.AddMessage(f"Creando listas de categorías: {categorias}")

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
        arcpy.AddMessage(f"Convirtiendo el raster de Kernel Density a enteros para la priorización {categoria}")
        raster_entero = arcpy.sa.Int(kernel_density_raster)
        raster_entero_path = os.path.join(output_gdb, f"Kernel_Priorizacion_{categoria}_Int")
        raster_entero.save(raster_entero_path)
        arcpy.AddMessage(f"Raster convertido a enteros guardado como {raster_entero_path}")
        
        # Convertir el raster entero a polígonos
        output_polygon = os.path.join(output_gdb, f"Poligonos_Priorizacion_{categoria}")
        arcpy.AddMessage(f"Convirtiendo el raster a polígonos para la priorización {categoria}")
        arcpy.conversion.RasterToPolygon(raster_entero_path, output_polygon, "NO_SIMPLIFY", "VALUE")
        arcpy.AddMessage(f"Polígonos creados para la priorización {categoria} guardados en {output_polygon}")


# Procesar cada feature layer
for feature in features_Lista:
    generar_shapefiles_y_kernel_density(feature, campo_categoria, gdb_temporal)

arcpy.AddMessage("Proceso completado.")


