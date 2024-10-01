# Taller de manejo de datos vectoriales - Semana de la Geomática
# Dirección de Gestión de Información Geográfica 
# Grupo de Investigación y Desarrollo

## OBJETIVO: Desarrollar un script que permita a los participantes del taller dominar 
#conceptos básicos como selecciones por atributos y por localización, manejo de cursores, funciones, y definición de variables.

import arcpy
import os

# Recibir las capas de municipios y parques nacionales como parámetros
municipios = arcpy.GetParameterAsText(0)
parques_nacionales = arcpy.GetParameterAsText(1)

# Habilitar sobreescritura de resultados
arcpy.env.overwriteOutput = True

# Seleccionar los municipios del departamento de Amazonas
# Explicación: Se usa la función SelectLayerByAttribute para seleccionar por un criterio en la tabla de atributos
arcpy.AddMessage("Seleccionando municipios del departamento de Amazonas...")
arcpy.management.SelectLayerByAttribute(municipios, "NEW_SELECTION", "Depto = 'Amazonas'")

# Agregar una nueva columna para indicar si el municipio tiene parques
campo_nuevo = "Parques"
if not arcpy.ListFields(municipios, campo_nuevo):
    arcpy.AddMessage(f"Agregando campo '{campo_nuevo}'...")
    arcpy.management.AddField(municipios, campo_nuevo, "TEXT", field_length=10)
else:
    arcpy.AddMessage(f"El campo '{campo_nuevo}' ya existe.")



# Selección por localización: municipios que se intersectan con parques nacionales
# Explicación: Seleccionamos municipios que están dentro o intersectan con parques nacionales
arcpy.AddMessage("Seleccionando municipios que intersectan con parques nacionales...")
arcpy.management.SelectLayerByLocation(municipios, "INTERSECT", parques_nacionales, selection_type="SUBSET_SELECTION")

# Uso de SearchCursor: Mostrar los municipios seleccionados
# Explicación: Aquí usamos SearchCursor para listar los municipios seleccionados antes de hacer actualizaciones
with arcpy.da.SearchCursor(municipios, ["MpNombre", "Depto"]) as search_cursor:
    arcpy.AddMessage("Municipios seleccionados que intersectan con parques:")
    for row in search_cursor:
        arcpy.AddMessage(f"Municipio: {row[0]}, Departamento: {row[1]}")




# Actualizar la nueva columna con 'Sí tiene' para los municipios seleccionados
# Explicación: Se usa UpdateCursor para actualizar la información en los municipios que tienen parques
arcpy.AddMessage("Actualizando campo 'Tiene_Parques' para los municipios del Amazonas...")
with arcpy.da.UpdateCursor(municipios, [campo_nuevo, "Depto"]) as update_cursor:
    for row in update_cursor:
        if row[1] == "Amazonas":
            row[0] = 'Sí tiene'  # Actualiza el campo con 'Sí tiene' si el municipio tiene parques
            update_cursor.updateRow(row)
            arcpy.AddMessage(f"Municipio actualizado en Amazonas con parques: {row[0]}")


            

# Limpiar la selección
# Explicación: Limpia la selección actual para evitar errores en otros procesos
arcpy.management.SelectLayerByAttribute(municipios, "CLEAR_SELECTION")
arcpy.AddMessage("Selección limpiada.")
