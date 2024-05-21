#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Diego Rugeles - Michael Rojas
import rapidfuzz
from rapidfuzz import fuzz
import arcpy 
import os

#Libreria Rapid Fuzz




#Parámetros de entrada
Puntos1 = arcpy.GetParameterAsText(0)
Puntos2 = arcpy.GetParameterAsText(1)
Buffer_Dist = arcpy.GetParameterAsText(2)
Ruta_Salida = arcpy.GetParameterAsText(3)

#Se requiere comparar dos feature dataset de geometria tipo punto, los cuales contienen nombres 
#geograficos en uno de sus campos, se tienen que relacionar los puntos de ambos features para determinar su semejanza en al menos un 80%, en un radio de busqueda
#dinamico, al final exportar una capa de puntos quew contenga los datos con semejanza mayor al 80%


#Hacer un join espacial para unir ambas tablas en un radio de busqueda

arcpy.AddMessage("Iniciando Union Espacial")
Puntos_Union = arcpy.analysis.SpatialJoin(
    target_features=Puntos1,
    join_features=Puntos2,
    out_feature_class= os.path.join(Ruta_Salida, "Puntos_Union.shp"),
    join_operation="JOIN_ONE_TO_MANY",
    join_type="KEEP_ALL", #Mantener todos los campos de ambas capas
    field_mapping=None,  # Usar los campos por defecto
    match_option="INTERSECT",
    search_radius=Buffer_Dist,
    distance_field_name=None,
    match_fields=None
)

# Crear una feature class para los puntos que cumplen con el criterio de similitud
Puntos80 = os.path.join(Ruta_Salida, "Puntos_Semejanza_80")
# Campo que contiene los nombres geográficos
campo_nombre = "NGNPrincip"  # Cambiar según el nombre del campo en tus datasets


# Lista para almacenar los resultados
resultados_similitud = []

# Usar un SearchCursor para iterar sobre los puntos

arcpy.AddMessage("Iniciando Cursores")

with arcpy.da.SearchCursor(Puntos_Union, ['SHAPE@', 'JOIN_FID', campo_nombre, campo_nombre + "_1"]) as sCur:
    for row in sCur:
        # Comparar la similitud entre los campos
        similitud = fuzz.ratio(row[2], row[3])
        # Si la similitud es mayor o igual a 80, agregar al resultado
        if similitud >= 80:
            resultados_similitud.append((row[0], row[1], row[2], row[3], similitud))

# Usar un InsertCursor para agregar los puntos similares a la nueva feature class
with arcpy.da.InsertCursor(Puntos80, ['SHAPE@', 'JOIN_FID', campo_nombre, campo_nombre + "_1", 'Similitud']) as iCur:
    for resultado in resultados_similitud:
        iCur.insertRow(resultado)


arcpy.AddMessage("Unión espacial completada")




