import arcpy
import os
arcpy.env.overwriteOutput = True

inGDB = arcpy.GetParameterAsText(0)  
xml = arcpy.GetParameterAsText(1)
outXML = arcpy.GetParameterAsText(2)



def contar_registros(inGDB, outXML):
    arcpy.env.workspace = inGDB
    
    # Listar todos los datasets en la geodatabase
    datasets = arcpy.ListDatasets(feature_type='feature') or [""]  # Manejo de None
    
    # Diccionario para almacenar los resultados
    resultados = {}
    total_registros = 0  # Variable para contar el total de registros
    
    for dataset in datasets:
        resultados[dataset] = {}
        total_por_dataset = 0  # Contador para el total por dataset
        
        # Listar todas las clases de entidad dentro de cada dataset
        feature_classes = arcpy.ListFeatureClasses(feature_dataset=dataset)
        
        for fc in feature_classes:
            try:
                # Contar los registros en cada clase de entidad
                count = int(arcpy.management.GetCount(os.path.join(inGDB, dataset, fc)).getOutput(0))
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
    
    # Imprimir los resultados detallados
    for dataset, fc_dict in resultados.items():
        arcpy.AddMessage(f"Dataset: {dataset}")
        for fc, count in fc_dict.items():
            arcpy.AddMessage(f"  Clase de entidad: {fc} - Número de registros: {count}")
    
    
    if xml == "true":
        # Exportar la geodatabase a un archivo XML
        arcpy.AddMessage(f"Exportando esquema GDB")
        arcpy.conversion.ExportXMLWorkspaceDocument(
            in_data=inGDB,
            out_file=outXML,
            export_type="DATA",  # Opción para exportar datos
            storage_type="BINARY",  # Tipo de almacenamiento
            export_metadata=False  # No exportar metadata
        )
        arcpy.AddMessage(f"Archivo XML exportado a: {outXML}")
    else:
        pass

    return resultados

resultados = contar_registros(inGDB, outXML)