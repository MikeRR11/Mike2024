#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Michael Rojas
import arcpy
from arcpy.sa import *
import os
import math

GDB = arcpy.GetParameterAsText(0)

arcpy.AddMessage("INICIANDO PROCESO")


arcpy.env.workspace = GDB

#Reparar geom pa todo
def codigo(fc, field):
    # try:
        # Iniciar una sesión de edición
        edit = arcpy.da.Editor(arcpy.env.workspace)
        edit.startEditing(False, True)
        edit.startOperation()

        with arcpy.da.SearchCursor(fc,['SHAPE@','OBJECTID',field]) as sCur:
            for geometria1 in sCur:
                with arcpy.da.UpdateCursor("NombresGeograficos\\NGeogr",['SHAPE@','OBJECTID','NGIORelaci']) as uCur:
                    for geometria2 in uCur:
                        if geometria1[0].contains(geometria2[0]) == True and geometria2[1] != None:
                            arcpy.AddMessage("FEATURE CLASS:" + fc)
                            geometria2[2] = geometria1[1]
                            uCur.updateRow(geometria2) 
                            arcpy.AddMessage("Insertando: OBJECTID:" + geometria1[1] + " -  Valor del campo" + field +": " + geometria1[3])  

        # Finalizar la operación y la sesión de edición
        edit.stopOperation()
        edit.stopEditing(True)

    # except Exception as e:
    #     arcpy.AddError("Verificar estructura de datos: No se encuentra el Fearure Class " + fc)
    #     arcpy.GetMessages()

arcpy.AddMessage("Iniciando relación de identificadores con datos de tablas")
# CoberturaTierra
codigo("CoberturaTierra/AExtra", 'AEIdentif')
# ViviendaCiudadTerritorio
codigo("ViviendaCiudadTerritorio/ZDura", 'ZDIdentif')
# Hidrografia
codigo("Hidrografia/DAgua_L", 'DAIdentif')
codigo("Hidrografia/DAgua_R", 'DAIdentif')
codigo("Hidrografia/Drenaj_L", 'DIdentif')
codigo("Hidrografia/Drenaj_R", 'DIdentif')
codigo("Hidrografia/Humeda", 'HIdentif')
codigo("Hidrografia/LCoste", 'LCIdentif')
codigo("Hidrografia/Mangla", 'MgIdentif')
# Transporte
codigo("Transporte/Puente_L", 'PIdentif')
#codigo("Transporte/Embarc", 'Eldentifi')
codigo("Transporte/Telefe", 'TelIdentif')
codigo("Transporte/VFerre", 'VFIdentif')
codigo("Transporte/Via", 'VIdentif')
codigo("Transporte/Tunel", 'TIdentif')

# ViviendaCiudadTerritorio
codigo("ViviendaCiudadTerritorio/Constr_P", 'CIdentif')
# Hidrografia
codigo("Hidrografia/DAgua_P", 'DAIdentif')
# InfraestructuraServicios
codigo("InfraestructuraServicios/Pozo", 'PoIdentif')
# Transporte
codigo("Transporte/Puente_P", 'PIdentif')

arcpy.AddMessage("Proceso relación de identificadores con datos de tablas finalizado")

arcpy.AddMessage("-----------------------------------------------------------------------")
arcpy.AddMessage("PROCESO FINALIZADO")


# def codigo(fc, field):
#     try:
#         fields = ['OBJECTID', field]
#         CountDi = {}
#         with arcpy.da.SearchCursor(fc, fields) as cursor:
#             for row in cursor:
#                 CountDi[row[1]] = 1

#         campos = ["NGIORelaci"]
#         other_fc_values = set()
#         with arcpy.da.SearchCursor("NombresGeograficos\\NGeogr", campos) as cursor:
#             for row in cursor:
#                 other_fc_values.add(row[0])

#         with arcpy.da.InsertCursor("NombresGeograficos\\NGeogr", campos) as cursor:
#             for key in CountDi.keys():
#                 if key not in other_fc_values:
#                     arcpy.AddMessage(f"FEATURE CLASS:" + fc)
#                     cursor.insertRow([key])
#                     arcpy.AddMessage(f"Insertando: OBJECTID: {CountDi[key]}, Valor del campo {field}: {key}")  # Imprimir el OBJECTID y el valor del campo de los elementos insertados
#     except:
        
#         arcpy.AddError("Verificar estructura de datos: No se encuentra el Fearure Class " + fc)
#         arcpy.GetMessages()

# def codigo(fc, field):   
#     try:       
#         fields = ['OBJECTID',field]
#         CountDi = {}
#         with arcpy.da.SearchCursor (fc, fields) as cursor:
#             for row in cursor:
#                 if not row[1] in CountDi.keys():
#                     CountDi[row[1]] = 1
                    
#                 else:
#                     CountDi[row[1]] += 1
#         for key in CountDi.keys():
#             if CountDi[key] > 1:
#                 print(str(key) + ":", CountDi[key], "features")
#                 arcpy.AddMessage(fc + " Identif_Duplicado: " + str(key) + ", " + str(CountDi[key]) + "\n")
#     except:
#         arcpy.AddMessage("Proceso finalizado con errores")
#         arcpy.AddError("Verificar estructura de datos: No se encuentra el Fearure Class " + fc)
#         arcpy.AddMessage(arcpy.GetMessages())
    