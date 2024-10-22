#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Yaritza Quevedo - Michael Andres Rojas - Diego Rugeles
import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
shp = arcpy.GetParameterAsText(0) #Shapefile de las edificiaciones
MDT = arcpy.GetParameterAsText(1)  # Modelo digital de terreno a ras de piso
MDS = arcpy.GetParameterAsText(2)   #Modelo de superficie con alturas
altura_pisos = arcpy.GetParameterAsText(3) #Altura de los pisos 
usar_raster_pisos = arcpy.GetParameterAsText(4) #Condicional usar pisos 
Raster_pisos = arcpy.GetParameterAsText(5) #Raster altura pisos
Ruta_Salida = arcpy.GetParameterAsText(6) # Ruta de salida

espacio = ".                                                                   ."


# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage(espacio)
# Crear una Geodatabase temporal para almacenar los resultados
nombre_gdb = f"Altura Edificaciones.gdb"
gdb = os.path.join(Ruta_Salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb}")
arcpy.CreateFileGDB_management(Ruta_Salida, nombre_gdb)

#Crear copia de los shape de edificaciones a la GDB Nueva
Feature_Entrada = f"{os.path.basename(shp)}_Alturas"
# Guardar dentro de la geodatabase (sin extensión .shp)
shp_gdb = os.path.join(gdb, f"{Feature_Entrada}")
arcpy.management.CopyFeatures(shp, shp_gdb)
arcpy.AddMessage(f"Feature class {Feature_Entrada} creado en la GDB")
arcpy.AddMessage(espacio)

#Generar centroides de los polignonos en gdb
centroides = os.path.join(gdb, f"{Feature_Entrada}_Centroides")
featuretopoint = arcpy.management.FeatureToPoint(shp_gdb, centroides, "INSIDE")
arcpy.AddMessage(f"Centroides generados en: {centroides}")
arcpy.AddMessage(espacio)
#Crear raster de diferencia de alturas MDS - MDT??}

# Crear raster de diferencia de alturas MDS - MDT

if usar_raster_pisos == "false":
    altura_diff = arcpy.ia.Minus(MDS, MDT)
    raster_diff = os.path.join(gdb, 'Diferencia_Alturas')
    altura_diff.save(raster_diff)
    arcpy.AddMessage(f"Raster de diferencia de alturas creado: {raster_diff}")
    arcpy.AddMessage(espacio)
else:
    raster_diff = os.path.join(Raster_pisos)

# Raster to point con los centroides de los polígonos para extraer la altura y guardar en GDB
puntos_altura = os.path.join(gdb, 'Puntos_Altura')
arcpy.sa.ExtractValuesToPoints(centroides, raster_diff, puntos_altura)
arcpy.AddMessage(f"Valores de altura extraídos y guardados en: {puntos_altura}")
arcpy.AddMessage(espacio)

# Agregar los datos de altura a la capa de polígonos original (con unión espacial o actualización de atributos)
arcpy.management.JoinField(shp_gdb, "OBJECTID", puntos_altura, "OBJECTID", "RASTERVALU")
arcpy.AddMessage(f"Alturas agregadas al feature class de edificaciones: {shp_gdb}")
arcpy.AddMessage(espacio)


#Agregar el número de pisos según la altura ingresada 
arcpy.management.AddField(shp_gdb, "Número_Pisos", "DOUBLE",field_scale = 0)
SQL = f"math.floor(!RASTERVALU!/{altura_pisos})"
arcpy.management.CalculateField(shp_gdb, "Número_Pisos",SQL, "PYTHON3")
arcpy.AddMessage(f"Número de pisos calculado en: {shp_gdb}")


arcpy.AddMessage("PROCESO COMPLETADO CORRECTAMENTE.")




