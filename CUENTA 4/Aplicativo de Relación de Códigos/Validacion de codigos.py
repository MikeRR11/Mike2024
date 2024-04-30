#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Michael Rojas
import arcpy
from arcpy.sa import *
import os
import math

GDB = arcpy.GetParameterAsText(0)


def Identificadores(GDB):
    arcpy.env.workspace = GDB
    def codigo(fc, field):
        try:
            fields = ['OBJECTID', field]
            CountDi = {}
            with arcpy.da.SearchCursor(fc, fields) as cursor:
                for row in cursor:
                    CountDi[row[1]] = 1

            # Crear un conjunto con los valores del campo en el otro Feature Class
            other_fc_values = set()
            with arcpy.da.SearchCursor("NombresGeograficos\NGeogr,'NGIORelaci'", [field]) as cursor:
                for row in cursor:
                    other_fc_values.add(row[0])

            # Insertar los elementos que no están en ambas capas
            with arcpy.da.InsertCursor("NombresGeograficos\NGeogr,'NGIORelaci'", [field]) as cursor:
                for key in CountDi.keys():
                    if key not in other_fc_values:
                        cursor.insertRow([key])

        except:
            arcpy.AddMessage("Proceso finalizado con errores")
            arcpy.AddError("Verificar estructura de datos: No se encuentra el Fearure Class " + fc)
            arcpy.AddMessage(arcpy.GetMessages())

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
        
    arcpy.AddMessage("Iniciando relación de identificadores con datos de tablas")
    "NombresGeograficos\NGeogr,'NGIORelaci'"
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
    codigo("Transporte/Embarc", 'Eldentifi')
    codigo("Transporte/Telefe", 'TelIdentif')
    codigo("Transporte/VFerre", 'VFIdentif')
    codigo("Transporte/Via", 'VIdentif')
    codigo("Transporte/Tunel", 'TIdentif')
    arcpy.AddMessage("Proceso finalizado")
        

    def intersect(fc, field):
        fields = ['OBJECTID', field]
        with arcpy.da.SearchCursor(fc, fields) as cursor:
            for row in cursor:
                if row[1] is None or row[1] == "" or row[1] == " " or row[1] == 'None':
                    arcpy.AddMessage(fc + " Identicador_Null," + " " + "ObjectID: " + " " +  str(row[0]))
        arcpy.AddMessage("Iniciando relación de identificadores con relación espacial")
    
    # ViviendaCiudadTerritorio
    intersect("ViviendaCiudadTerritorio/Constr_P", 'CIdentif')
    # Hidrografia
    intersect("Hidrografia/DAgua_P", 'DAIdentif')
    # InfraestructuraServicios
    codigo("InfraestructuraServicios/Pozo", 'PoIdentif')
    # Transporte
    codigo("Transporte/Puente_P", 'PIdentif')

Identificadores(GDB)