import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
shapefile = arcpy.GetParameterAsText(0)
excel_path = arcpy.GetParameterAsText(1)  # Tipo "file"
output_folder = arcpy.GetParameterAsText(2)
zona = arcpy.GetParameterAsText(3)

# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage("  ")
arcpy.AddMessage(f"Calculando parámetros para zona {zona}.")

# 1. Crear copia del shapefile original
output_name = f"Tolerancia_{os.path.basename(shapefile)[:10]}.shp"
output_path = os.path.join(output_folder, output_name)
shp_copy = arcpy.management.CopyFeatures(shapefile, output_path)
arcpy.management.RepairGeometry(in_features=shp_copy, delete_null="DELETE_NULL", validation_method="OGC")

# 2. Convertir el archivo Excel a una tabla de ArcGIS
arcpy.AddMessage("Convirtiendo archivo Excel a tabla...")
excel_table = os.path.join(output_folder, "excel_table")
dbf = arcpy.conversion.ExcelToTable(excel_path, excel_table, "Hoja1")

# 4. Realizar el join con la tabla de Excel
arcpy.AddMessage(f"Realizando JOIN de {excel_table}...")
arcpy.management.JoinField(
    in_data=shp_copy,
    in_field="CODIGO",
    join_table=dbf,
    join_field="NUMERO_PRE",
    fields=["AREATERR"])


# Agregar el campo Tol_P como tipo DOUBLE
arcpy.management.AddField(in_table=shp_copy, field_name="Tol_P", field_type="DOUBLE")

# Calcular el campo Tol_P
arcpy.management.CalculateField(
    in_table=shp_copy,
    field="Tol_P",
    expression="round(abs((!Shape_Area! - !AREATERR!) / !Shape_Area! * 100), 3)",
    expression_type="PYTHON3"
)

# Agregar el campo Tol_OK como tipo texto
arcpy.management.AddField(in_table=shp_copy, field_name="Tol_OK", field_type="TEXT")

# Determinar el bloque de código según la zona
if zona == 'Urbano':
    # Definir el código de la función como un bloque de texto
    code_block = """
def validar_tolerancia(area, tolerancia):
    if area <= 80:
        max_tolerancia = 7
    elif 80 < area <= 250:
        max_tolerancia = 6
    elif 250 < area <= 500:
        max_tolerancia = 4
    else:
        max_tolerancia = 3

    return "OK" if tolerancia <= max_tolerancia else "NO OK"
"""
else:
    code_block = """
def validar_tolerancia(area, tolerancia):
    if area <= 2000:
        max_tolerancia = 10
    elif 2000 < area <= 10000:
        max_tolerancia = 9
    elif 10000 < area <= 100000:
        max_tolerancia = 7
    elif 100000 < area <= 500000:
        max_tolerancia = 4
    else:
        max_tolerancia = 2

    return "OK" if tolerancia <= max_tolerancia else "NO OK"
"""

# Definir la expresión de cálculo para el campo Tol_OK
expression = "validar_tolerancia(!Shape_Area!, !Tol_P!)"

# Calcular el campo Tol_OK utilizando la expresión y el código de la función
arcpy.management.CalculateField(
    in_table=shp_copy,
    field="Tol_OK",
    expression=expression,
    expression_type="PYTHON3",
    code_block=code_block
)

arcpy.AddMessage("Proceso completado.")
