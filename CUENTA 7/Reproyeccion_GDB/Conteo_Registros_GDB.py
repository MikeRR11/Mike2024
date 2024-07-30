import arcpy
import os

arcpy.env.overwriteOutput = True

inGDB = arcpy.GetParameterAsText(0)  
xml = arcpy.GetParameterAsText(1)
outXML = arcpy.GetParameterAsText(2)
repair = arcpy.GetParameterAsText(3)

def repair_geometry(feature_classes):
    for fc in feature_classes:
        try:
            arcpy.AddMessage(f"Reparando geometría para: {fc}")
            arcpy.management.RepairGeometry(fc)
            arcpy.AddMessage(f"Geometría reparada para: {fc}")
        except arcpy.ExecuteError:
            arcpy.AddError(f"Error al reparar geometría para {fc}")

def contar_registros(inGDB, outXML):

    arcpy.AddMessage(f"Contando registros de: {inGDB}")
    arcpy.AddMessage(f"--------------------------------------------------------")
    arcpy.env.workspace = inGDB
    
    # Listar todos los datasets en la geodatabase y ordenarlos alfabéticamente
    datasets = sorted(arcpy.ListDatasets(feature_type='feature') or [""])  # Manejo de None
    
    # Diccionario para almacenar los resultados
    resultados = {}
    total_registros = 0  # Variable para contar el total de registros
    
    for dataset in datasets:
        resultados[dataset] = {}
        total_por_dataset = 0  # Contador para el total por dataset
        
        # Listar todas las clases de entidad dentro de cada dataset y ordenarlas alfabéticamente
        feature_classes = sorted(arcpy.ListFeatureClasses(feature_dataset=dataset))
        
        # Reparar geometría antes de contar los registros
        if repair == "true":
            full_fc_paths = [os.path.join(inGDB, dataset, fc) for fc in feature_classes]
            repair_geometry(full_fc_paths)
        else:
            pass
        
        for fc in feature_classes:
            try:
                # Contar los registros en cada clase de entidad
                fc_path = os.path.join(inGDB, dataset, fc)
                count = int(arcpy.management.GetCount(fc_path).getOutput(0))
                resultados[dataset][fc] = count
                total_por_dataset += count  # Sumar al total por dataset
            except arcpy.ExecuteError:
                arcpy.AddError(f"Error al contar registros para {fc} en {dataset}")
        
        # Añadir el total por dataset al total general
        total_registros += total_por_dataset
        # Imprimir el total de registros por dataset
        arcpy.AddMessage(f"Total de registros en el dataset {dataset}: {total_por_dataset}")

    # Imprimir el total de registros en la geodatabase
    arcpy.AddMessage(f"Total de registros en la geodatabase: {total_registros}")
    arcpy.AddMessage(f"--------------------------------------------------------")
    
    # Imprimir los resultados detallados
    for dataset, fc_dict in resultados.items():
        arcpy.AddMessage(f"Dataset: {dataset}")
        for fc, count in fc_dict.items():
            arcpy.AddMessage(f"  Clase de entidad: {fc} - Número de registros: {count}")
    
    if xml.lower() == "true":
        # Exportar la geodatabase a un archivo XML
        arcpy.AddMessage(f"--------------------------------------------------------")
        arcpy.AddMessage(f"Exportando esquema GDB")
        arcpy.management.ExportXMLWorkspaceDocument(
            in_data=inGDB,
            out_file=outXML,
            export_type="DATA",  # Opción para exportar datos
            storage_type="BINARY",  # Tipo de almacenamiento
            export_metadata=False  # No exportar metadata
        )
        arcpy.AddMessage(f"Archivo XML exportado a: {outXML}")
    
    return resultados

resultados = contar_registros(inGDB, outXML)
