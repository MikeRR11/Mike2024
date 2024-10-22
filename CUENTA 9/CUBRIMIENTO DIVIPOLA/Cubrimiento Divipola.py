
import arcpy
import os

# Configuración de entorno
arcpy.env.overwriteOutput = True
espacio = ".                                                                   ."
espacio2 = "-------------------------------------------------------------------------------------------------------"

# Parámetros de entrada desde la toolbox
Munpi = arcpy.GetParameterAsText(0)  # Feature de municipios
feature = arcpy.GetParameterAsText(1)  # Feature con datos
ruta_salida = arcpy.GetParameterAsText(2)  # Ruta de GDB para los resultados
arcpy.env.workspace = ruta_salida  # Volver al espacio de trabajo original

# Validación de entradas
if not os.path.exists(ruta_salida):
    arcpy.AddError(f"La ruta de salida no existe: {ruta_salida}")
    raise ValueError("Ruta de salida inválida")

#Crear feature data set
out_name = f"Procesos_Biofisicos"
# Crear Feature Dataset en la geodatabase de salida (output_gdb)
output_dataset = os.path.join(ruta_salida, out_name)

# Verificar si el Feature Dataset ya existe para evitar errores
if not arcpy.Exists(output_dataset):
    spatial_ref = arcpy.SpatialReference(9377)
    arcpy.management.CreateFeatureDataset(ruta_salida, out_name, spatial_ref)

# Lista de nombres de los feature class específicos
features_especificos = [
    "_1191_Ecosistemascontinentales",
    "_2861_SuelosIGAC",
    "_1201_Erosion",    
    "_1791_CambioC",
    "_1071_ClasificacionClimatica",
    "_1261_Inundacion"
]

# Diccionario con los campos de disolución específicos para cada feature class
dissolve_fields_dict = {
    "_1191_Ecosistemascontinentales": ["TIPO_ECOSI", "GRADO_TRAN", "ECOS_SINTE", "COBERTURA"],
    "_2861_SuelosIGAC": ["PAISAJE", "TIPO_RELIE"],
    "_1201_Erosion": ["TIPO", "CLASE","GRADO"],
    "_1791_CambioC": ["valor_ries", "vn_vs_am"],
    "_1071_ClasificacionClimatica": ["CALDASLANG"],
    "_1261_Inundacion": ["BASE2001"]
}

# Procesamiento de los shapes de puntos originales

def cubrimiento(Munpi, feature, gdb_temporal, output_dataset):

    feature_name = os.path.basename(feature)
    arcpy.AddMessage(espacio)
    arcpy.AddMessage(f"Inciando Proceso para {feature_name}")
    # Obtener el nombre del feature class
    # Realizar el clip con la capa de municipios
    clip2 = arcpy.gapro.ClipLayer(
        input_layer=feature,
        clip_layer=Munpi,
        out_feature_class=os.path.join(gdb_temporal, f"clip_{feature_name}")
    )
    arcpy.AddMessage(f"Clip nacional realizado para {feature_name}")

    # Obtener los campos de disolución específicos para este feature class
    dissolve_fields = dissolve_fields_dict.get(feature_name, None)

    # Si hay campos de disolución definidos, realizar el Dissolve
    if dissolve_fields:
        disolve = arcpy.management.Dissolve(
            in_features=clip2,
            out_feature_class=os.path.join(gdb_temporal, f"{feature_name}_Dissolve"),
            dissolve_field=dissolve_fields,
            statistics_fields=None,
            multi_part = False,
            unsplit_lines="DISSOLVE_LINES"
        )
        arcpy.AddMessage(f"Dissolve realizado para {feature_name} con campos {', '.join(dissolve_fields)}")
    else:
        arcpy.AddWarning(f"No se encontraron campos de disolución para {feature_name}. Se omite el Dissolve.")

    # Realizando intersección con los municipios
    clip = arcpy.analysis.PairwiseIntersect(
        in_features=[disolve, Munpi],
        out_feature_class=os.path.join(output_dataset, feature_name),
        join_attributes="ALL",
        output_type="INPUT"
    )

    arcpy.AddMessage(f"Clip municipal realizado para {feature_name}")

    # Añadir campos de DIVIPOLA y CUBRIMIENTO
    arcpy.management.AddField(clip, "DIVIPOLA", "TEXT")
    arcpy.management.AddField(clip, "CUBRIMIENTO", "DOUBLE")

    lista = sorted(list(set([row[0] for row in arcpy.da.SearchCursor(Munpi, ['OBJECTID'])])))

    # Permitir la iteración de cada elemento de la tabla de municipios a través de un query dinámico
    for i in lista:
        SQL = "OBJECTID = {0}".format(i)  # Comillas simples alrededor de {0} para manejar texto
        arcpy.AddMessage(f"Iniciando iterador para municipio {i} ................................")
        select_a = arcpy.management.SelectLayerByAttribute(Munpi, "NEW_SELECTION", SQL)
        select_b = arcpy.management.SelectLayerByLocation(clip, "WITHIN", select_a)

        # Actualizar campos de DIVIPOLA y CUBRIMIENTO
        with arcpy.da.SearchCursor(select_a, ['MpCodigo', 'SHAPE@AREA']) as Scur:
            for municipio in Scur:
                with arcpy.da.UpdateCursor(select_b, ["DIVIPOLA", "CUBRIMIENTO", "SHAPE@AREA"]) as Ucur:
                    for poligono in Ucur:
                        poligono[0] = municipio[0]  # Asignar el código DIVIPOLA
                        poligono[1] = (poligono[2] / municipio[1]) * 100  # Calcular porcentaje de cubrimiento
                        Ucur.updateRow(poligono)
                        if poligono[1] > 0:
                            arcpy.AddMessage(f"Datos actualizados para municipio {municipio[0]}")

    # Eliminar el clip temporal
    arcpy.management.Delete(clip2)
    arcpy.management.Delete(disolve)
    arcpy.AddMessage(espacio2)
    arcpy.AddMessage(f"Proceso finalizado para {feature_name}")

# Procesar los features filtrados

# Procesar cada feature layer
cubrimiento(Munpi, feature, ruta_salida, output_dataset)

arcpy.AddMessage("-------------------------------------------------------------------------------------------------------")
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO")





#######################################################################

#Ajustar codigo para enrutar GDB manualmente