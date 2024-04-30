import arcpy
import os


# Obtener parámetros de entrada
municipios = arcpy.GetParameterAsText(0)
antenas = arcpy.GetParameterAsText(1)
ruta_salida = arcpy.GetParameterAsText(2)

arcpy.env.overwriteOutput = True

# Crear una geodatabase de salida para almacenar las capas
arcpy.AddMessage("Creando GDB")
gdb_salida = arcpy.CreateFileGDB_management(ruta_salida, 'GDB_Cobertura_Antenas')
GDB = gdb_salida.getOutput(0)

# Copiar la capa de antenas a la geodatabase de salida
arcpy.AddMessage("Copiando entidades")
antenas_copia = arcpy.management.CopyFeatures(antenas, os.path.join(GDB, 'Geodesia_estaciones'))
# Obtener el nombre del campo Buff_km
nombre_campo_buff = None
campos = arcpy.ListFields(antenas_copia)
for campo in campos:
    if campo.name == "Buff_km":
        nombre_campo_buff = campo.name
        
    
if nombre_campo_buff:
    
    # Crear campo temporal para almacenar valores convertidos a kilómetros
    arcpy.AddMessage("Convirtiendo unidades a kilómetros")
    arcpy.management.AddField(antenas_copia, "Buff_km_km", "DOUBLE")
    arcpy.management.CalculateField(antenas_copia, "Buff_km_km", "!{}! * 1000".format(nombre_campo_buff), "PYTHON3")
    
    # Realizar buffer en función del campo Buff_km
    arcpy.AddMessage("Realizando Buffer")
    capa_buff = arcpy.Buffer_analysis(antenas_copia, os.path.join(GDB, "Geodesia_cubrimiento"), 'Buff_km_km')
    arcpy.AddMessage("Se ha creado una nueva capa con buffers basados en los valores de Buff_km.")
else:
    arcpy.AddError("No se encontró el campo 'Buff_km' en la capa de antenas.")


# Usar disolve con el buffer y cortar la capa con los limites de municipios ingresados y
# calcular %cubrimiento sobre el municipio, tener en cuenta que el buffer puede estar sobre más de 1 municipio.

# Disolver la capa del buffer

# Utilizar Pairwise Dissolve en la capa del buffer
arcpy.AddMessage("Realizando Dissolve")
buffer_disuelto = arcpy.analysis.PairwiseDissolve(capa_buff, os.path.join(GDB, "Buffer_Disuelto"))

# Realizar la intersección entre la capa disuelta del buffer y los límites de los municipios
arcpy.AddMessage("Realizando Corte por Municipios")
buffer_cortado = arcpy.analysis.Intersect([buffer_disuelto, municipios], os.path.join(GDB, "Geodesia_cubrimiento_municipio"))

# Calculando parametros
arcpy.AddMessage("Calculando Parámetros")

#Area Munpi
arcpy.management.AddField(buffer_cortado, "Area_Municipio", "DOUBLE")
arcpy.management.CalculateField(buffer_cortado, "Area_Municipio", "!MpArea!", "PYTHON3")
#Area cubrimiento
arcpy.management.AddField(buffer_cortado, "Area_Cubrimiento", "DOUBLE")
arcpy.management.CalculateGeometryAttributes(buffer_cortado, [["Area_Cubrimiento", "AREA"]], area_unit="HECTARES")
# Calculando cubrimiento
arcpy.AddMessage("Calculando Porcentaje de Cubrimiento")
#!Shape_Area!/(!MpArea!*10000)
arcpy.management.AddField(buffer_cortado, "Porcentaje_Cubrimiento", "FLOAT")
arcpy.management.CalculateField(buffer_cortado, "Porcentaje_Cubrimiento", "(!SHAPE.AREA! / (!MpArea! * 10000))*100", "PYTHON3")

#Eliminando archivos
arcpy.management.Delete(buffer_disuelto)

