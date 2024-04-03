# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Direccion de Gestion de Información Geografica
# Created on: 2023-06-22
# Created by: Kelly Garro
# # Usage: ModelosDigitalesDeTerrenos
# Description:
# Actualizado semillero de desarrollo
# Yaritza Quevedo
# Michael Rojas
# ---------------------------------------------------------------------------
# Importe librerias
import arcpy
import os
import math
from arcpy.sa import *
from arcpy import env
arcpy.env.overwriteOutput = True

shp_vectores = arcpy.GetParameterAsText(0)
dgn = arcpy.GetParameterAsText(1)
raster_dataset = arcpy.GetParameterAsText(2)
shp_limite = arcpy.GetParameterAsText(3)
escala = arcpy.GetParameterAsText(4)
ruta_salida = arcpy.GetParameterAsText(5)

arcpy.env.overwriteOutput = True

#Creando función de reporte

def generar_reporte (resultado_reporte,ruta_salida):
    
    desc = arcpy.Describe(resultado_reporte) #raster
    sr = desc.spatialReference #spatial reference
    nombre_reporte = 'Reporte_Exactitud_Posicional_Vertical_'+str(desc.Name[0:-4])+'.txt'
    
    file = open(os.path.join(str(ruta_salida),nombre_reporte), "w") 
    #variables de entorno
    arrow = "================================================================="
    espacio= '  '
    arcpy.AddMessage(arrow)
    arcpy.AddMessage("Generando Reporte")

    cont_id = 0
    with arcpy.da.SearchCursor(resultado_reporte, ['DIFERENCIA']) as cursor:
        file.write('Reporte Exactitud Absoluta Posicional Vertical MDT\n' +
                    arrow +
                    '\nDatos Generales Modelo Digital de Terreno'+
                    '\n\nNombre:' + espacio + str(desc.Name) +
                    '\nTipo:' + espacio + str(desc.dataType)  +
                    '\n\nSistema de Referencia'+
                    '\nNombre:' + espacio + espacio + espacio +  str(sr.name) +
                    '\nWKID:' + espacio +  espacio + espacio + str(sr.factoryCode) +
                    '\n'+arrow +
                   '\n\nPoint'+espacio+espacio+espacio+'delta Z')
        
        suma_z = 0
        
        for row in cursor:
            file.write('\n'+ str(cont_id+1) + espacio +espacio +espacio +
                       str(math.sqrt(row[0])) )
            
            suma_z += row[0]
            cont_id = cont_id+1
            
        n = str(arcpy.management.GetCount(resultado_reporte))
    
        arcpy.AddMessage("Se han verificado {} entidades que cumplen con la cláusula de selección.".format(n))
        rmse_z = suma_z/float(n)
        rmse_r = math.sqrt(rmse_z)
        rmse_e =rmse_r*1.96
        arcpy.AddMessage('El RMSE total es: ' + str(round(rmse_r, 2)))
        file.write('\n\n' + arrow + '\nResultados'+
                   '\nUnidades: '+espacio+espacio+espacio+'Meters'+
                   '\nNivel de Confianza: '+espacio+espacio+'95%'+
                   '\nNumero de Observaciones: '+espacio+n+
                   '\nRMSEz: '+espacio+espacio+espacio+espacio+ str(round(rmse_r, 2))+
                   '\nRMSEz con 95% de Confianza: '+espacio+str(round(rmse_e, 2)))
    file.close()         


#Realizando Validación con vectores
def vectores(shp_vectores, raster_dataset, shp_limite, ruta_salida,escala,margen):
    arcpy.AddMessage("Realizando Validación con vectores...")
    dgn_name = os.path.basename(shp_vectores)
    arcpy.AddMessage ("Realizando validacion con shapefile: {0}  ...".format(dgn_name))
    
    #Se crean puntos a partir de los vertices de entrada 
    vertices_vectores = os.path.join(ruta_salida, 'vertices.shp')
    arcpy.management.FeatureVerticesToPoints(shp_vectores, vertices_vectores,'ALL')
  
    # Se obtienen las propiedades del raster, como su valor máximo y mínimo
    arcpy.AddMessage("Obteniendo propiedades del raster...")
    max_result = arcpy.management.GetRasterProperties(raster_dataset, 'MAXIMUM')
    max_value = float(max_result.getOutput(0).replace(",", '.')) if max_result is not None else 0.0
    
    min_result = arcpy.management.GetRasterProperties(raster_dataset, 'MINIMUM')
    min_value = float(min_result.getOutput(0).replace(",", '.')) if min_result is not None else 0.0

    # Se calculan los valores máximo y mínimo con un margen específico
    max = max_value + margen
    min = min_value - margen

    # Se agrega un campo 'altura' al shapefile de puntos y se calcula su valor Z
    arcpy.management.AddField(vertices_vectores, 'altura', 'FLOAT')
    arcpy.management.CalculateGeometryAttributes(vertices_vectores, [["altura", "POINT_Z"]],"METERS")
 
    # Se seleccionan los puntos que cumplen con cierta condición de altura
    where_clause = 'altura <= '+str(max) + 'and altura >= '+str(min)
    select = arcpy.management.SelectLayerByAttribute(vertices_vectores, 'NEW_SELECTION', where_clause, 'NON_INVERT')
    
    # Se copian las entidades seleccionadas a un nuevo shapefile
    vertices_select = os.path.join(ruta_salida,'vertices_select.shp')
    arcpy.management.CopyFeatures(select, vertices_select )

    # Se crean puntos de validación basados en los datos seleccionados
    puntos_validacion = os.path.join(str(ruta_salida),"Puntos_Validacion.shp")
    ExtractValuesToPoints(vertices_select, raster_dataset, puntos_validacion)


    arcpy.AddMessage("Calculando diferencias...")
    arcpy.AddField_management(puntos_validacion, 'DIFERENCIA', 'double')
    arcpy.CalculateField_management(puntos_validacion, 'DIFERENCIA', '(!altura!-!RASTERVALU!)**2','PYTHON3')

    # Se crea un buffer alrededor del límite proporcionado
    limite_buffer = os.path.join(ruta_salida,'shp_limite_buffer.shp')
    arcpy.analysis.Buffer(shp_limite,limite_buffer,  escala)

    # Se crea un nombre para el resultado basado en el nombre del raster de entrada
    desc = arcpy.Describe(raster_dataset) #raster
    shp_resultado = 'Resultado_Consistencia_Logica_'+str(desc.Name[0:-4])+'.shp'

    # Se seleccionan los puntos de validación que están completamente dentro del buffer del 
    arcpy.AddMessage("Filtrando...")
    resultado = arcpy.management.SelectLayerByLocation(puntos_validacion,'COMPLETELY_WITHIN', limite_buffer)
    
    # Seleccionar solo los resultados con valores RASTERVALU positivos
    arcpy.AddMessage("Filtrando...")
    resultado_reporte = arcpy.management.SelectLayerByAttribute(resultado, 'NEW_SELECTION', '"RASTERVALU" >= 0', 'NON_INVERT')

    arcpy.AddMessage("Copiando entidades...")
    #COPIAR ENTIDADES
    arcpy.management.CopyFeatures(resultado_reporte,os.path.join(ruta_salida,shp_resultado))
    
    # Seleccionar los resultados completamente dentro del límite original
    resultado_reporte_filtrado = arcpy.management.SelectLayerByLocation(os.path.join(ruta_salida,shp_resultado), 'COMPLETELY_WITHIN', shp_limite)

    # Generar reporte
    generar_reporte(resultado_reporte_filtrado, ruta_salida)


    # Eliminar los archivos temporales
    arcpy.management.Delete([vertices_vectores, vertices_select, puntos_validacion, limite_buffer])
    arcpy.management.Delete(os.path.join(ruta_salida,'GDB'))
    
#Realizando Validación con DGN   
def cad(dgn, raster_dataset, shp_limite, ruta_salida, escala, margen):
    dgn_name = os.path.basename(dgn)
    arcpy.AddMessage ("Realizando validacion con DGN: {0}  ...".format(dgn_name))

    # Se crea una carpeta para almacenar los datos de salida
    arcpy.management.CreateFolder(ruta_salida, 'GDB')
    arcpy.env.workspace = os.path.join(str(ruta_salida),'GDB')
    GDB_Salida = arcpy.management.CreateFileGDB(os.path.join(str(ruta_salida),'GDB'), 'restitucion')
    arcpy.conversion.CADToGeodatabase(input_cad_datasets = dgn, 
                                      out_gdb_path = GDB_Salida, 
                                      out_dataset_name = 'datos',
                                      reference_scale = 1000,
                                      spatial_reference='PROJCS["MAGNA-SIRGAS_Origen-Nacional",GEOGCS["GCS_MAGNA",DATUM["D_MAGNA",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",5000000.0],PARAMETER["False_Northing",2000000.0],PARAMETER["Central_Meridian",-73.0],PARAMETER["Scale_Factor",0.9992],PARAMETER["Latitude_Of_Origin",4.0],UNIT["Meter",1.0]];-618700 -8436100 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision'
                                      )
    
    arcpy.env.workspace = ruta_salida
    Feature_Class_Polyline = os.path.join(str(GDB_Salida),'datos\Polyline')
    polylinea = arcpy.management.SelectLayerByAttribute(Feature_Class_Polyline, 'NEW_SELECTION',
                                                        "Layer IN ('LEVEL_1','LEVEL_18','LEVEL_19','LEVEL_20','LEVEL_53') OR Layer IN ('Level 1','Level 18','Level 19','Level 20','Level 53') OR Layer IN ('Level_1','Level_18','Level_19','Level_20','Level_53') OR Layer IN ('LAYER_1','LAYER_18','LAYER_19','LAYER_20','LAYER_53') OR Layer IN ('Layer 1','Layer 18','Layer 19','Layer 20','Layer 53')")
    
    
    arcpy.management.CreateFileGDB(ruta_salida,'GDB_Polyline')
    arcpy.AddMessage("Elementos Seleccionados {0}".format(str(polylinea)))
    # Se convierten las entidades seleccionadas a shapefile
    arcpy.conversion.FeatureClassToFeatureClass(polylinea, os.path.join(ruta_salida,"GDB_Polyline.gdb"),"vectores_piso")
    # arcpy.management.Rename('Polyline_Layer1.shp', 'vectores.shp')
    vectores_piso = os.path.join(ruta_salida,r"GDB_Polyline.gdb\vectores_piso")
    
    # Se crean puntos a partir de los vértices de las polilíneas
    vertices_vectores = os.path.join(ruta_salida,r"GDB_Polyline.gdb\vertices_vectores")
    arcpy.management.FeatureVerticesToPoints(vectores_piso, vertices_vectores,'ALL')
  
    # Se obtienen las propiedades del raster, como su valor máximo y mínimo
    max_result = arcpy.management.GetRasterProperties(raster_dataset, 'MAXIMUM')
    max_value = float(max_result.getOutput(0).replace(",", '.')) if max_result is not None else 0.0
    
    min_result = arcpy.management.GetRasterProperties(raster_dataset, 'MINIMUM')
    min_value = float(min_result.getOutput(0).replace(",", '.')) if min_result is not None else 0.0

    # Se calculan los valores máximo y mínimo con un margen específico
    max = max_value + margen
    min = min_value - margen

    arcpy.AddMessage ("Calculando parametros")
    arcpy.management.AddField(vertices_vectores, 'altura', 'FLOAT')
    arcpy.management.CalculateGeometryAttributes(vertices_vectores, [["altura", "POINT_Z"]],"METERS")
    where_clause = 'altura <= '+str(max) + 'and altura >= '+str(min)
    select = arcpy.management.SelectLayerByAttribute(vertices_vectores, 'NEW_SELECTION', where_clause, 'NON_INVERT')

    # Se copian las entidades seleccionadas a un nuevo shapefile
    vertices_select = os.path.join(ruta_salida,'vertices_select.shp')
    arcpy.management.CopyFeatures(select, vertices_select )

    # Se crean puntos de validación basados en los datos seleccionados
    puntos_validacion = os.path.join(str(ruta_salida),"Puntos_Validacion.shp")
    arcpy.AddMessage ("Creando puntos de validación")
    ExtractValuesToPoints(vertices_select, raster_dataset, puntos_validacion)

    
    arcpy.AddField_management(puntos_validacion, 'DIFERENCIA', 'double')
    arcpy.CalculateField_management(puntos_validacion, 'DIFERENCIA', '(!altura!-!RASTERVALU!)**2','PYTHON3')

    # Se crea un buffer alrededor del límite proporcionado
    limite_buffer = os.path.join(ruta_salida,'shp_limite_buffer')
    arcpy.analysis.Buffer(shp_limite,limite_buffer,  escala)

    # Se crea un nombre para el resultado basado en el nombre del raster de entrada
    desc = arcpy.Describe(raster_dataset) #raster
    shp_resultado = 'Resultado_Consistencia_Logica_'+str(desc.Name[0:-4])+'.shp'

    # Se seleccionan los puntos de validación que están completamente dentro del buffer del 
    
    resultado = arcpy.management.SelectLayerByLocation(puntos_validacion,'COMPLETELY_WITHIN', limite_buffer)
    
    # Seleccionar solo los resultados con valores RASTERVALU positivos
    resultado_reporte = arcpy.management.SelectLayerByAttribute(resultado, 'NEW_SELECTION', '"RASTERVALU" >= 0', 'NON_INVERT')

    #COPIAR ENTIDADES
    arcpy.management.CopyFeatures(resultado_reporte,os.path.join(ruta_salida,shp_resultado))
    
    # Seleccionar los resultados completamente dentro del límite original
    resultado_reporte_filtrado = arcpy.management.SelectLayerByLocation(shp_resultado, 'COMPLETELY_WITHIN', shp_limite)

    # Generar reporte
    generar_reporte(resultado_reporte_filtrado, ruta_salida)


    # Eliminar los archivos temporales
    #arcpy.management.Delete([vectores_piso, vertices_vectores, vertices_select, puntos_validacion, limite_buffer])
    arcpy.management.Delete(os.path.join(ruta_salida,'GDB'))





if __name__ == '__main__':
    dic_escala = {
        '1000' : '-1 Meters',
        '2000' : '-2 Meters',
        '5000' : '-5 Meters',
        '10000' : '-10 Meters',
        '25000' : '-25 Meters',
    }

    dic_range = {
        '1000' : 0.3,
        '2000' : 0.6,
        '5000' : 1.5,
        '10000' : 3,
        '25000' : 7.5,
    }
    
    if shp_vectores != '':
        vectores(shp_vectores, raster_dataset,shp_limite, ruta_salida,dic_escala[escala],dic_range[escala])
        
    if dgn != '':
        cad(dgn, raster_dataset,shp_limite, ruta_salida, dic_escala[escala],dic_range[escala])
