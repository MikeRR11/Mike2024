import arcpy

gdb_in=arcpy.GetParameterAsText(0)  #gdb
folder_output=arcpy.GetParameterAsText(1)

def project_gdb(input_gdb, output_gdb):
    # Definir el sistema de coordenadas de origen único nacional de Colombia 2018
    sr = arcpy.SpatialReference(9377)  # EPSG:9377

    # Crear la nueva geodatabase
    arcpy.CreateFileGDB_management(out_folder_path=r'C:\ruta\a\tu', out_name='output.gdb')

    # Obtener la lista de feature datasets
    datasets = arcpy.ListDatasets(feature_type='feature')

    # Copiar datasets y feature classes
    for dataset in datasets:
        arcpy.CreateFeatureDataset_management(output_gdb, dataset, sr)
        arcpy.env.workspace = input_gdb + "\\" + dataset
        feature_classes = arcpy.ListFeatureClasses()
        for fc in feature_classes:
            arcpy.Project_management(fc, output_gdb + "\\" + dataset + "\\" + fc, sr)
            print(f'Feature class {fc} proyectada y copiada.')

    # Copiar feature classes que no están en datasets
    arcpy.env.workspace = input_gdb
    feature_classes = arcpy.ListFeatureClasses()
    for fc in feature_classes:
        arcpy.Project_management(fc, output_gdb + "\\" + fc, sr)
        print(f'Feature class {fc} proyectada y copiada.')

    # Copiar reglas de replicación y topología
    arcpy.env.workspace = input_gdb
    replication_rules = arcpy.da.ListReplicas()
    for rule in replication_rules:
        arcpy.management.CreateReplicaFromServer(rule, output_gdb)
        print(f'Replication rule {rule} copiada.')

    topology_rules = arcpy.da.ListTopologies()
    for topology in topology_rules:
        arcpy.management.CreateTopology(output_gdb, topology)
        print(f'Topology rule {topology} copiada.')

    print('Proceso completado.')

# Parámetros de entrada para la toolbox
if __name__ == '__main__':
    input_gdb = arcpy.GetParameterAsText(0)
    output_gdb = arcpy.GetParameterAsText(1)
    project_gdb(input_gdb, output_gdb)
