#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Yaritza Quevedo - Michael Andres Rojas - Diego Rugeles
import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
shapefile = arcpy.GetParameterAsText(0)
excel_path = arcpy.GetParameterAsText(1)  # Tipo "file"
Ruta_Salida = arcpy.GetParameterAsText(2)
zona = arcpy.GetParameterAsText(3)

# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage("  ")
arcpy.AddMessage(f"Calculando parámetros para zona {zona}.")

# 1. Crear copia del shapefile original
output_name = f"Tolerancia_{os.path.basename(shapefile)[:10]}.shp"
output_path = os.path.join(Ruta_Salida, output_name)
shp_copy = arcpy.management.CopyFeatures(shapefile, output_path)
arcpy.management.RepairGeometry(in_features=shp_copy, delete_null="DELETE_NULL", validation_method="OGC")

# 2. Convertir el archivo Excel a una tabla de ArcGIS
arcpy.AddMessage("Convirtiendo archivo Excel a tabla...")
excel_table = os.path.join(Ruta_Salida, "excel_table")
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

#### LINDEROS
arcpy.AddMessage("Convirtiendo a líneas...")
lineas = arcpy.management.FeatureToLine(in_features=shp_copy, out_feature_class=os.path.join(Ruta_Salida, "Lineas"), cluster_tolerance=None, attributes="ATTRIBUTES")
arcpy.AddMessage("Conversión a líneas completada.")

# Realizar un Spatial Join para identificar las superposiciones
arcpy.AddMessage("Realizando Spatial Join para identificar superposiciones...")
spatial_join = os.path.join(Ruta_Salida, "Join_Overlaps")
arcpy.analysis.SpatialJoin(
    target_features=lineas,
    join_features=lineas,
    out_feature_class=spatial_join,
    join_type="KEEP_COMMON",  # Mantener solo los registros coincidentes
    match_option="CONTAINS",  # Coincidir si las geometrías se intersectan
    field_mapping="",  # Mantener todos los campos de las entidades de unión en la salida
    distance_field_name="",  # No agregar campo de distancia
    join_operation="JOIN_ONE_TO_ONE"  # Fusionar atributos de múltiples entidades de unión
)
arcpy.AddMessage("Spatial Join completado.")

arcpy.AddMessage("Calculando Semaforo.")

code_block = """
def validar_semaforo(Tol_OK, Tol_OK_1):
    if Tol_OK == "OK" and Tol_OK_1 == "OK":
        semaforo = "VERDE"
    elif Tol_OK == "NO OK" and Tol_OK_1 == "OK":
        semaforo = "AMARILLO"
    elif Tol_OK == "OK" and Tol_OK_1 == "NO OK":
        semaforo = "AMARILLO"
    elif Tol_OK == "NO OK" and Tol_OK_1 == "NO OK":
        semaforo = "ROJO"
    else:
        semaforo = ""

    return semaforo
"""

# Definir la expresión de cálculo para el campo SEMAFO
expression = "validar_semaforo(!Tol_OK!, !Tol_OK_1!)"

# Añadir el nuevo campo para el semáforo
arcpy.AddMessage("Añadiendo el campo de semáforo...")
arcpy.management.AddField(spatial_join, "SEMAFORO", "TEXT")
arcpy.AddMessage("Campo de semáforo añadido.")

# Calcular el campo SEMAFO utilizando la expresión y el código de la función
arcpy.management.CalculateField(
    in_table=spatial_join,  # Cambiado de shp_copy a spatial_join
    field="SEMAFORO",
    expression=expression,
    expression_type="PYTHON3",
    code_block=code_block
)

# Crear la geodatabase
arcpy.management.CreateFileGDB(Ruta_Salida, "Linderos_Verificados.gdb")
gdb_path = os.path.join(Ruta_Salida, "Linderos_Verificados.gdb")

# Copiar los feature classes a la geodatabase
arcpy.AddMessage("Copiando feature classes a la geodatabase...")
copy_spatial = arcpy.management.CopyFeatures(spatial_join, os.path.join(gdb_path, "SemaforoLinderos"))
copy_shp = arcpy.management.CopyFeatures(shp_copy, os.path.join(gdb_path, "PorcentajeTolerancia"))
copy_table = arcpy.conversion.TableToGeodatabase(dbf, gdb_path)

#Eliminar Shapes

arcpy.management.Delete(spatial_join)
arcpy.management.Delete(shp_copy)
arcpy.management.Delete(dbf)
arcpy.management.Delete(lineas)

arcpy.AddMessage("Proceso completado.")
