#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Yaritza Quevedo - Michael Andres Rojas - Diego Rugeles
import arcpy
import os

# Obtener las rutas de la GDB y la carpeta de salida desde las entradas del usuario
shp = arcpy.GetParameterAsText(0) #Shapefile de las edificiaciones
MDT = arcpy.GetParameterAsText(1)  # Modelo digital de terreno a ras de piso
MDS = arcpy.GetParameterAsText(2)   #Modelo de superficie con alturas
Ruta_Salida = arcpy.GetParameterAsText(3) # Ruta de salida
espacio = ".                                                                   ."
espacio2 = "-------------------------------------------------------------------------------------------------------"

# Habilitar la sobrescritura de salidas existentes
arcpy.env.overwriteOutput = True

arcpy.AddMessage("INICIANDO PROCESO ...............")
arcpy.AddMessage(espacio)
# Crear una Geodatabase temporal para almacenar los resultados
nombre_gdb = f"Zonificacion_Priorizada.gdb"
gdb = os.path.join(Ruta_Salida, nombre_gdb)
arcpy.AddMessage(f"Creando Geodatabase de resultados: {gdb}")
arcpy.CreateFileGDB_management(Ruta_Salida, nombre_gdb)

#Crear copia de los shape de edificaciones a la GDB Nueva
Feature_Entrada = os.path.basename(shp)
arcpy.AddMessage(espacio2)
# Guardar dentro de la geodatabase (sin extensión .shp)
shp_gdb = os.path.join(gdb, f"{Feature_Entrada}")
arcpy.management.CopyFeatures(shp, shp_gdb)
arcpy.AddMessage(f"Feature class {Feature_Entrada} creado en la GDB")


#Generar centroides de los polignonos en gdb
centroides = os.path.join(gdb, f"{Feature_Entrada}_Points")
featuretopoint = arcpy.management.FeatureToPoint(shp_gdb, centroides, "INSIDE")
arcpy.AddMessage(f"Centroides generados en: {centroides}")

#Crear raster de diferencia de alturas MDS - MDT??}

# Crear raster de diferencia de alturas MDS - MDT
altura_diff = arcpy.ia.Minus(MDS, MDT)
raster_diff = os.path.join(gdb, 'Diferencia_Alturas')
altura_diff.save(raster_diff)
arcpy.AddMessage(f"Raster de diferencia de alturas creado: {raster_diff}")

# Raster to point con los centroides de los polígonos para extraer la altura y guardar en GDB
puntos_altura = os.path.join(gdb, 'Puntos_Altura')
arcpy.sa.ExtractValuesToPoints(centroides, raster_diff, puntos_altura)
arcpy.AddMessage(f"Valores de altura extraídos y guardados en: {puntos_altura}")

# Agregar los datos de altura a la capa de polígonos original (con unión espacial o actualización de atributos)
arcpy.management.JoinField(shp_gdb, "OBJECTID", puntos_altura, "OBJECTID", "RASTERVALU")
arcpy.AddMessage(f"Alturas agregadas al feature class de edificaciones: {shp_gdb}")

arcpy.AddMessage("PROCESO COMPLETADO CORRECTAMENTE.")








