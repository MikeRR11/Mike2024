
import arcpy
import os
from openpyxl import Workbook

# Parámetro de entrada: ruta de la geodatabase
features = arcpy.GetParameterAsText(0)  # Parámetro 1
output_folder = arcpy.GetParameterAsText(1)  # Parámetro 2 (ruta de la carpeta de salida)

arcpy.AddMessage("INICIANDO PROCESO....")

# Crear una lista para almacenar los datos

# Procesamiento de los shapes de puntos originales
if features:
    features_Lista = [rel.strip() for rel in features.split(";")]  # Se dejan en una lista separados por punto y coma las rutas
else:
    arcpy.AddError("No se ha proporcionado ninguna capa de entrada.")
    raise ValueError("No se han proporcionado features de entrada")

# Crear un libro de trabajo de Excel y agregar una hoja
wb = Workbook()
ws = wb.active
ws.title = "Anotaciones"

# Escribir encabezados en la primera fila
ws.append(['FeatureDataset', 'FeatureClass', 'OBJECTID', 'FeatureID', 'TextString'])

# Procesar cada feature class
for anotacion_layer in features_Lista:
    arcpy.AddMessage(f"Iniciando proceso para: {anotacion_layer}")

    # Extraer el FeatureDataset y FeatureClass
    fds, fc = os.path.split(anotacion_layer)
    fds = os.path.basename(fds)  # Extraer solo el nombre del Feature Dataset

    # Aplicar la selección por atributos
    SQL = "Status = 0 AND TextString IS NOT NULL"
    seleccion = arcpy.SelectLayerByAttribute_management(anotacion_layer, "NEW_SELECTION", SQL)

    # Verificar si hay registros seleccionados
    if int(arcpy.GetCount_management(seleccion).getOutput(0)) > 0:
        # Utilizar un cursor para extraer datos específicos solo de la selección
        fields = ['OBJECTID', 'FeatureID', 'TextString']  # Reemplazar con los campos específicos que necesitas
        with arcpy.da.SearchCursor(seleccion, fields) as cursor:
            for row in cursor:
                # Agregar la información a la hoja de Excel
                ws.append([fds, fc] + list(row))

    # Limpiar la selección
    arcpy.SelectLayerByAttribute_management(anotacion_layer, "CLEAR_SELECTION")

# Guardar el archivo Excel
excel_path = os.path.join(output_folder, "anotaciones_resultado.xlsx")
wb.save(excel_path)

arcpy.AddMessage(f'Archivo Excel generado en: {excel_path}')
print(f'Archivo Excel generado en: {excel_path}')
