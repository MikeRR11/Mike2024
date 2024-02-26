#Desarrollo de Empalmes 
#Semillero de Investigación y Desrrollo (2024)
#Yaritza Quevedo - Michael Rojas

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
    "monda": "CAMPO",
    "Cerca": "CampoComunCerca",
    "Muro": "CampoComunMuro",
    "Ldemar": "CampoComunLdemar",
    "Terrap": "CampoComunTerrap",
    "Via": "CampoComunVia",
    "Puente_L": "CampoComunPuente_L",
    "VFerre": "CampoComunVFerre",
    "LVia": "CampoComunLVia",
    "SVial": "CampoComunSVial"
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
        arcpy.management.CreateFeatureclass(gdb, fc + "_Empalmes", "POLYGON", GDB_Entrada + "\\" + fc)
        
        # Ejecuta GenerateEdgematchLinks con el campo común
        arcpy.GenerateEdgematchLinks_edit(GDB_Entrada + "\\" + fc, GDB_Adyacente + "\\" + fc, out_fc, Buffer, [(campo_comun, campo_comun)])
        arcpy.AddMessage(f"Empalmes generados para la clase de entidad {fc}")
    else:
        arcpy.AddMessage(f"La clase de entidad {fc} no se encuentra en el diccionario de campos comunes y se omitirá")
