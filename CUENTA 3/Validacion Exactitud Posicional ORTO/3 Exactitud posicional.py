# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Direccion de Gestion de Información Geografica
# Created on: 2023-06-14
# Created by: Kelly Villamil - Diego Rugeles (Supervisor Desarrollo DGIG)
# Actualizado en: 2024-04-16
# Actualizado por: Michael Andres Rojas - Diego Rugeles (Supervisor Desarrollo DGIG)
# # Usage: Migracion de Dataset Superficies de Agua a GDB v.2.5
# Description:
# ---------------------------------------------------------------------------
# Importe librerias
import arcpy
import os
import math
# Script arguments
shp_validacion = arcpy.GetParameterAsText(0)
shp_fotocontrol = arcpy.GetParameterAsText(1)
ruta_salida = arcpy.GetParameterAsText(2)

arcpy.env.overwriteOutput = True
def RMSE (validacion, fotocontrol, ruta_salida):
    
    file = open(os.path.join(str(ruta_salida),'Reporte_RMSE ' + str(arcpy.Describe(fotocontrol).Name) + ".txt"), "w")
    #variables de entorno
    arrow = "=============================================="
    espacio= '	'
    
    arcpy.AddXY_management(validacion)
    arcpy.AddXY_management(fotocontrol)
    Vali_2 = arcpy.MakeFeatureLayer_management(validacion, os.path.join(str(ruta_salida),'ly_1_temp.shp'))
    Foto_2 = arcpy.MakeFeatureLayer_management(fotocontrol, os.path.join(str(ruta_salida),'ly_2_temp.shp'))
    
    join = arcpy.SpatialJoin_analysis(Vali_2,Foto_2, os.path.join(str(ruta_salida),'Spatial_join.shp'),
                                      'JOIN_ONE_TO_ONE', 'KEEP_ALL','','CLOSEST', '1000 Meters','')
    arcpy.AddField_management(join, 'x_rmse', 'double')
    arcpy.AddField_management(join, 'y_rmse', 'double')
    arcpy.CalculateField_management(join, 'x_rmse', '(!POINT_X!-!POINT_X_1!)**(2)','PYTHON3')
    arcpy.CalculateField_management(join, 'y_rmse', '(!POINT_Y!-!POINT_Y_1!)**(2)','PYTHON3')
    
    arcpy.Delete_management(Foto_2)
    arcpy.Delete_management(Vali_2)
    

    with arcpy.da.SearchCursor(join, ['FID','POINT_X','POINT_Y','x_rmse','y_rmse']) as cursor:
        file.write('\nINFORME DE EXACTITUD POSICIONAL ABSOLUTA \n' + arrow +
                '\n\nSistema De Referencia\n'+
                str(arcpy.Describe(fotocontrol).spatialReference.Name)+'\n'+arrow+
                '\n\nPunto'+espacio+'Coordenada X'+espacio+'Coordenada Y'+espacio+'Delta X'+espacio+espacio+espacio+'Delta Y')
            
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
        file.write('\n\n' + arrow + '\nReporte de Errores'+
                '\nUnidades del Reporte: '+espacio+espacio+'Metros'+
                '\nRMSE: '+espacio+espacio+espacio+espacio+str(rmse_r)+
                '\nNivel de Confianza: '+espacio+espacio+'95%'+
                '\nNúmero de observaciones: '+espacio+n+
                '\nRMSE 95%: '+espacio+espacio+espacio+str(round(rmse_r*1.96,2)))
        file.close()

    arcpy.Delete_management(join)
    arcpy.Delete_management(Foto_2)
    arcpy.Delete_management(Vali_2)

if __name__ == '__main__':
    RMSE(shp_validacion, shp_fotocontrol, ruta_salida)
