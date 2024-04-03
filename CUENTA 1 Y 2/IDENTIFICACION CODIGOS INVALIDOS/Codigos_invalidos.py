import pandas as pd
import arcpy
import os

# Ruta entrada
fc = arcpy.GetParameterAsText(0)
ruta_salida = arcpy.GetParameterAsText(1)

# Leer el Shapefile y convertirlo en un DataFrame de Pandas
# Leer el Shapefile y convertirlo en un DataFrame de Pandas
df = pd.DataFrame(arcpy.da.FeatureClassToNumPyArray(fc, ["OID@", "ngidentif", "ngnoficial", "ngsubcateg", "ngncateg"],
                                                     null_value="Null"))


# Convertir valores nulos a cadena 'Null'
df = df.fillna("Null")

# Limpiar valores en el campo ngidentif y ngnoficial
df["ngidentif"] = df["ngidentif"].astype(str).str.strip()
df["ngnoficial"] = df["ngnoficial"].astype(str).str.strip()
df["ngsubcateg"] = df["ngsubcateg"].astype(str).str.strip()
df["ngncateg"] = df["ngncateg"].astype(str).str.strip()

# Identificar registros con ngidentif vacío
vacios_nulos = df[df["ngidentif"].isna() | (df["ngidentif"] == "")]

# Identificar registros con ngsubcateg vacío
vacios_nulos2 = df[df["ngsubcateg"].isna() | (df["ngsubcateg"] == "")]

# Identificar registros con ngncateg vacío
vacios_nulos3 = df[df["ngncateg"].isna() | (df["ngncateg"] == "")]

#---------------------------------------------------------------------------------------
# Identificar registros con ngidentif nulo
sql_nulos1 = "ngidentif IS NULL"
nulos1 = arcpy.management.SelectLayerByAttribute(fc, "NEW_SELECTION", sql_nulos1)
contador_nulos1 = 0
if nulos1 is not None:
    contador_nulos1 = int(arcpy.GetCount_management(nulos1).getOutput(0))

# Identificar registros con ngsubcateg nulo
sql_nulos2 = "ngsubcateg IS NULL"
nulos2 = arcpy.management.SelectLayerByAttribute(fc, "NEW_SELECTION", sql_nulos2)
contador_nulos2 = 0
if nulos2 is not None:
    contador_nulos2 = int(arcpy.GetCount_management(nulos2).getOutput(0))

# Identificar registros con ngncateg nulo
sql_nulos3 = "ngncateg IS NULL"
nulos3= arcpy.management.SelectLayerByAttribute(fc, "NEW_SELECTION", sql_nulos3)
contador_nulos3 = 0
if nulos3 is not None:
    contador_nulos3 = int(arcpy.GetCount_management(nulos2).getOutput(0))
#----------------------------------------------------------------------------------------
# Agrupar por ngidentif y contar los valores únicos de ngnoficial
agrupado = df.groupby("ngidentif")["ngnoficial"].nunique()

# Filtrar los grupos con más de un valor único en ngnoficial
duplicados = agrupado[agrupado > 1]

# Contadores
contador_vacios_nulos = len(vacios_nulos)
contador_duplicados = 0
# registros = df[df["ngidentif"] == ng_identif]
# contador_duplicados += len(registros)
      
contador_vacios_nulos2 = len(vacios_nulos2)

contador_vacios_nulos3 = len(vacios_nulos3)

# Crear un reporte en un archivo de texto
with open(os.path.join(ruta_salida, "reporte_vacios_duplicados.txt"), "w") as file:
    # Registros con ngidentif con múltiples valores de ngnoficial
    file.write("#-----------------------------------------------------------\n")
    file.write("Registros con ngidentif con múltiples ngnoficial:\n")
    for ng_identif, num_unique_ngnoficial in duplicados.items():
        file.write(f"ngidentif: {ng_identif}\n")
        registros = df[df["ngidentif"] == ng_identif]
        for index, row in registros.iterrows():
            file.write(f"ID: {row['OID@']} // ngnoficial: {row['ngnoficial']}\n")
        file.write(f"Total registros: {len(registros)}\n")
        contador_duplicados += len(registros)
        file.write("\n")
    file.write("---------------------------------------------------\n")

    # Registros con valores de ngidentif vacíos
    if contador_vacios_nulos == 0:
        pass
    else:
        file.write("Registros con valores de ngidentif vacíos:\n")
        for index, row in vacios_nulos.iterrows():
            file.write(f"ID: {row['OID@']}\n")
        file.write(f"Total registros: {contador_vacios_nulos}\n")
        file.write("\n")
        file.write("---------------------------------------------------\n")

    # Registros con valores de ngidentif nulos
    if contador_nulos1 == 0:
        pass
    else:
        file.write("Registros con valores de ngidentif nulos:\n")
        with arcpy.da.SearchCursor(fc, ["OID@"], sql_nulos1) as cursor:
            for row in cursor:
                file.write(f"ID: {row[0]}\n")
        file.write(f"Total registros: {contador_nulos1}\n")
        file.write("\n")
        file.write("---------------------------------------------------\n")

        # Registros con valores de ngsubcateg vacíos
    if contador_vacios_nulos2 == 0:
        pass
    else:
        file.write("Registros con valores de ngsubcateg vacíos:\n")
        for index, row in vacios_nulos2.iterrows():
            file.write(f"ID: {row['OID@']}\n")
        file.write(f"Total registros: {contador_vacios_nulos2}\n")
        file.write("\n")
        file.write("---------------------------------------------------\n")

    # Registros con valores de ngsubcateg nulos
    if contador_nulos2 == 0:
        pass
    else:
        file.write("Registros con valores de ngsubcateg nulos:\n")
        with arcpy.da.SearchCursor(fc, ["OID@"], sql_nulos2) as cursor:
            for row in cursor:
                file.write(f"ID: {row[0]}\n")
        file.write(f"Total registros: {contador_nulos2}\n")
        file.write("\n")
        file.write("---------------------------------------------------\n")

        # Registros con valores de ngncateg vacíos
    if contador_vacios_nulos3 == 0:
        pass
    else:
        file.write("Registros con valores de ngncateg vacíos:\n")
        for index, row in vacios_nulos3.iterrows():
            file.write(f"ID: {row['OID@']}\n")
        file.write(f"Total registros: {contador_vacios_nulos3}\n")
        file.write("\n")
        file.write("---------------------------------------------------\n")

    # Registros con valores de ngncateg nulos
    if contador_nulos3 == 0:
        pass
    else:
        file.write("Registros con valores de ngncateg nulos:\n")
        with arcpy.da.SearchCursor(fc, ["OID@"], sql_nulos3) as cursor:
            for row in cursor:
                file.write(f"ID: {row[0]}\n")
        file.write(f"Total registros: {contador_nulos3}\n")
        file.write("\n")
        file.write("---------------------------------------------------\n")
    

    # Total de registros
    total_registros = contador_duplicados + contador_vacios_nulos + contador_nulos1 + contador_nulos2 + contador_nulos3 + contador_vacios_nulos2 + contador_vacios_nulos3
    file.write(f"TOTAL INCONSISTENCIAS: {total_registros}\n")
