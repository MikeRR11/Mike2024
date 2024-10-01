# Taller de manejo de datos vectoriales - Semana de la Geomática
# Dirección de Gestión de Información Geográfica 
# Grupo de Investigación y Desarrollo

## OBJETIVO: Desarrollar un script que permita a los participantes del taller dominar 
#conceptos básicos como selecciones por atributos y por localización, manejo de cursores, funciones, y definición de variables.

import arcpy
import os

# Recibir las capas de municipios, parques nacionales y consulta SQL como parámetros
municipios = arcpy.GetParameterAsText(0)  # Shapefile de municipios
parques_nacionales = arcpy.GetParameterAsText(1)  # Capa de parques nacionales
SQL = arcpy.GetParameterAsText(2)  # Consulta SQL para selecciones adicionales
Ruta_Salida = arcpy.GetParameterAsText(3)  # Ruta de salida de los datos

# Configurar el entorno de trabajo y sobreescribir resultados
arcpy.env.overwriteOutput = True

# Crear una geodatabase de trabajo
gdb_path = os.path.join(Ruta_Salida,"TallerSG.gdb")
if not arcpy.Exists(gdb_path):
    arcpy.management.CreateFileGDB(Ruta_Salida, "TallerSG.gdb")
arcpy.AddMessage(f"Geodatabase creada en: {gdb_path}")




# Definir el sistema de referencia MAGNA-SIRGAS Origen Nacional
sr = arcpy.SpatialReference(9377)  # Código EPSG 9377 para Colombia MAGNA-SIRGAS

# Crear una copia de la capa de municipios en la geodatabase con la nueva proyección, tambien se puede usar arcpy.management.CopyFeatures, en este caso reproyectamos a origen nacional
municipios_copia = os.path.join(gdb_path, "Municipios_Proyectados")
arcpy.management.Project(municipios, municipios_copia, sr)
arcpy.AddMessage(f"Copia de la capa de municipios proyectada a MAGNA-SIRGAS creada en: {municipios_copia}")





# Agregar un nuevo campo para indicar si el municipio tiene parques
campo_nuevo = "Tiene_Parques"
if not arcpy.ListFields(municipios_copia, campo_nuevo):
    arcpy.AddMessage(f"Agregando campo '{campo_nuevo}'...")
    arcpy.management.AddField(municipios_copia, campo_nuevo, "TEXT", field_length=10)
else:
    arcpy.AddMessage(f"El campo '{campo_nuevo}' ya existe.")





# Selección por localización: municipios que se intersectan con parques nacionales
arcpy.AddMessage("Seleccionando municipios que intersectan con parques nacionales...")
arcpy.management.SelectLayerByLocation(municipios_copia, "INTERSECT", parques_nacionales, selection_type="SUBSET_SELECTION")

# Uso de SearchCursor: Mostrar los municipios seleccionados
with arcpy.da.SearchCursor(municipios_copia, ["MpNombre", "Depto"]) as search_cursor:
    arcpy.AddMessage("Municipios seleccionados que intersectan con parques:")
    for row in search_cursor:
        arcpy.AddMessage(f"Municipio: {row[0]}, Departamento: {row[1]}")
        Depto = row[1]



# Abrir sesión de edición en la geodatabase
workspace = gdb_path
edit = arcpy.da.Editor(workspace)
edit.startEditing(False, True)  # False = no versionado, True = con autocommit


# Iniciar la operación de edición
edit.startOperation()

# Actualizar la nueva columna con 'Sí tiene' para los municipios seleccionados
arcpy.AddMessage("Actualizando campo 'Parques' para los municipios que intersectan con parques...")
with arcpy.da.UpdateCursor(municipios_copia, [campo_nuevo, "Depto", 'MpNombre' ]) as update_cursor:
    for row in update_cursor:
        if row[1] == Depto:  
            row[0] = 'Sí tiene'  # Actualiza el campo con 'Sí tiene' si el municipio tiene parques
            update_cursor.updateRow(row)
            arcpy.AddMessage(f"Municipio {row[2]} actualizado con parques: {row[0]}")

# Finalizar la operación de edición
edit.stopOperation()




# Limpiar la selección
arcpy.management.SelectLayerByAttribute(municipios_copia, "CLEAR_SELECTION")
arcpy.AddMessage("Selección limpiada.")

# Detener la sesión de edición (con guardar cambios)
edit.stopEditing(True)  # True para guardar los cambios

