import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
shapefile = arcpy.GetParameterAsText(0)
xlx = arcpy.GetParameterAsText(1)  # Tipo "file"
Ruta_Salida = arcpy.GetParameterAsText(2)
zona = arcpy.GetParameterAsText(3)

# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage("  ")
arcpy.AddMessage(f"Cálculando parámetros para zona {zona}.")

# 1. Crear copia del shapefile original
nombre_salida = f"Tolerancia_{os.path.basename(shapefile)[:10]}.shp"
ruta_salida = os.path.join(Ruta_Salida, nombre_salida)
shp = arcpy.management.CopyFeatures(shapefile, ruta_salida)
arcpy.management.RepairGeometry(in_features=shp, delete_null="DELETE_NULL", validation_method="OGC")

arcpy.AddMessage("Añadiendo campos...")
# 2. Verificar que el campo 'Toler_%' no exista antes de añadirlo
field_names = [field.name for field in arcpy.ListFields(shp)]
if 'Toleranc_%' not in field_names:
    arcpy.AddField_management(shp, 'Toleranc_%', 'DOUBLE')

# 3. Añadir el campo 'Tol_OK' con nombres cortos
if 'Toleran_OK' not in field_names:
    arcpy.AddField_management(shp, 'Toleran_OK', 'TEXT')

# 4. Verificar que la hoja de Excel existe y especificar la hoja
excel_sheet = xlx + r"\Hoja1$"  # Asegúrate de que "Hoja1" sea el nombre correcto de la hoja en tu Excel
if not arcpy.Exists(excel_sheet):
    arcpy.AddError("La hoja de Excel especificada no existe o no es accesible.")
    raise arcpy.ExecuteError

arcpy.AddMessage(f"Realizando JOIN de {excel_sheet}...")
# 5. Realizar el join con la tabla de Excel
arcpy.management.AddJoin(
    in_layer_or_view=shp,
    in_field="CODIGO",
    join_table=excel_sheet,
    join_field="NUMERO_PREDIAL",
    join_type="KEEP_ALL"
)

# 6. Copiar los resultados del join a un nuevo shapefile para que incluya los campos del Excel
shapefile_final = os.path.join(Ruta_Salida, f"Resultado_{os.path.basename(shapefile)[:10]}.shp")
arcpy.management.CopyFeatures(shp, shapefile_final)

arcpy.AddMessage("Calculando campos...")
# 7. Calcular el campo de % de tolerancia (VALOR ABSOLUTO) en el shapefile final
arcpy.management.CalculateField(
    in_table=shapefile_final,
    field="Toler_%",
    expression="abs((!Shape_Area! - !AREATERR!) / !Shape_Area! * 100)",
    expression_type="PYTHON3"
)

# 8. Remover el join (si lo consideras necesario para limpiar la capa original)
arcpy.management.RemoveJoin(shp)
