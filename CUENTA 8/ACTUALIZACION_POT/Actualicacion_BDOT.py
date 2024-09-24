# Desarrollado por Michael Rojas / Diego Rugeles 
# Aplicativo para convertir tabla Excel en feature class actualizando base de datos de Ordenamiento Territorial
# Version 1.0
# 19 de septiembre de 2024

import arcpy
import os
from datetime import datetime


def is_convertible_to_int(value):
    """Verifica si un valor es convertible a un entero."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None
    


def join_excel(excel, ruta_salida, bdot, munpi):
    # Definiendo espacio de trabajo e iniciando sesión de edición
    workspace = os.path.join(bdot)
    editor = arcpy.da.Editor(workspace)
    editor.startEditing(False, True)
    editor.startOperation()
    sr = arcpy.SpatialReference(9377)
    
    try:
        # Convirtiendo excel de OT en tabla de ArcGIS
        arcpy.AddMessage("Convirtiendo hoja HOJA_EXCEL de Excel a tabla...")
        tabla_OT = arcpy.conversion.ExcelToTable(excel, os.path.join(ruta_salida, "EXCEL_OT"), "POT")
        arcpy.AddMessage("Datos de HOJA_EXCEL convertidos exitosamente.")
        
        fields_OT = arcpy.ListFields(tabla_OT)

        fields_table_OT = [f.name for f in fields_OT if f.name not in ["OID", "COL_W"]]
        # Feature Class de OT (vacío)
        shape = os.path.join(bdot, "Instr_OT", "POT")

        fields_shape_OT = ['ID_OT', 'Divipola', 'nom_dpto', 'nom_mpio', 'ID_instrumento', 'tipo_instrumento', 'tipo_acto_admvo', 'num_acto_admvo', 
                           'fecha_adopcion', 'estado_instrumento', 'modificacion', 'tipo_modificacion', 'tipo_vigencia', 'Instr_comple', 'generacion_pot', 
                           'estado_igac', 'estado_carto', 'formato_carto', 'escala_rural', 'escala_urbana', 'gest_riesgo', 'tiempo_gest_riesgo']
        

        # Insertar datos en POT con conversiones necesarias
        arcpy.AddMessage("Insertando datos en POT...")
        with arcpy.da.SearchCursor(tabla_OT, fields_table_OT) as sCur:
            with arcpy.da.InsertCursor(shape, fields_shape_OT) as iCur:
                for row in sCur:
                    new_row = list(row)

                    # Campos de tipo Short
                    short_fields = [
                        'tipo_instr', 'tipo_acto_', 'estado_ins', 'modificaci', 
                        'tipo_modif', 'tipo_vigen', 'Instr_comp', 'generacion','estado_iga',
                        'estado_car','formato_ca','escala_rur','escala_urb','gest_riesg','tiempo_ges'
                    ]

                    for field in short_fields:
                        index = fields_table_OT.index(field)
                        new_row[index] = is_convertible_to_int(new_row[index])

                    # Conversión del campo fecha
                    fecha_index = fields_table_OT.index('fecha_adop')
                    if new_row[fecha_index]:
                        try:
                            new_row[fecha_index] = datetime.strptime(new_row[fecha_index], "%d/%m/%Y")
                        except ValueError:
                            new_row[fecha_index] = None  # Manejar fecha inválida
                    else:
                        new_row[fecha_index] = None  # Manejar valores nulos para fecha

                    # Insertar la fila con los valores convertidos
                    iCur.insertRow(new_row)
                    arcpy.AddMessage(f"Insertado: {new_row}")
        
        arcpy.AddMessage("Inserción de datos completada.")
        
        arcpy.AddMessage("Actualizando geometrías en POT...")
        with arcpy.da.SearchCursor(munpi, ['SHAPE@', 'MpCodigo']) as sCur:
            mp_rows = [(sRow[0].projectAs(sr), sRow[1]) for sRow in sCur]
        with arcpy.da.UpdateCursor(shape, ['SHAPE@', r'DIVIPOLA']) as iCur:
            for iRow in iCur:
                for mpShape, mpCode in mp_rows:
                    if mpCode == iRow[1]:
                        iRow[0] = mpShape
                        iCur.updateRow(iRow)
                        arcpy.AddMessage(f"Geometría actualizada: Codigo DANE: {iRow[1]}")
        arcpy.AddMessage("Actualización de geometrías en Estado_Geografia completada.")



    except arcpy.ExecuteError as e:
        # En caso de errores de arcpy
        arcpy.AddError(f"Error de arcpy durante la operación: {e}")
        editor.abortOperation()  # Abortar toda la operación si hay errores críticos
    except Exception as ex:
        # Otros errores no controlados
        arcpy.AddError(f"Error inesperado: {ex}")
        editor.abortOperation()  # Abortar en caso de errores graves

    finally:
        # Asegúrate de detener la operación de edición
        if editor.isEditing:
            editor.stopEditing(True)  # True para guardar cambios

if __name__ == "__main__":
    excel = arcpy.GetParameterAsText(0)
    ruta_salida = arcpy.GetParameterAsText(1)
    bdot = arcpy.GetParameterAsText(2)
    munpi = arcpy.GetParameterAsText(3)  # Capa de municipios
    join_excel(excel, ruta_salida, bdot, munpi)
