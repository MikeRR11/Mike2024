#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Diego Rugeles - Michael Rojas
import arcpy
import os

# Parámetros de entrada
Vias = arcpy.GetParameterAsText(0)
Ruta_Salida = arcpy.GetParameterAsText(1)
Buffer = arcpy.GetParameterAsText(2)

arcpy.env.overwriteOutput = True
arcpy.env.workspace = Vias
arcpy.AddMessage("INICIANDO PROCESO")

#1 HACER CAPA DE PUNTOS DE DANGLES. INICIO Y FINAL
Dangles = arcpy.FeatureVerticesToPoints_management(Vias,os.path.join(str(Ruta_Salida),'Dangles.shp'), "DANGLE")
PInicioFin = arcpy.FeatureVerticesToPoints_management(Vias,os.path.join(str(Ruta_Salida),'PInicioFin.shp'), "BOTH_ENDS")
#2 ELIMINAR L0OS PUNTOS BUENOS, LOS QUE TIENEN DANGLE
arcpy.AddMessage("Descartando puntos")
Select = arcpy.management.SelectLayerByLocation(PInicioFin, "INTERSECT", Dangles, invert_spatial_relationship = "NOT_INVERT")
Puntos = arcpy.management.CopyFeatures(Select, os.path.join(str(Ruta_Salida),'Puntos.shp'))
arcpy.Delete_management(Dangles)
arcpy.Delete_management(PInicioFin)

#3 HACER SELECCION DINAMICA DE PUNTOS CON MAS DE UN REGISTRO DE VÍA Y EXPORTAR PUNTOS A UN NUEVO FEATURE
# Definir la ruta de salida para la nueva capa de puntos
ruta_nueva_capa = os.path.join(Ruta_Salida, "Puntos_Validar.shp")

# Crear la nueva capa de puntos
arcpy.CreateFeatureclass_management(os.path.dirname(ruta_nueva_capa), os.path.basename(ruta_nueva_capa), "POINT", spatial_reference=Puntos)

# Abrir un cursor de inserción para la nueva capa
with arcpy.da.SearchCursor(Puntos, ["SHAPE@","ORIG_FID"]) as Scursor:
    for punto in Scursor:
        # Realizar la selección por localización de las vías que intersectan con el punto
        Selectp = 0
        Selectp = arcpy.management.SelectLayerByLocation(Vias, "INTERSECT", punto[0], search_distance=str(Buffer)+' Meters')
        # Obtiene el recuento de elementos seleccionados
        count = arcpy.GetCount_management(Selectp)
        # Convierte el recuento a un valor entero
        count_int = int(count.getOutput(0))
        # Si hay más de una vía intersectando con el punto, insertar el punto en la nueva capa
        if count_int > 1:
            with arcpy.da.InsertCursor(ruta_nueva_capa, ["SHAPE@"]) as Icursor: 
                Icursor.insertRow([punto[0]])

# Imprimir un mensaje con el número de puntos insertados
arcpy.AddMessage(f"Se han insertado {arcpy.GetCount_management(ruta_nueva_capa)} puntos con más de una vía sin conectar")

# Finalizar con un mensaje de éxito
arcpy.AddMessage("PROCESO FINALIZADO CON ÉXITO.")