#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Diego Rugeles - Michael Rojas
import arcpy

# Parámetros de entrada
GDB = arcpy.GetParameterAsText(0)
Reparar = arcpy.GetParameterAsText(1) 
arcpy.env.workspace = GDB
arcpy.AddMessage("INICIANDO PROCESO")
def repair(GDB):
    try:
        arcpy.AddMessage("Reparando Geometrías")
        arcpy.env.workspace = GDB

        # Reparar geometría para todos los feature classes en la geodatabase
        datasets = arcpy.ListDatasets(feature_type='All')
        for ds in datasets:
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                arcpy.RepairGeometry_management(fc, "DELETE_NULL", "OGC")

        arcpy.AddMessage("Geometrías reparadas exitosamente.")

    except arcpy.ExecuteError:
        # Mostrar errores
        arcpy.AddError(arcpy.GetMessages(2))
        
    except Exception as e:
        # otros errores
        arcpy.AddError(str(e))
    

def codigo(fc, field):
    try:
        # Iniciar una sesión de edición
        edit = arcpy.da.Editor(arcpy.env.workspace)
        edit.startEditing(False, True)
        edit.startOperation()
        with arcpy.da.SearchCursor(fc,['SHAPE@','OBJECTID',field]) as sCur:
            for geometria1 in sCur:
                with arcpy.da.UpdateCursor("NombresGeograficos\\NGeogr",['SHAPE@','OBJECTID','NGIORelaci']) as uCur:
                    for geometria2 in uCur:
                        if geometria1[0].contains(geometria2[0]) == True and geometria1[2] != None:
                            arcpy.AddMessage("FEATURE CLASS:" + fc)
                            geometria2[2] = geometria1[2]
                            uCur.updateRow(geometria2) 
                            arcpy.AddMessage("Insertando: OBJECTID:" + str(geometria1[1]) + " -  Valor del campo" + field +": " + str(geometria1[2]))  

        # Finalizar la operación y la sesión de edición
        edit.stopOperation()
        edit.stopEditing(True)

    except Exception as e:
        arcpy.AddWarning("Verificar estructura de datos: No se encuentra el Fearure Class " + fc)
        arcpy.AddWarning(str(e))

def drenajeR(fc, field):
    try:
        # Iniciar una sesión de edición
        edit = arcpy.da.Editor(arcpy.env.workspace)
        edit.startEditing(False, True)
        edit.startOperation()
        with arcpy.da.SearchCursor(fc,['SHAPE@','OBJECTID',field,'DTipo']) as sCur:
            for geometria1 in sCur:
                with arcpy.da.UpdateCursor("NombresGeograficos\\NGeogr",['SHAPE@','OBJECTID','NGIORelaci']) as uCur:
                    for geometria2 in uCur:
                        if geometria1[3] == 2 and geometria1[0].contains(geometria2[0]) == True and geometria1[2] != None:
                            arcpy.AddMessage("FEATURE CLASS:" + fc)
                            geometria2[2] = geometria1[2]
                            uCur.updateRow(geometria2) 
                            arcpy.AddMessage("Insertando: OBJECTID:" + str(geometria1[1]) + " -  Valor del campo" + field +": " + str(geometria1[2]))  

        # Finalizar la operación y la sesión de edición
        edit.stopOperation()
        edit.stopEditing(True)

    except Exception as e:
        arcpy.AddWarning("Verificar estructura de datos: No se encuentra el Fearure Class " + fc)
        arcpy.AddWarning(str(e))

if Reparar == "true":
    repair(GDB)
else:
    pass

arcpy.AddMessage("Iniciando relación de identificadores con datos de tablas")

# CoberturaTierra
codigo("CoberturaTierra/AExtra", 'AEIdentif')

# ViviendaCiudadTerritorio
codigo("ViviendaCiudadTerritorio/Constr_P", 'CIdentif')
codigo("ViviendaCiudadTerritorio/ZDura", 'ZDIdentif')

# Hidrografia
codigo("Hidrografia/DAgua_L", 'DAIdentif')
codigo("Hidrografia/DAgua_R", 'DAIdentif')
codigo("Hidrografia/Drenaj_L", 'DIdentif')

drenajeR("Hidrografia/Drenaj_R", 'DIdentif')

codigo("Hidrografia/Humeda", 'HIdentif')
codigo("Hidrografia/LCoste", 'LCIdentif')
codigo("Hidrografia/Isla", 'IsIdentif')
codigo("Hidrografia/Mangla", 'MgIdentif')
codigo("Hidrografia/DAgua_P", 'DAIdentif')

# Transporte
codigo("Transporte/Puente_L", 'PIdentif')
codigo("Transporte\Embarc", 'EIdentifi')
codigo("Transporte/Telefe", 'TelIdentif')
codigo("Transporte/VFerre", 'VFIdentif')
codigo("Transporte/Via", 'VIdentif')
codigo("Transporte/Tunel", 'TIdentif')
# InfraestructuraServicios
codigo("InfraestructuraServicios/Pozo", 'PoIdentif')
# Transporte
codigo("Transporte/Puente_P", 'PIdentif')

arcpy.AddMessage("-----------------------------------------------------------------------")
arcpy.AddMessage("PROCESO FINALIZADO")


#Pruebas, 
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
    