# -*- coding: utf-8 -*-
"""
Descripción:
    Este script realiza empalmes entre clases de entidad de dos geodatabases en ArcGIS Pro.
    Requiere cuatro parámetros de entrada:
        1. GDB_Entrada: La ruta de la geodatabase de entrada.
        2. GDB_Adyacente: La ruta de la geodatabase adyacente para realizar los empalmes.
        3. Carpeta_Salida: La carpeta de salida donde se creará la nueva geodatabase con los resultados.
        4. Buffer: El tamaño del buffer para los empalmes.
Formato de salida:
    Se creará una nueva geodatabase en la carpeta de salida, con clases de entidad que contienen los empalmes.
"""

# Desarrollo de Empalmes
# Semillero de Investigación y Desarrollo (2024)
# Yaritza Quevedo - Michael Rojas

import arcpy
import os

# Obtención de parámetros
GDB_Entrada = arcpy.GetParameterAsText(0)
GDB_Adyacente = arcpy.GetParameterAsText(1)
Carpeta_Salida = arcpy.GetParameterAsText(2)
Buffer = arcpy.GetParameterAsText(3)

arcpy.env.overwriteOutput = True

# Creación de la geodatabase de salida
gdb_nombre = os.path.basename(GDB_Entrada) + "_Empalmes"
result = arcpy.management.CreateFileGDB(Carpeta_Salida, gdb_nombre)
gdb = result.getOutput(0)
arcpy.AddMessage("Geodatabase creada correctamente.")

# Definir diccionario de campos comunes por feature class
campos_comunes = {
    "Cerca": "RuleID",
    "Muro": "RuleID",
    "Ldemar": "RuleID",
    "Terrap": "RuleID",
    "Via": "RuleID",
    "Puente_L": "RuleID",
    "VFerre": "RuleID",
    "LVia": "RuleID",
    "SVial": "RuleID",
    "Telefe": "RuleID",
    "Tunel": "RuleID",
    "Ciclor": "RuleID",
    "Drenaj_L": "RuleID",
    "DAgua_L": "RuleID",
    "LCoste": "RuleID",
    "LCNivel": "RuleID",
    "LDterr": "RuleID",
    "RATens": "RuleID",
    "Tuberi": "RuleID",
    "Fronte": "RuleID",
    "Llimit": "RuleID",
}

# Lista de todas las clases de entidad en ambas geodatabases
arcpy.env.workspace = GDB_Entrada
datasets1 = arcpy.ListDatasets(feature_type='Feature')
feature_classes1 = arcpy.ListFeatureClasses()
for dataset in datasets1:
    feature_classes1 += arcpy.ListFeatureClasses(feature_dataset=dataset)

arcpy.env.workspace = GDB_Adyacente
datasets2 = arcpy.ListDatasets(feature_type='Feature')
feature_classes2 = arcpy.ListFeatureClasses()
for dataset in datasets2:
    feature_classes2 += arcpy.ListFeatureClasses(feature_dataset=dataset)

# Intersección de las listas para obtener las clases de entidad comunes
common_feature_classes = list(set(feature_classes1) & set(feature_classes2))

for fc in common_feature_classes:
    # Comprueba si la clase de entidad está en el diccionario
    if fc in campos_comunes:
        campo_comun = campos_comunes[fc]
        arcpy.AddMessage(f"Procesando la clase de entidad {fc} con el campo común {campo_comun}")
        
        # Crea la clase de entidad de salida
        out_fc = gdb + "\\" + fc + "_Empalmes"
        arcpy.management.CreateFeatureclass(gdb, fc + "_Empalmes", "POLYLINE", GDB_Entrada + "\\" + fc)
        
        # Ejecuta GenerateEdgematchLinks con el campo común
        empalmes = arcpy.edit.GenerateEdgematchLinks(GDB_Entrada + "\\" + fc, GDB_Adyacente + "\\" + fc, out_fc, Buffer, [(campo_comun, campo_comun)])
        conteo = arcpy.management.GetCount(empalmes)
         # Si la clase de entidad está vacía
        if int(conteo[0]) == 0:
                # Elimina la clase de entidad
                arcpy.Delete_management(empalmes)
        else:
         arcpy.AddMessage(f"Empalmes generados para la clase de entidad {fc}")   
    else:
        pass
        #arcpy.AddMessage(f"La clase de entidad {fc} no se encuentra en el diccionario de campos comunes y se omitirá")
