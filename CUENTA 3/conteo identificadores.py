import arcpy, os, string, re, math
import sys
from arcpy import env

GDB = arcpy.GetParameterAsText(0)
RutaSalida = arcpy.GetParameterAsText(1)

def ConteoIdentificadores(GDB, RutaSalida):
    arcpy.AddMessage("Iniciando validación de conteo de identificadores")
    ws = arcpy.env.workspace = GDB
    ##path = r'D:\IGAC\2022'
    arcpy.env.overwriteOutput = True
    file = open(os.path.join(RutaSalida,'Conteo_Identif.txt'), "w")
    try:
        def conteo(fc, field):
            fields = ['OBJECTID',field]
            CountDi = {}
            with arcpy.da.SearchCursor (fc, fields) as cursor:
                for row in cursor:
                    if not row[1] in CountDi.keys():
                        CountDi[row[1]] = 1
                    else:
                        CountDi[row[1]] += 1
            for key in CountDi.keys():
                if CountDi[key] > 1:
                    print(str(key) + ":", CountDi[key], "features")
                    file.write(fc + " Identif_Duplicado: " + str(key) + ", " + str(CountDi[key]) + "\n")
       
        # CoberturaTierra
        conteo("CoberturaTierra/AExtra", 'AEIdentif')
        conteo("CoberturaTierra/Bosque", 'BIdentif')
        conteo("CoberturaTierra/ZVerde", 'ZVIdentif')
        # Elevacion
        conteo("Elevacion/CNivel", 'CNIdentif')
        conteo("Elevacion/LDTerr", 'LDTIdentif')
        # Geodesia
        conteo("Geodesia/MRTerr", 'MRTIdentif')#
        # Hidrografia
        conteo("Hidrografia/DAgua_L", 'DAIdentif')
        conteo("Hidrografia/DAgua_P", 'DAIdentif')
        conteo("Hidrografia/DAgua_R", 'DAIdentif')
        conteo("Hidrografia/Drenaj_L", 'DIdentif')
        conteo("Hidrografia/Drenaj_R", 'DIdentif')
        conteo("Hidrografia/Humeda", 'HIdentif')
        conteo("Hidrografia/Isla", 'IsIdentif')
        conteo("Hidrografia/LCoste", 'LCIdentif')#
        conteo("Hidrografia/Mangla", 'MgIdentif')
        # InfraestructuraServicios
        conteo("InfraestructuraServicios/PDistr", 'PDIdentif')
        conteo("InfraestructuraServicios/Pozo", 'PoIdentif')
        conteo("InfraestructuraServicios/RATens", 'RATIdentif')
        conteo("InfraestructuraServicios/TSPubl", 'TSPIdentif')
        conteo("InfraestructuraServicios/Tuberi", 'TubIdentif')
        # NombresGeograficos
        conteo("NombresGeograficos/NGeogr", 'NGIdentif')
        # OrdenamientoTerritorial
        conteo("OrdenamientoTerritorial/Depart", 'DeCodigo')#
        conteo("OrdenamientoTerritorial/Fronte", 'FCodigo')
        conteo("OrdenamientoTerritorial/LLimit", 'LLIdentif')
        conteo("OrdenamientoTerritorial/MDANmu", 'MDANMCodig')#
        # Transporte
        conteo("Transporte/Ciclor", 'CiIdentif')
        conteo("Transporte/LVia", 'LVIdentif')
        conteo("Transporte/Puente_L", 'PIdentif')
        conteo("Transporte/Puente_P", 'PIdentif')
        conteo("Transporte/SVial", 'SVIdentif')
        conteo("Transporte/Telefe", 'TelIdentif')
        conteo("Transporte/Tunel", 'TIdentif')
        conteo("Transporte/VFerre", 'VFIdentif')
        conteo("Transporte/Via", 'VIdentif')
        # ViviendaCiudadTerritorio
        conteo("ViviendaCiudadTerritorio/BArena", 'BAIdentif')#
        conteo("ViviendaCiudadTerritorio/Cerca", 'CeIdentif')
        conteo("ViviendaCiudadTerritorio/Constr_P", 'CIdentif')
        conteo("ViviendaCiudadTerritorio/Constr_R", 'CIdentif')
        conteo("ViviendaCiudadTerritorio/LDemar", 'LDIdentif')
        conteo("ViviendaCiudadTerritorio/Muro", 'MuIdentif')
        conteo("ViviendaCiudadTerritorio/Piscin", 'PiIdentif')
        conteo("ViviendaCiudadTerritorio/Terrap", 'TeIdentif')
        conteo("ViviendaCiudadTerritorio/ZDura", 'ZDIdentif')

       
        def idnull(fc, field):
            fields = ['OBJECTID', field]
            with arcpy.da.SearchCursor(fc, fields) as cursor:
                for row in cursor:
                    if row[1] is None or row[1] == "" or row[1] == " " or row[1] == 'None':
                        file.write(fc + " Identicador_Null," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
        arcpy.AddMessage("Iniciando validación identificadores nulos")
        # CoberturaTierra
        idnull("CoberturaTierra/AExtra", 'AEIdentif')
        idnull("CoberturaTierra/Bosque", 'BIdentif')
        idnull("CoberturaTierra/ZVerde", 'ZVIdentif')
        # Elevacion
        idnull("Elevacion/CNivel", 'CNIdentif')
        idnull("Elevacion/LDTerr", 'LDTIdentif')
        # Geodesia
        idnull("Geodesia/MRTerr", 'MRTIdentif')#
        # Hidrografia
        idnull("Hidrografia/DAgua_L", 'DAIdentif')
        idnull("Hidrografia/DAgua_P", 'DAIdentif')
        idnull("Hidrografia/DAgua_R", 'DAIdentif')
        idnull("Hidrografia/Drenaj_L", 'DIdentif')
        idnull("Hidrografia/Drenaj_R", 'DIdentif')
        idnull("Hidrografia/Humeda", 'HIdentif')
        idnull("Hidrografia/Isla", 'IsIdentif')
        idnull("Hidrografia/LCoste", 'LCIdentif')#
        idnull("Hidrografia/Mangla", 'MgIdentif')
        # InfraestructuraServicios
        idnull("InfraestructuraServicios/PDistr", 'PDIdentif')
        idnull("InfraestructuraServicios/Pozo", 'PoIdentif')
        idnull("InfraestructuraServicios/RATens", 'RATIdentif')
        idnull("InfraestructuraServicios/TSPubl", 'TSPIdentif')
        idnull("InfraestructuraServicios/Tuberi", 'TubIdentif')
        # NombresGeograficos
        idnull("NombresGeograficos/NGeogr", 'NGIdentif')
        # OrdenamientoTerritorial
        idnull("OrdenamientoTerritorial/Depart", 'DeCodigo')#
        idnull("OrdenamientoTerritorial/Fronte", 'FCodigo')
        idnull("OrdenamientoTerritorial/LLimit", 'LLIdentif')
        idnull("OrdenamientoTerritorial/MDANmu", 'MDANMCodig')#
        # Transporte
        idnull("Transporte/Ciclor", 'CiIdentif')
        idnull("Transporte/LVia", 'LVIdentif')
        idnull("Transporte/Puente_L", 'PIdentif')
        idnull("Transporte/Puente_P", 'PIdentif')
        idnull("Transporte/SVial", 'SVIdentif')
        idnull("Transporte/Telefe", 'TelIdentif')
        idnull("Transporte/Tunel", 'TIdentif')
        idnull("Transporte/VFerre", 'VFIdentif')
        idnull("Transporte/Via", 'VIdentif')
        # ViviendaCiudadTerritorio
        idnull("ViviendaCiudadTerritorio/BArena", 'BAIdentif')#
        idnull("ViviendaCiudadTerritorio/Cerca", 'CeIdentif')
        idnull("ViviendaCiudadTerritorio/Constr_P", 'CIdentif')
        idnull("ViviendaCiudadTerritorio/Constr_R", 'CIdentif')
        idnull("ViviendaCiudadTerritorio/LDemar", 'LDIdentif')
        idnull("ViviendaCiudadTerritorio/Muro", 'MuIdentif')
        idnull("ViviendaCiudadTerritorio/Piscin", 'PiIdentif')
        idnull("ViviendaCiudadTerritorio/Terrap", 'TeIdentif')
        idnull("ViviendaCiudadTerritorio/ZDura", 'ZDIdentif')

        arcpy.AddMessage("Proceso finalizado")
    except:
        arcpy.AddMessage("Proceso finalizado con errores")
        arcpy.AddError("Verificar estructura de datos")
        arcpy.AddMessage(arcpy.GetMessages())
    return
codeblock = """rec=0
def autoIncrement():
    global rec
    pStart = 1
    pInterval = 1
    if (rec == 0):
        rec = pStart
    else:
        rec += pInterval
    return rec"""
code_block ="""
def estado(a):
    if (a>1):
        b = "REVISAR"
        return b
    else:
        b = "OMITIR"
        return b"""

ConteoIdentificadores(GDB, RutaSalida)