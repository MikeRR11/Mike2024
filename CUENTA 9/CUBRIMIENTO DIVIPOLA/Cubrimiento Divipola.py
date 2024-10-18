
import arcpy
import os

# Configuración de entorno
arcpy.env.overwriteOutput = True
espacio = ".                                                                   ."
espacio2 = "-------------------------------------------------------------------------------------------------------"

# Parámetros de entrada desde la toolbox
Munpi = arcpy.GetParameterAsText(0)  # Feature de municipios
GDB_entrada = arcpy.GetParameterAsText(1)  # GDB con datos
ruta_salida = arcpy.GetParameterAsText(2)  # Ruta de salida para los resultados
arcpy.env.workspace = GDB_entrada  # Volver al espacio de trabajo original

# Validación de entradas
if not os.path.exists(ruta_salida):
    arcpy.AddError(f"La ruta de salida no existe: {ruta_salida}")
    raise ValueError("Ruta de salida inválida")

# Crear una Geodatabase temporal para almacenar los resultados
nombre_gdb = f"GDB_Servicio_Web.gdb"
gdb_temporal = os.path.join(ruta_salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb_temporal}")
arcpy.CreateFileGDB_management(ruta_salida, nombre_gdb)


#Crear feature data set

out_name = f"Procesos_Biofisicos"

# Crear Feature Dataset en la geodatabase de salida (output_gdb)
output_dataset = os.path.join(gdb_temporal, out_name)

# Verificar si el Feature Dataset ya existe para evitar errores
if not arcpy.Exists(output_dataset):
    spatial_ref = arcpy.SpatialReference(9377)
    arcpy.management.CreateFeatureDataset(gdb_temporal, out_name, spatial_ref)

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

# Buscar todos los feature datasets en la geodatabase de entrada
feature_datasets = sorted(arcpy.ListDatasets(feature_type='feature') or [""])  # Manejo de None
#arcpy.AddMessage(f"Se encontraron los siguientes feature data set: {feature_datasets}")

# Inicializar una lista para almacenar las feature classes filtradas
features_filtrados = []

# Recorrer cada feature dataset y listar las feature classes
for fd in feature_datasets:
    # Cambiar el espacio de trabajo al feature dataset actual
    arcpy.env.workspace = os.path.join(GDB_entrada, fd)
    
    # Listar las feature classes en el feature dataset
    features_encontrados = arcpy.ListFeatureClasses()
    
    # Filtrar los feature class que coincidan con los nombres en la lista
    features_filtrados.extend([f for f in features_encontrados if os.path.basename(f) in features_especificos])

# Verificar si hay features que procesar
if not features_filtrados:
    arcpy.AddError("No se encontraron los feature class específicos en la geodatabase de entrada.")
    raise ValueError("No se encontraron los feature class solicitados.")
else:
    arcpy.AddMessage(f"PROCESO EN COLA PARA LOS FEATURE CLASS ENCONTRADOS:")
    arcpy.AddMessage(features_filtrados)

def cubrimiento(Munpi, feature, gdb_temporal, output_dataset):
    feature_name = os.path.basename(feature)
    arcpy.AddMessage(espacio)
    arcpy.AddMessage(f"Inciando Proceso para {feature_name}")

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
      # Si no hay campos, usamos directamente el clip
    if dissolve_fields:
        disolve = arcpy.analysis.PairwiseDissolve(
            in_features=clip2,
            out_feature_class=os.path.join(gdb_temporal, f"{feature_name}_Dissolve"),
            dissolve_field=dissolve_fields,
            statistics_fields=None,
            multi_part="MULTI_PART"
        )
        arcpy.AddMessage(f"Dissolve realizado para {feature_name} con campos {', '.join(dissolve_fields)}")


    # Realizando intersección con los municipios
    clip = arcpy.analysis.Intersect(
        in_features=[disolve, Munpi],
        out_feature_class=os.path.join(output_dataset, feature_name),
        join_attributes="ONLY_FID",
        cluster_tolerance=None,
        output_type="INPUT"
    )
    arcpy.AddMessage(f"Clip municipal realizado para {feature_name}")

    # Añadir campos de DIVIPOLA y CUBRIMIENTO
    arcpy.management.AddField(clip, "DIVIPOLA", "TEXT")
    arcpy.management.AddField(clip, "CUBRIMIENTO", "DOUBLE")

    lista = sorted(list(set([row[0] for row in arcpy.da.SearchCursor(Munpi, ['MpNombre'])])))

    # Iterar por cada municipio
    for i in lista:
        SQL = "MpNombre = '{0}'".format(i)  # Comillas simples alrededor de {0} para manejar texto
        arcpy.management.SelectLayerByAttribute(Munpi, 'CLEAR_SELECTION')
        arcpy.management.SelectLayerByAttribute(clip, 'CLEAR_SELECTION')
        arcpy.AddMessage(f"Iniciando iterador para municipio {i} ...")
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

    # Eliminar capas temporales después del procesamiento
    arcpy.management.Delete(clip2)
    arcpy.management.Delete(disolve)  # Asegúrate de eliminar el dissolve
    arcpy.AddMessage(espacio2)
    arcpy.AddMessage(f"Proceso finalizado para {feature_name}")

# Procesar los features filtrados
for feature in features_filtrados:
    cubrimiento(Munpi, feature, gdb_temporal, output_dataset)

arcpy.AddMessage("-------------------------------------------------------------------------------------------------------")
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO")
