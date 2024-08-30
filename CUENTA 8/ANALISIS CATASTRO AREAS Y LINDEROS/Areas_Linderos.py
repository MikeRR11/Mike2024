import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
shapefile = arcpy.GetParameterAsText(0)
xlx = arcpy.GetParameterAsText(1)
Ruta_Salida = arcpy.GetParameterAsText(2)
zona = arcpy.GetParameterAsText(3)

# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage("  ")
arcpy.AddMessage(f"Cálculando parametros para zona {zona}.")

#1 crear copia del shp original

# Nombre de salida para el shapefile de intersección
nombre_salida = f"Tolerancia_{os.path.basename(shapefile)[:10]}.shp"
ruta_salida = os.path.join(Ruta_Salida, nombre_salida)
shp = arcpy.management.CopyFeatures(shapefile, ruta_salida)
arcpy.management.RepairGeometry(in_features = shp, delete_null="DELETE_NULL", validation_method="OGC")

#2 Añadir campo para el parametro de % de tolerancia y evaluacion del mismo (OK y NO OK)

arcpy.AddField_management(shp, 'Tolerancia %', 'double')
arcpy.AddField_management(shp, 'Tolerancia OK', 'text')

#3 Realizar join

arcpy.management.AddJoin(
    in_layer_or_view = shp,
    in_field = "CODIGO",
    join_table = xlx,
    join_field = "NUMERO_PREDIAL",
    join_type = "KEEP_ALL",
    index_join_fields = "NO_INDEX_JOIN_FIELDS",
    rebuild_index = "NO_REBUILD_INDEX"
)

#4 Calcular campo de % de tolerancia

tolerancia = arcpy.management.CalculateField(in_table, field, expression, {expression_type}, {code_block}, {field_type}, {enforce_domains})
#5 Calcular evaluacion de tolerancia respecto a tabla IGAC



