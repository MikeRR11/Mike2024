# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Direccion de Gestion de Información Geografica
# Created on: 2023-11-28
# Created by: Kelly Garro - Diego Rugeles
# # Usage: Exactitud Posicional Relativa GDBs
# Description:
# ---------------------------------------------------------------------------
import arcpy, os, string, re, math
import sys
from arcpy import env
import random
import shutil #"shutil" used to remove existing directory
import statistics
import time
import os 


paso1 = arcpy.GetParameter(0)
escala = arcpy.GetParameterAsText(1)
gdb= arcpy.GetParameterAsText(2)
ruta_salida_puntos = arcpy.GetParameterAsText(3)
paso2 = arcpy.GetParameter(4)
puntos_extraidos =  arcpy.GetParameterAsText(5)
puntos_manuales_generados =  arcpy.GetParameterAsText(6)
ruta_salida_reporte =  arcpy.GetParameterAsText(7)
escala_rmse = arcpy.GetParameterAsText(8)
def SelectRandomByCount(layer,count,salidapuntos):
        layerCount = int(arcpy.GetCount_management(layer).getOutput(0))
        if layerCount < count:
            arcpy.AddMessage('NO EXISTEN SUFICIENTES PUNTOS PARA SELECIONAR')
            return
        oids = [oid for oid, in arcpy.da.SearchCursor(layer, "OID@")]
        oidFldName = arcpy.Describe(layer).OIDFieldName
        delimOidFld = arcpy.AddFieldDelimiters(layer, oidFldName)
        randOids = random.sample(oids, count)
        oidsStr = ",".join(map(str, randOids))
        sql = "{0} IN ({1})".format(delimOidFld, oidsStr)
        arcpy.management.MakeFeatureLayer(layer, "stateslyrs")
        arcpy.management.SelectLayerByAttribute("stateslyrs", "NEW_SELECTION", sql, "NON_INVERT")
        arcpy.management.CopyFeatures("stateslyrs", salidapuntos)
        #arcpy.management.Delete("stateslyrs")
        return

def vectores(gdb, escala, ruta_salida):
    arcpy.AddMessage("Extracción de vertices para la validación de exactitud posicional...")
    gdb_name = os.path.basename(gdb)
    arcpy.env.workspace = gdb 
    arcpy.AddMessage ("Extrayendo vertices para la escala {0} de la GDB {1} ...".format(escala,gdb_name))
    #Se crean puntos a partir de los vertices de entrada 
    vertices_vectores = os.path.join(ruta_salida, 'temp.shp')

    arcpy.AddMessage("Hay Suficientes Puntos del FC: TSPblu")
    arcpy.management.FeatureVerticesToPoints(gdb, vertices_vectores,'ALL')
    arcpy.management.AddField(vertices_vectores, 'FC_Origen','TEXT')
    arcpy.management.CalculateField(vertices_vectores, 'FC_Origen',"{0}".format(str(gdb)), 'PYTHON3')

    vertices_rand = os.path.join(ruta_salida, 'Puntos_Revisar.shp')
    
    try:
        SelectRandomByCount(vertices_vectores,20,vertices_rand)
    
    arcpy.management.Delete(vertices_vectores)
    return

def RMSE (validacion, fotocontrol, ruta_salida, escala):
    
    file = open(os.path.join(str(ruta_salida),'Reporte_RMSE_GDB.txt'), "w")
    #variables de entorno
    arrow = "=============================================="
    espacio= '	'
    dic_escala = {'1:1000':'4 Meters',
                  '1:2000':'10 Meters',
                  '1:5000':'20 Meters',
                  '1:10000':'50 Meters',
                  '1:25000':'100 Meters',
                  '1:50000':'100 Meters'}
    
    arcpy.AddXY_management(validacion)
    arcpy.AddXY_management(fotocontrol)
    Vali_2 = arcpy.management.CopyFeatures(validacion, os.path.join(str(ruta_salida),'ly_1_temp.shp'))
    Foto_2 = arcpy.management.CopyFeatures(fotocontrol, os.path.join(str(ruta_salida),'ly_2_temp.shp'))
    
    join = arcpy.SpatialJoin_analysis(Vali_2,Foto_2, os.path.join(str(ruta_salida),'Spatial_join.shp'),
                                      'JOIN_ONE_TO_ONE', 'KEEP_ALL','','CLOSEST', dic_escala[escala],'')
    arcpy.AddField_management(join, 'x_rmse', 'double')
    arcpy.AddField_management(join, 'y_rmse', 'double')
    arcpy.CalculateField_management(join, 'x_rmse', '(!POINT_X!-!POINT_X_1!)**(2)','PYTHON3')
    arcpy.CalculateField_management(join, 'y_rmse', '(!POINT_Y!-!POINT_Y_1!)**(2)','PYTHON3')
    
    arcpy.Delete_management(Foto_2)
    arcpy.Delete_management(Vali_2)
    with arcpy.da.SearchCursor(join, ['FID','POINT_X','POINT_Y','x_rmse','y_rmse']) as cursor:
        file.write('\nPositional Accuracy Report\n' + arrow +
                   '\n\nSpatial Reference Information\n'+
                   str(arcpy.Describe(fotocontrol).spatialReference.Name)+'\n'+arrow+
                   '\n\nPoint'+espacio+'X coord.'+espacio+'Y coord.'+espacio+'Delta X'+espacio+espacio+espacio+'Delta Y')
        
        suma_x = 0
        suma_y = 0 
        for row in cursor:
            file.write('\n'+ str(row[0]+1) + espacio +
                       str(row[1]) + espacio +
                       str(row[2]) + espacio +
                       str(math.sqrt(row[3])) + espacio +
                       str(math.sqrt(row[4])) )
            
            suma_x = suma_x + row[3]
            suma_y = suma_y + row[4]
            
        n = str(arcpy.management.GetCount(join))
        
        rmse_x = suma_x/float(n)
        rmse_y = suma_y/float(n)
        rmse_r = round((math.sqrt(rmse_x + rmse_y)),2)
        arcpy.AddMessage('El RMSE total es: ' + str(rmse_r))
        file.write('\n\n' + arrow + '\nError Report Section'+
                   '\nReport Units: '+espacio+espacio+espacio+'Meters'+
                   '\nRMSE: '+espacio+espacio+espacio+espacio+str(rmse_r)+
                   '\nConfidence Level: '+espacio+espacio+'95%'+
                   '\nNumber of observations: '+espacio+n+
                   '\nRMSE 95%: '+espacio+espacio+espacio+str(round(rmse_r*1.96,2)))
    file.close()
    arcpy.Delete_management(join)


if paso1 == True:
    vectores(gdb,escala, ruta_salida_puntos)
elif paso2 == True:
    RMSE(puntos_extraidos,puntos_manuales_generados, ruta_salida_reporte, escala_rmse)

