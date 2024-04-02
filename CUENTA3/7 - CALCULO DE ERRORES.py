import arcpy, os, time

carpeta_origen = arcpy.GetParameterAsText(5)
gdb_origen = arcpy.GetParameterAsText(0)
gdb_dataReview = arcpy.GetParameterAsText(2)
gdb_inconsistencias = arcpy.GetParameterAsText(1)
marcos_control = arcpy.GetParameterAsText(3)
archivo_txt = arcpy.GetParameterAsText(4)
ws_inconsistencias = os.path.join(gdb_inconsistencias, "Inconsistencia", "Inconsistencias_Carto")

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
linea_puntos = ".............................................................................."

def crear_gdb(carpeta_origen):
    try:
        gdb_name = "fGDB.gdb"
        gdb_path = os.path.join(carpeta_origen, gdb_name)

        if arcpy.Exists(gdb_path):
            arcpy.Delete_management(gdb_path)
            arcpy.AddMessage(f"Geodatabase '{gdb_name}' existente eliminado.")

        arcpy.management.CreateFileGDB(carpeta_origen, gdb_name)
        arcpy.AddMessage(f"{linea_puntos}")
        #arcpy.AddMessage(f"Geodatabase '{gdb_name}' creada exitosamente.\n\n")
        return gdb_path
    except arcpy.ExecuteError:
        arcpy.AddMessage(f"Error al crear la geodatabase: {arcpy.GetMessages(2)}")
    except Exception as e:
        arcpy.AddMessage(f"Error inesperado: {e}")
        
        
def reconstruirIndiceEspacial(gdb_origen):
    arcpy.env.workspace = gdb_origen
    fc_inconsistencias = os.path.join(gdb_origen, "Inconsistencia", "Inconsistencias_Carto")

    try:
        if arcpy.Exists(fc_inconsistencias):
            arcpy.management.RemoveSpatialIndex(fc_inconsistencias)
            arcpy.management.AddSpatialIndex(fc_inconsistencias)
            arcpy.AddMessage(f"{linea_puntos}")
            #print(f"Índice espacial removido y agregado para {fc_inconsistencias}")
        else:
            print(f"Feature class {fc_inconsistencias} no encontrado.")
    except Exception as e:
        print(f"Error al modificar índice espacial de {fc_inconsistencias}: {e}")


def validar_y_exportar_errores(gdb_origen, gdb_destino):
    try:
        arcpy.env.workspace = gdb_origen
        datasets = arcpy.ListDatasets('*', 'Feature')

        for dataset in datasets:
            topology_name = f"{dataset}_topology"
            topology_path = os.path.join(gdb_origen, dataset, topology_name)

            if arcpy.Exists(topology_path):
                arcpy.ValidateTopology_management(in_topology=topology_path)
                #arcpy.AddMessage(f"Topología {topology_name} validada.")
                errores_fc = f"{topology_name}_errores"
                arcpy.ExportTopologyErrors_management(topology_path, gdb_destino, out_basename=errores_fc)
                #arcpy.AddMessage(f"Errores de la topología {topology_name} exportados correctamente.\n\n")
        arcpy.AddMessage(f"{linea_puntos}")
            #else:
                #arcpy.AddMessage(f"La topología {topology_name} no existe en el dataset {dataset}.\n\n")
    except arcpy.ExecuteError:
        arcpy.AddMessage(f"Error al validar y exportar errores: {arcpy.GetMessages(2)}")
    except Exception as e:
        arcpy.AddMessage(f"Error inesperado: {e}")

def crear_feature_template(gdb_path, fc_ini, fc_nombre):
    try:
        arcpy.env.workspace = gdb_path

        feature_classes = arcpy.ListFeatureClasses()

        template_feature_class = None
        for fc in feature_classes:
            if fc.endswith(fc_ini):
                template_feature_class = fc
                break

        if template_feature_class:
            arcpy.CreateFeatureclass_management(
                out_path=gdb_path,
                out_name=fc_nombre,
                template=template_feature_class
            )
        #else:
            #arcpy.AddMessage(f"No se encontró ningún feature class cuyo nombre termine en '{fc_ini}'.\n\n")
    except arcpy.ExecuteError:
        arcpy.AddMessage(f"Error al crear feature template: {arcpy.GetMessages(2)}")
    except Exception as e:
        arcpy.AddMessage(f"Error inesperado: {e}")

def insertar_datos_fc(gdb_path, fc_destino, fc_name):
    try:
        arcpy.env.workspace = gdb_path

        feature_classes = arcpy.ListFeatureClasses()

        for source_fc in feature_classes:
            if source_fc.endswith(fc_name):
                #arcpy.AddMessage(f"Procesando {source_fc}...")
                arcpy.Append_management(source_fc, fc_destino, "NO_TEST")
        #arcpy.AddMessage("Datos anexados correctamente.\n\n")
        arcpy.AddMessage(f"{linea_puntos}")
    except arcpy.ExecuteError:
        arcpy.AddMessage(f"Error al insertar datos: {arcpy.GetMessages(2)}")
    except Exception as e:
        arcpy.AddMessage(f"Error inesperado: {e}")
        
def eliminar_entidades_especificas(gdb_path):
    try:
        arcpy.env.workspace = gdb_path

        # Procesar tp_point
        fc_point = "tp_point"
        point_conditions = ["esriTRTLineNoDangles", "esriTRTLineNoPseudos"]
        if arcpy.Exists(os.path.join(gdb_path, fc_point)):
            with arcpy.da.UpdateCursor(fc_point, ["RuleType"]) as cursor:
                for row in cursor:
                    if row[0] in point_conditions:
                        cursor.deleteRow()
            #print(f"Entidades eliminadas en '{fc_point}' que cumplen con las condiciones.")
            arcpy.AddMessage(f"{linea_puntos}")
            
        fc_line = "tp_line"
        line_conditions = [
            ('Cnivel', 'Must Not Have Dangles'), ('Lvia', 'Must Not Self Overlap'),
            ('Cnivel', 'Must Not Self Overlap'), ('Puente_L', 'Must Not Have Dangles'),
            ('LDTerr', 'Must Not Have Dangles'), ('Puente_L', 'Must Not Self Overlap'),
            ('LDTerr', 'Must Not Self Overlap'), ('SVial', 'Must Not Self Overlap'),
            ('DAgua_L', 'Must Not Have Dangles'), ('SVial', 'Must Not Be Single Part'),
            ('DAgua_L', 'Must Not Self Overlap'), ('SVial', 'Must Not Have Dangles'),
            ('Drenaj_L', 'Must Not Have Dangles'), ('Telefe', 'Must Not Have Dangles'),
            ('Drenaj_L', 'Must Not Self Overlap'), ('Telefe', 'Must Not Self Overlap'),
            ('LCoste', 'Must Not Have Dangles'), ('Tunel', 'Must Not Self Overlap'),
            ('LCoste', 'Must Not Self Overlap'), ('Tunel', 'Must Not Have Dangles'),
            ('RATens', 'Must Not Have Dangles'), ('VFerre', 'Must Not Self Overlap'),
            ('RATens', 'Must Not Self Overlap'), ('VFerre', 'Must Not Have Dangles'),
            ('Tuberi', 'Must Not Have Dangles'), ('Via', 'Must Not Have Dangles'),
            ('Tuberi', 'Must Not Self Overlap'), ('Via', 'Must Not Self Overlap'),
            ('Tuberi', 'Must Not Be Single Part'), ('Cerca', 'Must Not Self Overlap'),
            ('Fronte', 'Must Not Have Dangles'), ('Cerca', 'Must Not Have Dangles'),
            ('Fronte', 'Must Not Self Overlap'), ('LDemar', 'Must Not Have Dangles'),
            ('LLimit', 'Must Not Have Dangles'), ('LDemar', 'Must Not Self Overlap'),
            ('LLimit', 'Must Not Self Overlap'), ('Muro', 'Must Not Self Overlap'),
            ('Ciclor', 'Must Not Self Overlap'), ('Muro', 'Must Not Have Pseudo Nodes'),
            ('Ciclor', 'Must Not Have Dangles'), ('Muro', 'Must Not Have Dangles'),
            ('Lvia', 'Must Not Have Dangles'), ('Terrap', 'Must Not Self Overlap'),
            ('Lvia', 'Must Not Have Pseudo Nodes'), ('Terrap', 'Must Not Have Dangles')
        ]
        if arcpy.Exists(os.path.join(gdb_path, fc_line)):
            with arcpy.da.UpdateCursor(fc_line, ["OriginObjectClassName", "RuleType"]) as cursor:
                for row in cursor:
                    if (row[0], row[1]) in line_conditions:
                        cursor.deleteRow()
            #print(f"Entidades eliminadas en '{fc_line}' que cumplen con las condiciones.")
            arcpy.AddMessage(f"{linea_puntos}")
            
        fc_poly = "tp_poly"
        line_conditions = [
            ('Zverde', 'Must Not Overlap with Bosque'), ('Mangla', 'Must Not Overlap With Humeda'),
            ('Humeda', 'Must Not Overlap With DAgua_R'), ('Mangla', 'Must Not Overlap With Drenaj_R'),
            ('Isla', 'Must Not Overlap With DAgua_R'), ('Mangla', 'Must Not Overlap With DAgua_R'),
            ('Mangla', 'Must Not Overlap With Isla')
        ]
        if arcpy.Exists(os.path.join(gdb_path, fc_poly)):
            with arcpy.da.UpdateCursor(fc_poly, ["OriginObjectClassName", "RuleType"]) as cursor:
                for row in cursor:
                    if (row[0], row[1]) in line_conditions:
                        cursor.deleteRow()
            #print(f"Entidades eliminadas en '{fc_poly}' que cumplen con las condiciones.")
            arcpy.AddMessage(f"{linea_puntos}")
            
    except arcpy.ExecuteError:
        print(f"Error al eliminar entidades: {arcpy.GetMessages(2)}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def crear_buffer(gdb_path, fc_names, buffer_distance):
    try:
        arcpy.env.workspace = gdb_path

        for fc_name in fc_names:
            feature_class_path = os.path.join(gdb_path, fc_name)
            buffer_fc_name = f"{fc_name}_buffer"
            buffer_fc_path = os.path.join(gdb_path, buffer_fc_name)

            if arcpy.Exists(feature_class_path):
                arcpy.analysis.Buffer(feature_class_path, buffer_fc_path, buffer_distance)
                #arcpy.AddMessage(f"Buffer de {buffer_distance} creado para '{fc_name}' y guardado como '{buffer_fc_name}'.\n\n")
            else:
                arcpy.AddMessage(f"El feature class '{fc_name}' no existe en la geodatabase.")
        arcpy.AddMessage(f"{linea_puntos}")
    except arcpy.ExecuteError:
        arcpy.AddMessage(f"Error al crear buffer: {arcpy.GetMessages(2)}")
    except Exception as e:
        arcpy.AddMessage(f"Error inesperado: {e}")
   
        
def insertar_inconsistencias(gdb_origen,gdb_destino):
    
    fc_inconsistencias = os.path.join(gdb_destino, "Inconsistencia", "Inconsistencias_Carto")

    fcs_origen = ["tp_point_buffer", "tp_line_buffer", "tp_poly"]

    lista_origen = ['SHAPE@', 'OriginObjectClassName', 'OriginObjectID', 'RuleDescription']
    lista_destino = ['SHAPE@', 'Lote_Inconsistencia', 'ID_Proyecto', 'Obs', 'Inspeccion', 'Elemento_Calidad', 'Tipo_Inconsistencia', 'Correccion']

    count_inserciones = 0

    nombres_dominio = {
        1: 'Area_Extra',
        2: 'Bosque',
        3: 'Zona_Verde',
        4: 'Curva_Nivel',
        5: 'LD_Terreno',
        6: 'Marco_referencia',
        7: 'Banco_Arena',
        8: 'Deposito_Agua_P',
        9: 'Deposito_Agua_R',
        10: 'Drenaje_L',
        11: 'Drenaje_R',
        12: 'Humedal',
        13: 'Isla',
        14: 'Manglar',
        15: 'Punto_Dist',
        16: 'Pozo',
        17: 'Red_Alta_Tens',
        18: 'Tapa_Servi',
        19: 'Nombre_Geo',
        20: 'Ciclorruta',
        21: 'Limite_Via',
        22: 'Puente_L',
        23: 'Puente_P',
        24: 'Separador_Vial',
        25: 'Tunel',
        26: 'Vferre',
        27: 'Via',
        28: 'Cerca',
        29: 'Const_P',
        30: 'Const_R',
        31: 'Muro',
        32: 'Piscina',
        33: 'Zona_Dura',
        34: 'DAgua_L',
        35: 'Indice',
        36: 'Tuberi',
        37: 'Depart',
        38: 'LLimit',
        39: 'Fronte',
        40: 'MDANMu',
        41: 'Telefe',
        42: 'Terrap',
        43: 'LDemar'
    }

    mapeo_valores = {v: k for k, v in nombres_dominio.items()}

    mapeo_descripciones = {
        "Must Not Intersect": "No debe cruzarse con {0}",
        "Must Not Self-Intersect": "No debe intersectarse con {0}",
        "Must Not Intersect Or Touch Interior": "No debe cruzarse ni tocar el interior de {0}",
        "Must Not Overlap With":  "No debe superponerse con {0}",
        "Must Be Covered By Feature Class Of": "Debe estar cubierto por la clase de característica de {0}",
        "Must Not Overlap": "No debe superponerse con {0}",
    }

    edit = arcpy.da.Editor(gdb_destino)
    edit.startEditing(False, True)
    edit.startOperation()

    #arcpy.AddMessage("Inicio del proceso de inserción de datos...")

    try:
        for fc_origen_name in fcs_origen:
            fc_origen = os.path.join(gdb_origen, fc_origen_name)
            with arcpy.da.SearchCursor(fc_origen, lista_origen) as sCur:
                with arcpy.da.InsertCursor(fc_inconsistencias, lista_destino) as iCur:
                    for row in sCur:
                        geom_proyectada = row[0].projectAs(arcpy.SpatialReference(9377))
                        lote_inconsistencia = mapeo_valores.get(row[1], 0)
                        nombre_lote_inconsistencia = nombres_dominio.get(lote_inconsistencia, "Desconocido")
                        rule_description = row[3]
                        if rule_description in mapeo_descripciones:
                            obs = mapeo_descripciones[rule_description].format(nombre_lote_inconsistencia)
                        else:
                            obs = rule_description
                        row_destino = [geom_proyectada, lote_inconsistencia, row[2], obs, 1, 1, 3, 1]
                        iCur.insertRow(tuple(row_destino))
                        
                        #arcpy.AddMessage(f"Insertada inconsistencia para el elemento con ID: {row[2]}, Tipo de Inconsistencia: {obs}")
                        count_inserciones += 1
                    
        edit.stopOperation()
        edit.stopEditing(True)
        arcpy.AddMessage(f"{linea_puntos}")
        #arcpy.AddMessage(f"Proceso finalizado exitosamente. Inserciones realizadas : {count_inserciones}\n\n")

    except Exception as e:
        edit.abortOperation()
        edit.stopEditing(False)
        arcpy.AddMessage(f"Se produjo un error: {e}")
        
def eliminar_gdb(gdb_path):

    try:
        if arcpy.Exists(gdb_path):
            arcpy.Delete_management(gdb_path)
            arcpy.AddMessage(f"{linea_puntos}")
            #arcpy.AddMessage(f"Geodatabase {gdb_path} eliminada correctamente.")
    except Exception as e:
        arcpy.AddMessage(f"Error al eliminar la geodatabase: {e}")
        
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------

def buffer_fc(gdb_origen):

    arcpy.env.workspace = gdb_origen
    feature_classes = arcpy.ListFeatureClasses()

    for fc in feature_classes:
        desc = arcpy.Describe(fc)
        if desc.shapeType in ['Point', 'Multipoint', 'Polyline']:
            temp_output_fc = f"{fc}_TempBuffer"
            
            if arcpy.Exists(temp_output_fc):
                arcpy.Delete_management(temp_output_fc)
                
            arcpy.Buffer_analysis(fc, temp_output_fc, "5 meters")
            
            if arcpy.Exists(fc):
                arcpy.Delete_management(fc)           
            arcpy.Rename_management(temp_output_fc, fc)
            
    arcpy.AddMessage(f"{linea_puntos}")
            #print(f"Buffer creado y reemplazado para {fc}")
        
        
def insertar_inconsistencias_dw(gdb_origen, gdb_destino):
    
    fc_inconsistencias = os.path.join(gdb_destino, "Inconsistencia", "Inconsistencias_Carto")

    arcpy.env.workspace = gdb_origen
    fcs_origen = arcpy.ListFeatureClasses()

    lista_origen = ['SHAPE@', 'FC_Origen']
    lista_destino = ['SHAPE@', 'Lote_Inconsistencia', 'Obs', 'Inspeccion', 'Elemento_Calidad', 'Tipo_Inconsistencia', 'Correccion']

    count_inserciones = 0
    errores = 0

    nombres_dominio = {
        1: 'Area_Extra',
        2: 'Bosque',
        3: 'Zona_Verde',
        4: 'Curva_Nivel',
        5: 'LD_Terreno',
        6: 'Marco_referencia',
        7: 'Banco_Arena',
        8: 'Deposito_Agua_P',
        9: 'Deposito_Agua_R',
        10: 'Drenaje_L',
        11: 'Drenaje_R',
        12: 'Humedal',
        13: 'Isla',
        14: 'Manglar',
        15: 'Punto_Dist',
        16: 'Pozo',
        17: 'Red_Alta_Tens',
        18: 'Tapa_Servi',
        19: 'Nombre_Geo',
        20: 'Ciclorruta',
        21: 'Limite_Via',
        22: 'Puente_L',
        23: 'Puente_P',
        24: 'Separador_Vial',
        25: 'Tunel',
        26: 'Vferre',
        27: 'Via',
        28: 'Cerca',
        29: 'Const_P',
        30: 'Const_R',
        31: 'Muro',
        32: 'Piscina',
        33: 'Zona_Dura',
        34: 'DAgua_L',
        35: 'Indice',
        36: 'Tuberi',
        37: 'Depart',
        38: 'LLimit',
        39: 'Fronte',
        40: 'MDANMu',
        41: 'Telefe',
        42: 'Terrap',
        43: 'LDemar'
    }

    mapeo_valores = {v: k for k, v in nombres_dominio.items()}

    edit = arcpy.da.Editor(gdb_destino)
    edit.startEditing(False, True)
    edit.startOperation()

    #arcpy.AddMessage("Inicio del proceso de inserción de datos...")

    for fc_origen_name in fcs_origen:
        try:
            fc_origen = os.path.join(gdb_origen, fc_origen_name)
            with arcpy.da.SearchCursor(fc_origen, lista_origen) as sCur, arcpy.da.InsertCursor(fc_inconsistencias, lista_destino) as iCur:
                for row in sCur:
                    geom_proyectada = row[0].projectAs(arcpy.SpatialReference(9377))
                    lote_inconsistencia = mapeo_valores.get(row[1], 0)
                    parts = fc_origen_name.split('_')
                    formatted_name = ' y '.join(parts)
                    obs = f"No se puede cruzar {formatted_name}"
                    row_destino = [geom_proyectada, lote_inconsistencia, obs, 1, 1, 3, 1]
                    iCur.insertRow(tuple(row_destino))

                    count_inserciones += 1

        except Exception as e:
            arcpy.AddMessage(f"Error en {fc_origen_name}: {e}")
            errores += 1
            continue

    edit.stopOperation()
    edit.stopEditing(True)
    arcpy.AddMessage(f"{linea_puntos}")
    #arcpy.AddMessage(f"Proceso finalizado. Inserciones realizadas: {count_inserciones}. Errores encontrados: {errores}")

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------

def erroresDominio(txt):

    if not txt:
        return 0  # Retorna 0 en lugar de None

    contador_errores = 0
    with open(txt, 'r') as archivo:
        for linea in archivo:
            contador_errores += 1

    return contador_errores

#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------

def contar_entidades(workspace_e, fc_rectangulos):
    try:
        arcpy.env.workspace = workspace_e
        total_count = 0
        cercas_count = 0
        bosques_count = 0
        total_entidades_gdb = 0

        arcpy.MakeFeatureLayer_management(fc_rectangulos, "rectangulos_layer")

        datasets = arcpy.ListDatasets()
        for dataset in datasets:
            feature_classes = arcpy.ListFeatureClasses(feature_dataset=dataset)
            for fc in feature_classes:
                total_entidades_gdb += int(arcpy.GetCount_management(fc).getOutput(0))
                arcpy.MakeFeatureLayer_management(os.path.join(workspace_e, dataset, fc), "fc_layer")
                arcpy.SelectLayerByLocation_management("fc_layer", "INTERSECT", "rectangulos_layer")
                count = int(arcpy.GetCount_management("fc_layer").getOutput(0))
                total_count += count

                arcpy.Delete_management("fc_layer")

        arcpy.MakeFeatureLayer_management("ViviendaCiudadTerritorio\\Cerca", "cercas_layer")
        arcpy.SelectLayerByLocation_management("cercas_layer", "INTERSECT", "rectangulos_layer")
        cercas_count = int(arcpy.GetCount_management("cercas_layer").getOutput(0))

        arcpy.MakeFeatureLayer_management("CoberturaTierra\\Bosque", "bosques_layer")
        arcpy.SelectLayerByLocation_management("bosques_layer", "INTERSECT", "rectangulos_layer")
        bosques_count = int(arcpy.GetCount_management("bosques_layer").getOutput(0))

        arcpy.Delete_management("cercas_layer")
        arcpy.Delete_management("bosques_layer")
        arcpy.Delete_management("rectangulos_layer")

        resultados = {
            'total_entidades_mc': total_count,
            'cercas_bosques_count': cercas_count + bosques_count,
            'total_entidades_gdb': total_entidades_gdb,
            'total_restante': total_count - (cercas_count + bosques_count)
        }
        return resultados
    except Exception as e:
        arcpy.AddMessage(f"Error en contar_entidades: {e}")
        return None

def contar_inconsistencias(workspace_i):
    try:
        inconsistencias_fc = workspace_i
        count_inconsistencias_omision = 0
        count_bosque_cerca_omision = 0
        count_inconsistencias_comision = 0
        count_bosque_cerca_comision = 0
        count_inconsistencias_topologia = 0
        count_inconsistencias_tematica_cl = 0
        count_inconsistencias_tematica_ac = 0

        consulta_omision = "Tipo_Inconsistencia = 1 AND Elemento_Calidad = 0"
        consulta_comision = "Tipo_Inconsistencia = 2 AND Elemento_Calidad = 0"
        consulta_topologia = "Tipo_Inconsistencia = 3 AND Elemento_Calidad = 1"
        consulta_tematica_cl = "Elemento_Calidad = 4 AND Tipo_Inconsistencia = 0"
        consulta_tematica_ac = "Elemento_Calidad = 4 AND Tipo_Inconsistencia = 1"

        with arcpy.da.SearchCursor(inconsistencias_fc, ["Tipo_Inconsistencia", "Elemento_Calidad", "Lote_Inconsistencia"], where_clause=consulta_omision) as cursor:
            for fila in cursor:
                count_inconsistencias_omision += 1
                if fila[2] == 2 or fila[2] == 28:
                    count_bosque_cerca_omision += 1

        with arcpy.da.SearchCursor(inconsistencias_fc, ["Tipo_Inconsistencia", "Elemento_Calidad", "Lote_Inconsistencia"], where_clause=consulta_comision) as cursor:
            for fila in cursor:
                count_inconsistencias_comision += 1
                if fila[2] == 2 or fila[2] == 28:
                    count_bosque_cerca_comision += 1

        with arcpy.da.SearchCursor(inconsistencias_fc, ["Tipo_Inconsistencia", "Elemento_Calidad"], where_clause=consulta_topologia) as cursor:
            for fila in cursor:
                count_inconsistencias_topologia += 1

        with arcpy.da.SearchCursor(inconsistencias_fc, ["Tipo_Inconsistencia", "Elemento_Calidad"], where_clause=consulta_tematica_cl) as cursor:
            for fila in cursor:
                count_inconsistencias_tematica_cl += 1
                
        with arcpy.da.SearchCursor(inconsistencias_fc, ["Tipo_Inconsistencia", "Elemento_Calidad"], where_clause=consulta_tematica_ac) as cursor:
            for fila in cursor:
                count_inconsistencias_tematica_ac += 1

        resultados = {
            'total_omision': count_inconsistencias_omision,
            'cercas_bosques_omision': count_bosque_cerca_omision,
            'total_restante_omision': count_inconsistencias_omision - count_bosque_cerca_omision,
            'total_comision': count_inconsistencias_comision,
            'cercas_bosques_comision': count_bosque_cerca_comision,
            'total_restante_comision': count_inconsistencias_comision - count_bosque_cerca_comision,
            'total_topologia': count_inconsistencias_topologia,
            'total_tematica_clasificacion': count_inconsistencias_tematica_cl,
            'total_tematica_cualitativos' : count_inconsistencias_tematica_ac
        }
        return resultados
    except Exception as e:
        arcpy.AddMessage(f"Error en contar_inconsistencias: {e}")
        return None

def calcular_metricas(resultados_i, resultados_e, resultado_d):
    try:
        omision_bosque_cerca = (resultados_i['cercas_bosques_omision'] / (resultados_e['cercas_bosques_count'] + resultados_i['cercas_bosques_omision']))*100
        omision_restante = (resultados_i['total_restante_omision'] / (resultados_e['total_restante'] + resultados_i['total_restante_omision']))*100
        comision_bosque_cerca = (resultados_i['cercas_bosques_comision'] / (resultados_e['cercas_bosques_count'] - resultados_i['cercas_bosques_comision']))*100
        comision_restante = (resultados_i['total_restante_comision'] / (resultados_e['total_restante'] - resultados_i['total_restante_comision']))*100
        consistencia_logica = (resultados_i['total_topologia'] / resultados_e['total_entidades_gdb'])*100
        exactitud_tematica_cl = (resultados_i['total_tematica_clasificacion'] / resultados_e['total_entidades_mc'])*100
        exactitud_tematica_ac = (resultados_i['total_tematica_cualitativos'] / resultados_e['total_entidades_mc'])*100
        conteo_dominios = (resultado_d / resultados_e['total_entidades_gdb'])*100
        
        return {
            'omision_bosque_cerca': omision_bosque_cerca,
            'omision_restante': omision_restante,
            'comision_bosque_cerca': comision_bosque_cerca,
            'comision_restante': comision_restante,
            'consistencia_logica': consistencia_logica,
            'total_tematica_clasificacion': exactitud_tematica_cl,
            'total_tematica_cualitativos' : exactitud_tematica_ac,
            'errores_validacion_dominios' : conteo_dominios
        }
    except Exception as e:
        arcpy.AddMessage(f"Error al calcular métricas: {e}")
        return None
        
def main():
    linea_guiones = "------------------------------------------------------------------------------"
    longitud_linea = len(linea_guiones)
    start_time = time.time()
    try:
        arcpy.AddMessage(f"{linea_guiones}")
        texto1 = ["INICIANDO TOOLBOX","Calculando Inconsistencias", "Contando Inconsistencias", "Calculando Métricas",
                  "Inconsistencias Calculadas", "Inconsistencias Contadas", "Contando Entidades", "Entidades Contadas",
                  "Métricas calculadas", "Escribiendo en el archivo de reporte", "Reporte Completado", "TOOLBOX COMPLETADO CON EXITO!"]
        arcpy.AddMessage(f"{texto1[0]:.^{longitud_linea}}\n{linea_guiones}\n{linea_guiones}")
        arcpy.AddMessage(f"{texto1[1]:.^{longitud_linea}}\n{linea_guiones}")

        reconstruirIndiceEspacial(gdb_inconsistencias)
        nueva_gdb = crear_gdb(carpeta_origen)
        if nueva_gdb:
            validar_y_exportar_errores(gdb_origen, nueva_gdb)
            fc_initial = [("point", "tp_point"), ("line", "tp_line"), ("poly", "tp_poly")]
            for template_name, new_name in fc_initial:
                crear_feature_template(nueva_gdb, template_name, new_name)
            fc_errores = [("tp_point", "errores_point"), ("tp_line", "errores_line"), ("tp_poly", "errores_poly")]
            for fc_destino, fc_errores in fc_errores:
                insertar_datos_fc(nueva_gdb, fc_destino, fc_errores)
            eliminar_entidades_especificas(nueva_gdb)
            fc_names = ["tp_point", "tp_line"]
            crear_buffer(nueva_gdb, fc_names, "50 Meters")
            insertar_inconsistencias(nueva_gdb, gdb_inconsistencias)
        eliminar_gdb(nueva_gdb)
        
        buffer_fc(gdb_dataReview)
        insertar_inconsistencias_dw(gdb_dataReview, gdb_inconsistencias)
        
        resultadosDominios = erroresDominio(archivo_txt)
        
        arcpy.AddMessage(f"{texto1[4]:.^{longitud_linea}}\n{linea_guiones}\n{linea_guiones}")
        
        nombre_archivo = "reporte.txt"
        ruta_completa = os.path.join(carpeta_origen, nombre_archivo)
        
        gdb_nom = os.path.basename(gdb_origen)
        nombre_gdb = os.path.splitext(gdb_nom)[0]
        tipo_gdb = "File Geodatabase"
        
        arcpy.AddMessage(f"{texto1[2]:.^{longitud_linea}}\n{linea_guiones}")       
        resultados_i = contar_inconsistencias(ws_inconsistencias)
        arcpy.AddMessage(f"{texto1[5]:.^{longitud_linea}}\n{linea_guiones}\n{linea_guiones}")

        arcpy.AddMessage(f"{texto1[6]:.^{longitud_linea}}\n{linea_guiones}")
        resultados_e = contar_entidades(gdb_origen, marcos_control)
        arcpy.AddMessage(f"{texto1[7]:.^{longitud_linea}}\n{linea_guiones}\n{linea_guiones}")
        
        if resultados_i is not None and resultados_e is not None:
            arcpy.AddMessage(f"{texto1[3]:.^{longitud_linea}}\n{linea_guiones}")
            metricas = calcular_metricas(resultados_i, resultados_e, resultadosDominios)
            if metricas is not None:
                arcpy.AddMessage(f"{texto1[8]:.^{longitud_linea}}\n{linea_guiones}\n{linea_guiones}\n{texto1[9]:.^{longitud_linea}}")
                with open(ruta_completa, 'w') as archivo:
                    resulwrite = ["RESULTADO DE INCONSISTENCIAS", "RESULTADO DE ENTIDADES","CÁLCULOS DE MÉTRICAS"]
                    #Encabezado Reporte
                    archivo.write(f"{'REPORTE TOTALIZACION DE INCONSISTENCIAS':.^78}\n")
                    archivo.write(f"{linea_guiones}\n\n")
                    archivo.write(f"Datos Generales Base de Datos Vectorial\n")
                    archivo.write(f"Nombre: \"{nombre_gdb}\"\n")
                    archivo.write(f"Tipo: {tipo_gdb}\n\n")
                    archivo.write(f"{linea_guiones}\n")#
                    archivo.write(f"{linea_guiones}\n{resulwrite[0]:.^{longitud_linea}}\n")
                    for clave, valor in resultados_i.items():
                        archivo.write(f'{clave}: {valor}\n')
                    archivo.write(f"{linea_guiones}\n{linea_guiones}\n")
                    archivo.write(f"{resulwrite[1]:.^{longitud_linea}}\n")
                    for clave, valor in resultados_e.items():
                        archivo.write(f'{clave}: {valor}\n')
                    archivo.write(f"{linea_guiones}\n{linea_guiones}\n")
                    archivo.write(f"{resulwrite[2]:.^{longitud_linea}}\n")
                    archivo.write(f"Omisión Bosque Cerca: {metricas['omision_bosque_cerca']:.1f}%\n")
                    archivo.write(f"Omisión Restante: {metricas['omision_restante']:.1f}%\n")
                    archivo.write(f"Comisión Bosque Cerca: {metricas['comision_bosque_cerca']:.1f}%\n")
                    archivo.write(f"Comisión Restante: {metricas['comision_restante']:.1f}%\n")
                    archivo.write(f"Consistencia Lógica: {metricas['consistencia_logica']:.1f}%\n")
                    archivo.write(f"Exactitud Tematica Clasificación: {metricas['total_tematica_clasificacion']:.1f}%\n")
                    archivo.write(f"Exactitud Tematica Atributo Cualitativo: {metricas['total_tematica_cualitativos']:.1f}%\n")
                    archivo.write(f"Metricas Dominios: {metricas['errores_validacion_dominios']:.1f}%\n")
                    archivo.write(f"{linea_guiones}\n{linea_guiones}\n")
                arcpy.AddMessage(f"{texto1[10]:.^{longitud_linea}}\n{linea_guiones}\n{linea_guiones}")

    except Exception as e:
        arcpy.AddMessage(f"Error en la función principal: {e}")
    finally:
        end_time = time.time()
        tiempo_ejecucion_min = int((end_time - start_time) // 60)
        tiempo_ejecucion_sec = int((end_time - start_time) % 60)
        arcpy.AddMessage(f"{texto1[11]:.^{longitud_linea}}\n{linea_guiones}")
        duracion_toolbox = f"Tiempo de ejecución: {tiempo_ejecucion_min} min {tiempo_ejecucion_sec} seg"
        arcpy.AddMessage(f"{duracion_toolbox:.^{longitud_linea}}\n{linea_guiones}")

if __name__ == "__main__":
    main()