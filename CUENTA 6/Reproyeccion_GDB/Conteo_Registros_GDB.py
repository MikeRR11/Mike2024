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
            # Extraer nombre del dataset y del feature class
            dataset_name = os.path.basename(os.path.dirname(fc))
            fc_name = os.path.basename(fc)

            # Reparar geometría
            arcpy.management.RepairGeometry(fc, delete_null=True, validation_method='OGC')
            arcpy.AddMessage(f"Geometría reparada para: {dataset_name} / {fc_name}")
        except arcpy.ExecuteError:
            # Capturar y mostrar el mensaje de error detallado
            error_message = arcpy.GetMessages()
            arcpy.AddError(f"Error al reparar geometría para {fc_name} en dataset {dataset_name}: {error_message}")



def contar_registros(inGDB):
    arcpy.AddMessage("--------------------------------------------------------")
    arcpy.AddMessage(f"Contando registros de: {inGDB}")
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

        for fc in feature_classes:
            fc_path = os.path.join(inGDB, dataset, fc)
            try:
                count = int(arcpy.management.GetCount(fc_path).getOutput(0))
                resultados[dataset][fc] = count
                total_por_dataset += count  # Sumar al total por dataset
            except arcpy.ExecuteError:
                arcpy.AddError(f"Error al contar registros para {fc} en {dataset}")
                error_message = arcpy.GetMessages()
                arcpy.AddError(f" {error_message}")

        # Añadir el total por dataset al total general
        total_registros += total_por_dataset
        # Imprimir el total de registros por dataset
        arcpy.AddMessage(f"Total de registros en el dataset {dataset}: {total_por_dataset}")

    # Imprimir el total de registros en la geodatabase
    arcpy.AddMessage(f"Total de registros en la geodatabase: {total_registros}")
    arcpy.AddMessage("#########################################################")
    # Imprimir los resultados detallados
    for dataset, fc_dict in resultados.items():
        arcpy.AddMessage(f"Dataset: {dataset}")
        for fc, count in sorted(fc_dict.items()):
            arcpy.AddMessage(f"  Clase de entidad: {fc} - Número de registros: {count}")

    return resultados, total_registros

def exportar_xml(inGDB, outXML):
    arcpy.AddMessage("--------------------------------------------------------")
    arcpy.AddMessage("Exportando esquema GDB")
    arcpy.management.ExportXMLWorkspaceDocument(
        in_data=inGDB,
        out_file=outXML,
        export_type="DATA",  # Opción para exportar datos
        storage_type="BINARY",  # Tipo de almacenamiento
        export_metadata=False  # No exportar metadata
    )
    arcpy.AddMessage(f"Archivo XML exportado a: {outXML}")

def main():
    full_fc_paths = []

    if repair.lower() == "true":
        # Obtener rutas completas de las clases de entidad antes de contar
        arcpy.env.workspace = inGDB
        datasets = sorted(arcpy.ListDatasets(feature_type='feature') or [""])  # Manejo de None
        for dataset in datasets:
            feature_classes = sorted(arcpy.ListFeatureClasses(feature_dataset=dataset))
            full_fc_paths.extend([os.path.join(inGDB, dataset, fc) for fc in feature_classes])

        # Reparar geometría
        repair_geometry(full_fc_paths)

    # Contar registros
    resultados, total_registros = contar_registros(inGDB)

    # Exportar XML
    if xml.lower() == "true":
        exportar_xml(inGDB, outXML)

main()
