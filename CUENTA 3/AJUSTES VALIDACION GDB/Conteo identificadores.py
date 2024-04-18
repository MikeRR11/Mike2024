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
       
        conteo("InfraestructuraServicios/PDistr", 'PDIdentif')
        conteo("InfraestructuraServicios/Pozo", 'PoIdentif')
        conteo("InfraestructuraServicios/TSPubl", 'TSPIdentif')
        conteo("InfraestructuraServicios/RATens", 'RATIdentif')
        conteo("InfraestructuraServicios/Tuberi", 'TubIdentif')
        conteo("NombresGeograficos/NGeogr", 'NGIdentif')
        conteo("Transporte/Puente_P", 'PIdentif')
        conteo("Transporte/LVia", 'LVIdentif')
        conteo("Transporte/Puente_L", 'PIdentif')
        conteo("Transporte/SVial", 'SVIdentif')
        conteo("Transporte/Tunel", 'TIdentif')
        conteo("Transporte/VFerre", 'VFIdentif')
        conteo("Transporte/Via", 'VIdentif')
        conteo("Transporte/Ciclor", 'CiIdentif')
        conteo("Transporte/Telefe", 'TelIdentif')
        conteo("ViviendaCiudadTerritorio/Constr_P", 'CIdentif')
        conteo("ViviendaCiudadTerritorio/Cerca", 'CeIdentif')
        conteo("ViviendaCiudadTerritorio/Muro", 'MuIdentif')
        conteo("ViviendaCiudadTerritorio/Terrap", 'TeIdentif')
        conteo("ViviendaCiudadTerritorio/LDemar", 'LDIdentif')
        conteo("ViviendaCiudadTerritorio/Constr_R", 'CIdentif')
        conteo("ViviendaCiudadTerritorio/Piscin", 'PiIdentif')
        conteo("ViviendaCiudadTerritorio/ZDura", 'ZDIdentif')
        conteo("Elevacion/CNivel", 'CNIdentif')
        conteo("Elevacion/LDTerr", 'LDTIdentif')
        conteo("Hidrografia/DAgua_P", 'DAIdentif')
        conteo("Hidrografia/Drenaj_L", 'DIdentif')
        conteo("Hidrografia/DAgua_L", 'DAIdentif')
        conteo("Hidrografia/BArena", 'BAIdentif')
        conteo("Hidrografia/DAgua_R", 'DAIdentif')
        conteo("Hidrografia/Humeda", 'HIdentif')
        conteo("Hidrografia/Isla", 'IsIdentif')
        conteo("Hidrografia/Mangla", 'MgIdentif')
        conteo("Hidrografia/Drenaj_R", 'DIdentif')
        conteo("OrdenamientoTerritorial/LLimit", 'LLIdentif')
        conteo("OrdenamientoTerritorial/Fronte", 'FCodigo')
        conteo("CoberturaTierra/AExtra", 'AEIdentif')
        conteo("CoberturaTierra/Bosque", 'BIdentif')
        conteo("CoberturaTierra/ZVerde", 'ZVIdentif')
       
        def idnull(fc, field):
            fields = ['OBJECTID', field]
            with arcpy.da.SearchCursor(fc, fields) as cursor:
                for row in cursor:
                    if row[1] is None:
                        file.write(fc + " Identicador_Null," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
        idnull("InfraestructuraServicios/PDistr", 'PDIdentif')
        idnull("InfraestructuraServicios/Pozo", 'PoIdentif')
        idnull("InfraestructuraServicios/TSPubl", 'TSPIdentif')
        idnull("InfraestructuraServicios/RATens", 'RATIdentif')
        idnull("InfraestructuraServicios/Tuberi", 'TubIdentif')
        idnull("NombresGeograficos/NGeogr", 'NGIdentif')
        idnull("Transporte/Puente_P", 'PIdentif')
        idnull("Transporte/LVia", 'LVIdentif')
        idnull("Transporte/Puente_L", 'PIdentif')
        idnull("Transporte/SVial", 'SVIdentif')
        idnull("Transporte/Tunel", 'TIdentif')
        idnull("Transporte/VFerre", 'VFIdentif')
        idnull("Transporte/Via", 'VIdentif')
        idnull("Transporte/Ciclor", 'CiIdentif')
        idnull("Transporte/Telefe", 'TelIdentif')
        idnull("ViviendaCiudadTerritorio/Constr_P", 'CIdentif')
        idnull("ViviendaCiudadTerritorio/Cerca", 'CeIdentif')
        idnull("ViviendaCiudadTerritorio/Muro", 'MuIdentif')
        idnull("ViviendaCiudadTerritorio/Terrap", 'TeIdentif')
        idnull("ViviendaCiudadTerritorio/LDemar", 'LDIdentif')
        idnull("ViviendaCiudadTerritorio/Constr_R", 'CIdentif')
        idnull("ViviendaCiudadTerritorio/Piscin", 'PiIdentif')
        idnull("ViviendaCiudadTerritorio/ZDura", 'ZDIdentif')
        idnull("Elevacion/CNivel", 'CNIdentif')
        idnull("Elevacion/LDTerr", 'LDTIdentif')
        idnull("Hidrografia/DAgua_P", 'DAIdentif')
        idnull("Hidrografia/Drenaj_L", 'DIdentif')
        idnull("Hidrografia/DAgua_L", 'DAIdentif')
        idnull("Hidrografia/BArena", 'BAIdentif')
        idnull("Hidrografia/DAgua_R", 'DAIdentif')
        idnull("Hidrografia/Humeda", 'HIdentif')
        idnull("Hidrografia/Isla", 'IsIdentif')
        idnull("Hidrografia/Mangla", 'MgIdentif')
        idnull("Hidrografia/Drenaj_R", 'DIdentif')
        idnull("OrdenamientoTerritorial/LLimit", 'LLIdentif')
        idnull("OrdenamientoTerritorial/Fronte", 'FCodigo')
        idnull("CoberturaTierra/AExtra", 'AEIdentif')
        idnull("CoberturaTierra/Bosque", 'BIdentif')
        idnull("CoberturaTierra/ZVerde", 'ZVIdentif')
        print("End...")
    except:
        print(arcpy.GetMessages())
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