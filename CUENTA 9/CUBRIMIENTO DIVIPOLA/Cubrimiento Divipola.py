import arcpy
import os

# Configuración de entorno
arcpy.env.overwriteOutput = True

# Parámetros de entrada desde la toolbox
Munpi = arcpy.GetParameterAsText(0)  # Entrada de features desde toolbox
features = arcpy.GetParameterAsText(1)  # Campo para clasificar
ruta_salida = arcpy.GetParameterAsText(2)  # Ruta de salida para los resultados
espacio = ".                                                                   ."
espacio2 = "-------------------------------------------------------------------------------------------------------"

# Validación de entradas
if not os.path.exists(ruta_salida):
    arcpy.AddError(f"La ruta de salida no existe: {ruta_salida}")
    raise ValueError("Ruta de salida inválida")

# Procesamiento de los shapes de puntos originales
if features:
    features_Lista = [rel.strip() for rel in features.split(";")]  # Se dejan en una lista separados por punto y coma las rutas
else:
    arcpy.AddError("No se ha proporcionado ninguna capa de entrada.")
    raise ValueError("No se han proporcionado features de entrada")

# Crear una Geodatabase temporal para almacenar los resultados
nombre_gdb = f"Cubrimiento_Munpi.gdb"
gdb_temporal = os.path.join(ruta_salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb_temporal}")
arcpy.CreateFileGDB_management(ruta_salida, nombre_gdb)

def cubrimiento(Munpi, feature, gdb_temporal):
    #Obteniendo nombre del feature
    feature_name = f"{os.path.basename(feature)}_Cubrimiento"
    #Realizar el clip de la capa con el feature de municipios
    clip = arcpy.gapro.ClipLayer(
    input_layer= feature,
    clip_layer=Munpi,
    out_feature_class= os.path.join(gdb_temporal,feature_name))

    arcpy.AddMessage(f"Clip realizado para {feature_name}")
    
    #Añadiendo campos
    arcpy.management.AddField(clip, "DIVIPOLA", "TEXT")
    arcpy.management.AddField(clip, "%_CUBRIMIENTO", "DOUBLE")

    conteo_municipio = int(arcpy.management.GetCount(Munpi).getOutput(0))

    # Permitir la iteración de cada elemnto de la tabla de municipios a través de un query dinámico
    for i in range(1,conteo_municipio+1):
        SQL = 'OBJECTID = {0}'.format(i)
        arcpy.AddMessage(f"Inciando iterador para municipio {i}")
        select_a = arcpy.management.SelectLayerByAttribute(Munpi, "NEW_SELECTION", SQL)
        select_b = arcpy.management.SelectLayerByLocation(select_a, "WITHIN", clip)

        #Realizar la actualización del campo de % de cubrimiento a partir de la busqueda del DIVIPOLA 
        with arcpy.da.SearchCursor(select_a,['MpCodigo','SHAPE@AREA']) as Scur:
            for municipio in Scur:
                with arcpy.da.UpdateCursor(select_b,["DIVIPOLA","%_CUBRIMIENTO","SHAPE@AREA"]) as Ucur: 
                    for poligono in Ucur:
                        poligono[0] = municipio[0]
                        poligono[1] = (poligono[2]/municipio[1])*100
                        Ucur.UpdateRow(poligono)
                        

for feature in features_Lista:
    cubrimiento(Munpi, feature, gdb_temporal)

arcpy.AddMessage(espacio2)
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO")
