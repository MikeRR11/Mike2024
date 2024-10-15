# -*- coding: utf-8 -*-
import arcpy
import os
 
MDB_original = r"C:\Users\yaritza.quevedo\Downloads\OneDrive_2024-08-27\Cartografia Qquindio igac 10000_CORDILLERA\CARTOGRAFIA 1_10.000\GEODATABASE\INTEGRADA"
Ruta_salida = r"D:\Proyecto"
xml_esquema = os.path.join(Ruta_salida, "esquema_mdb.xml")
 
arcpy.env.overwriteOutput = True
 
 
def convertir_mdb_a_gdb(MDB_original, Ruta_salida):
    try:
        for dirpath, dirnames, filenames in os.walk(MDB_original):
            for filename in filenames:
                if filename.endswith(".mdb"):
                    mdb_path = os.path.join(dirpath, filename)
                   
                    if os.path.exists(xml_esquema):
                        os.remove(xml_esquema)
                   
                    arcpy.management.ExportXMLWorkspaceDocument(mdb_path, xml_esquema, "SCHEMA_ONLY", "BINARY", "METADATA")
                    arcpy.AddMessage("Exportación del esquema completada exitosamente.")
                   
                    gdb_name = os.path.splitext(filename)[0] + ".gdb"
                    fgdb = os.path.join(Ruta_salida, gdb_name)
                   
                    arcpy.AddMessage("Creando FGDB: {}".format(fgdb))
                    arcpy.management.CreateFileGDB(Ruta_salida, gdb_name, "CURRENT")
                   
                    arcpy.management.ImportXMLWorkspaceDocument(fgdb, xml_esquema, "SCHEMA_ONLY")
                    arcpy.AddMessage("Importación del esquema completada exitosamente.")
                   
                    arcpy.env.workspace = mdb_path
 
                    datasets = arcpy.ListDatasets()
 
                    for dataset in datasets:
                        arcpy.env.workspace = os.path.join(mdb_path, dataset)
                        feature_classes = arcpy.ListFeatureClasses()
                       
                        topologies = arcpy.ListDatasets("*_topology", "Topology")
                   
                        for topology in topologies:
                            topology_path = os.path.join(fgdb, dataset, topology)
                            if arcpy.Exists(topology_path):
                                arcpy.management.Delete(topology_path)
                                arcpy.AddMessage("Topología '{}' eliminada.".format(topology_path))
 
                        for fc in feature_classes:
                           
                            count = arcpy.GetCount_management(fc).getOutput(0)
                            if count == "0":
                                arcpy.AddMessage("Feature class '{}' no tiene registros, se omite.".format(fc))
                                continue
                           
                            fc_name = arcpy.Describe(fc).name
                            fc_output_path = os.path.join(fgdb, dataset, fc_name)
                           
                            try:
                           
                                arcpy.CopyFeatures_management(fc, fc_output_path)
                                arcpy.AddMessage("Feature class {} copiado a la gdb de destino".format(fc_name))
                               
                            except:
                                arcpy.AddError("Error durante la operación de copia")
 
    except arcpy.ExecuteError:
        arcpy.AddError("Ocurrió un error en la ejecución de ArcPy: {}".format(arcpy.GetMessages(2)))
    except:
        arcpy.AddError("Ocurrió un error: ")
 
 
convertir_mdb_a_gdb(MDB_original, Ruta_salida)
 