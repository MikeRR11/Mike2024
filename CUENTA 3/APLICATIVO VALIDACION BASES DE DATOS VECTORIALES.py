#Desarrollo Validacion de Bases de Datos Vectoriales Modelo 2.5 / 2024
#Modificado por Diego Rugeles, Sergio Rafael Navarro, Yaritza Quevedo, Michael Rojas
#Ultima revison 01/04/2024

#Función para la validación de contar elementos
import arcpy, os, string, re, math
import sys
from arcpy import env
import random
import shutil #"shutil" used to remove existing directory
import statistics
import time
arcpy.env.overwriteOutput = True

def ValidacionCoordenadas(GDB, RutaSalida):
    arcpy.AddMessage("Iniciando validación de coordenadas")
    arcpy.env.workspace = GDB
    file = open(os.path.join(RutaSalida,'Validacion_Coordenadas_GDB.txt'), "w")
    # Script execution code goes here
    name = str(env.workspace).split("\\")
    print (name[-1])
    datasetList = arcpy.ListDatasets ('*','Feature')
    for i in datasetList:
        file.write((i) + ": "+ arcpy.Describe(i).spatialReference.name + " "+ "EPSG: " + str(arcpy.Describe(i).spatialReference.factoryCode) + "\n" )
    return
#Función para la validacion de dominios
def ValidacionDominios_2_4(GDB, RutaSalida):
    arcpy.AddMessage("Iniciando validación de dominios para modelo 2.4")
    arcpy.env.workspace = GDB
    arcpy.CheckOutExtension("spatial")
    file = open(os.path.join(RutaSalida,'Error_Tablas_2_4.txt'), "w")
    fdmdb = arcpy.ListDatasets()
    try:
        for fds in fdmdb:
            features = arcpy.ListFeatureClasses(feature_dataset=fds)
            for fc in features:
                if arcpy.Exists(fc)== True:
                    def feature(fc):
                        feature_ly =arcpy.MakeFeatureLayer_management(fc, fc+'_ly'+'null')
                        fields = ['OBJECTID', 'RuleID']
                        with arcpy.da.SearchCursor(feature_ly , fields) as cursor:
                            for row in cursor:
                                if(row[1] is None):
                                    file.write(fc + " RuleID Null " + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    feature('AExtra')
                    feature('Bosque')
                    feature('ZVerde')
                    feature('CNivel')
                    feature('LDTerr')
                    feature('MRTerr')
                    feature('BArena')
                    feature('DAgua_P')
                    feature('DAgua_R')
                    feature('Drenaj_L')
                    feature('Humeda')
                    feature('Isla')
                    feature('Mangla')
                    feature('Drenaj_R')
                    feature('DAgua_L')
                    feature('Indice')
                    feature('PDistr')
                    feature('Pozo')
                    feature('RATens')
                    feature('TSPubl')
                    feature('Tuberi')
                    feature('NGeogr')
                    feature('Depart')
                    feature('LLimit')
                    feature('Fronte')
                    feature('MDANMu')
                    feature('LVia')
                    feature('Puente_L')
                    feature('SVial')
                    feature('Tunel')
                    feature('VFerre')
                    feature('Via')
                    feature('Ciclor')
                    feature('Puente_P')
                    feature('Telefe')
                    feature('Cerca')
                    feature('Constr_P')
                    feature('Constr_R')
                    feature('Muro')
                    feature('Piscin')
                    feature('ZDura')
                    feature('Terrap')
                    feature('LDemar')                
                   
                    def CNivel(fc):
                        CNivel_ly = arcpy.MakeFeatureLayer_management("CNivel", "CNivel_ly")
                        fields = ['OBJECTID', 'CNTipo','RuleID']
                        with arcpy.da.SearchCursor(CNivel_ly, fields) as cursor:
                            for row in cursor:
                                if(row[1] != row[2]):
                                    print("{}".format(str(row[0])))
                                    file.write("Curva Tipo-RuleID," + " " + "ObjectID: " + " " + str(row[0])  + " " + "\n")
                    CNivel("CNivel_ly")
                   
                    def P_Distr(fc):
                        P_Distr_ly =arcpy.MakeFeatureLayer_management("PDistr", "P_Distr_ly")
                        fields = ['OBJECTID', 'PDTipo', 'RuleID']
                        with arcpy.da.SearchCursor(P_Distr_ly, fields) as cursor:
                            for row in cursor:
                                if(row[1] == 1 and row[2] != 1 or
                                   row[1]==2 and row[2] !=2 or
                                   row[1]==3 and row[2] !=3):
                                    file.write("PDistr Tipo-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    P_Distr("P_Distr_ly")
                    def NGeogr(fc):
                        NGeogr_ly =arcpy.MakeFeatureLayer_management("NGeogr", "NGeogr_ly")
                        fields = ['OBJECTID', 'NGCategori', 'NGSubcateg', 'NGEstado', 'RuleID']
                        with arcpy.da.SearchCursor(NGeogr_ly , fields) as cursor:
                            for row in cursor:
                                if(row[1] != row[4] and row[4] not in [15,16,17,18] or row[1] != 3 and row[4] in [3,17,18] or row[1] != 7 and row[4] in [7,15,16] or row[1] != 14 and row[4] in [14]):
                                    file.write("NGeogr Categ-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    NGeogr("NGeogr_ly")
                   
                    def Constr_P(fc):
                        Constr_P_ly =arcpy.MakeFeatureLayer_management("Constr_P", "Constr_P_ly")
                        fields = ['OBJECTID', 'CTipo', 'RuleID']
                        with arcpy.da.SearchCursor(Constr_P_ly , fields) as cursor:
                            for row in cursor:
                                if(row[1] != row[2]):
                                    file.write("Constr_P Tipo-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Constr_P("Constr_P_ly")
                    
                    def LDTerr(fc):
                        LDTerr_ly =arcpy.MakeFeatureLayer_management("LDTerr", 'LDTerr_ly')
                        fields = ['OBJECTID', 'LDTTipo', 'LDTFuente']
                        with arcpy.da.SearchCursor(LDTerr_ly , fields) as cursor:
                            for row in cursor:
                                if(row[1] is None or row[2] is None):
                                    file.write("LDTerr LDTTipo o LDTFuente es Null," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    LDTerr('LDTerr')
                    def Drenaj_L(fc):
                        Drenaj_L_ly =arcpy.MakeFeatureLayer_management("Drenaj_L", "Drenaj_L_ly")
                        fields = ['OBJECTID', 'DEstado', 'DDisperso','DNombre', 'RuleID']
                        with arcpy.da.SearchCursor(Drenaj_L_ly , fields) as cursor:
                            for row in cursor:
                                if (row[1] == 1 and row[2] == '1' and row[4]!= 4 or
                                    row[1] == 1 and row[2] == '2' and row[4]!= 3 or
                                    row[1] == 2 and row[2] == '1' and row[4]!= 2 or
                                    row[1] == 2 and row[2] == '2' and row[4]!= 1 or
                                    row[1] == 3 and row[2] not in [None] and row[4]!= 5  or
                                    row[2] in ["", " "] or
                                    row[3] in ["", " "] or
                                    row[4] is [None] or
                                    row[1] == 2 and row[3] not in [None]):
                                    file.write("Drenaj_L DEstado-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                                if (row[1] == 1 and row[3] in ["", None, " "]):
                                    file.write("Drenaj_L DEstado-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Drenaj_L("Drenaj_L_ly")
                   
                    def Drenaj_R(fc):
                        Drenaj_R_ly =arcpy.MakeFeatureLayer_management("Drenaj_R", "Drenaj_R_ly")
                        fields = ['OBJECTID', 'DTipo', 'DNombre', 'RuleID']
                        with arcpy.da.SearchCursor(Drenaj_R_ly, fields) as cursor:
                            for row in cursor:
                                if (row[1] != row[3] or row[1]==2 and row[2] in ["", " "] or row[1]==1 and row[2] not in ["", None, " "]):
                                    file.write("Drenaj_R DTipo-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Drenaj_R("Drenaj_L_ly")
                    def Puente_P(fc):
                        Puente_P_ly =arcpy.MakeFeatureLayer_management("Puente_P", "Puente_P_ly")
                        fields = ['OBJECTID', 'PuFuncion', 'RuleID']
                        with arcpy.da.SearchCursor(Puente_P_ly, fields) as cursor:
                            for row in cursor:
                                if (row[1] != row[2]):
                                    file.write("Puente_P Funcion-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Puente_P("Puente_P_ly")
                    def Puente_L(fc):
                        Puente_L_ly =arcpy.MakeFeatureLayer_management("Puente_L", "Puente_L_ly")
                        fields = ['OBJECTID', 'PuFuncion', 'RuleID']
                        with arcpy.da.SearchCursor(Puente_L_ly, fields) as cursor:
                            for row in cursor:
                                if (row[1] != row[2]):
                                    file.write("Puente_L Funcion-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Puente_L("Puente_L_ly")
                   
                    def LVia(fc):
                        LVia_ly =arcpy.MakeFeatureLayer_management("LVia", "LVia_ly")
                        fields = ['OBJECTID', 'LVTipo', 'RuleID']
                        with arcpy.da.SearchCursor(LVia_ly , fields) as cursor:
                            for row in cursor:
                                if (row[1] != row[2]):
                                    file.write("LVia Tipo-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    LVia("LVia_ly")
                    def Via(fc):
                        Via_ly =arcpy.MakeFeatureLayer_management("Via", "Via_ly")
                        fields = ['OBJECTID', 'VTipo', 'VEstado','VCarril','VAcceso','RuleID']
                        with arcpy.da.SearchCursor(Via_ly , fields) as cursor:
                            for row in cursor:
                                if ((row[1] != row[5])or
                                    (row[1] == 6 and row[3] != '0') or
                                    (row[1] == 1 and row[2] != '1') or
                                    (row[1] == 1 and row[3] != '1') or
                                    (row[1] == 1 and row[4] != '1') or
                                    (row[1] == 2 and row[2] not in ['1','2']) or
                                    (row[1] == 2 and row[3] != '2') or
                                    (row[1] == 2 and row[4] != '1') or
                                    (row[1] == 3 and row[2] not in ['2','3'])or
                                    (row[1] == 3 and row[3] != '0') or
                                    (row[1] == 3 and row[4] != '2') or
                                    (row[1] == 4 and row[2] != '4') or
                                    (row[1] == 4 and row[3] != '0') or
                                    (row[1] == 4 and row[4] != '2') or
                                    (row[1] == 5 and row[2] != '0') or
                                    (row[1] == 5 and row[3] != '0') or
                                    (row[1] == 5 and row[4] != '0') or
                                    (row[1] == 6 and row[2] != '0') or
                                    (row[1] == 6 and row[3] != '0') or
                                    (row[1] == 6 and row[4] != '0')
                                    ):
                                    file.write("Via Tipo-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Via("Via_ly")
                    def VFerre(fc):
                        VFerre_ly =arcpy.MakeFeatureLayer_management("VFerre", "VFerre_ly")
                        fields = ['OBJECTID', 'VFTipo', 'RuleID']
                        with arcpy.da.SearchCursor(VFerre_ly , fields) as cursor:
                            for row in cursor:
                                if (row[1] != row[2]):
                                    file.write("VFerre Tipo-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    VFerre("VFerre_ly")
                   
                    def Cerca(fc):
                        Cerca_ly =arcpy.management.MakeFeatureLayer("Cerca", "Cerca_ly")
                        fields = ['OBJECTID', 'CeTipo', 'RuleID']
                        with arcpy.da.SearchCursor(Cerca_ly , fields) as cursor:
                            for row in cursor:
                                if(row[1] != row[2]):
                                    file.write("Cerca Tipo-RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Cerca("Cerca_ly")
                   
                    def DAgua_R(fc):
                        DAgua_R_ly =arcpy.MakeFeatureLayer_management("DAgua_R", "DAgua_R_ly")
                        fields = ['OBJECTID','DATipo', 'RuleID']
                        with arcpy.da.SearchCursor(DAgua_R_ly , fields) as cursor:
                            for row in cursor:
                                if(row[1] != row[2]):
                                    file.write("DAgua_R Tipo_RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    DAgua_R("DAgua_R_ly")
                    def Constr_R(fc):
                        Constr_R_ly =arcpy.MakeFeatureLayer_management("Constr_R", "Constr_R_ly")
                        fields = ['OBJECTID','CTipo', 'RuleID']
                        with arcpy.da.SearchCursor(Constr_R_ly , fields) as cursor:
                            for row in cursor:
                                if(row[1] != row[2]):
                                    file.write("Constr_R Tipo_RuleID," + " " + "ObjectID: " + " " +  str(row[0]) + " " + "\n")
                    Constr_R("Constr_R_ly")
                    
                    def MDANMu(fc):
                        MDANMu_ly =arcpy.MakeFeatureLayer_management("MDANMu", "MDANMu_ly")
                        fields = ['OBJECTID', 'FCategoria', 'RuleID']
                        with arcpy.da.SearchCursor(MDANMu_ly, fields) as cursor:
                            for row in cursor:
                                if(row[1] != row[2]):
                                    print("{}".format(str(row[0])))
                                    
                                    file.write("MDANMu Categoria-RuleID," + " " + "ObjectID: " + " " + str(row[0])  + " " + "\n")
                    MDANMu("MDANMu_ly")
                    
                    print('Lastone Process.....')
                   
                arcpy.AddMessage("Informe finalizado")
                file.close()
            #break
    except:
        arcpy.AddMessage("------------------------------")
        a= arcpy.GetMessages()
        arcpy.AddMessage(a)
    return


#VALIDACION DE DOMINIOS 2.5 AJUSTADO ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

linea_guiones = "-----------------------------------------------------------------"
longitud_linea = len(linea_guiones)

#VALIDAR CONDICIONES FEATURES ------------------------------------------------------------------------------------------------------

def validarDominio(fc_path, fc_name, file):
    feature_ly = arcpy.MakeFeatureLayer_management(fc_path, fc_name + '_ly')
    errores_contador = 0
    # Validación general para todos las feature classes
    fields = ['OBJECTID', 'RuleID']
    with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
        for row in cursor:
            if row[1] is None or row[1] == "" or row[1] == " " or row[1] == 'None':
                file.write(f"{fc_name} RuleID Null, ObjectID: {row[0]}\n")
                errores_contador += 1
    with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
        for row in cursor:
            if (row[1] == '-1' or row[1] == -1 or row[1] == 'Free Representation'):
                file.write(f"{fc_name} RuleID Free Representation, ObjectID: {row[0]}\n")
                errores_contador += 1
    
# VALIDACIONES ESPECIFICAS ----------------

# CNivel 	LOS CAMPOS TIPO DE CURVA DE NIVEL Y RULE ID DEBEN SER IGUALES
    if fc_name == 'CNivel':
        fields = ['OBJECTID', 'CNTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} CNTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1
    
# LDTerr	LOS CAMPOS TIPO DE ELEVACION Y FUENTE DEBEN ESTAR DILIGENCIADOS
    if fc_name == 'LDTerr':
        fields = ['OBJECTID', 'LDTTipo', 'LDTFuente']
        with arcpy.da.SearchCursor(feature_ly , fields) as cursor:
            for row in cursor:
                if row[1] is None or row[2] is None:
                    file.write(f"{fc_name} LDTTipo o LDTFuente es Null, ObjectID: {row[0]}\n")
                    errores_contador += 1
    
# MRTerr	LOS CAMPOS TIPO DE PUNTO Y RULE ID DEBEN SER IGUALES
    if fc_name == 'MRTerr':
        fields = ['OBJECTID', 'MRTTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} MRTTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# DAgua_L	LOS CAMPOS TIPO DE DEPOSITO DE AGUA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'DAgua_L':
        fields = ['OBJECTID', 'DATipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} DATipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# DAgua_P	LOS CAMPOS TIPO DE DEPOSITO DE AGUA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'DAgua_P':
        fields = ['OBJECTID', 'DATipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} DATipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1
    
# DAgua_R	LOS CAMPOS TIPO DE DEPOSITO DE AGUA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'DAgua_R':
        fields = ['OBJECTID', 'DATipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} DATipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1
    
# Drenaj_L	SI EL ESTADO DEL DRENAJE ES "PERMANENTE" Y LA DISPERSION ES "DISPERSO", EL RULE ID DEBE ESTAR EN "PERMANENTE, DISPERSO"
    # Drenaj_L	SI EL ESTADO DEL DRENAJE ES "PERMANENTE" Y LA DISPERSION ES "NO DISPERSO", EL RULE ID DEBE ESTAR EN "PERMANENTE, NO DISPERSO"
    # Drenaj_L	SI EL ESTADO DEL DRENAJE ES "INTERMITENTE" Y LA DISPERSION ES "DISPERSO", EL RULE ID DEBE ESTAR EN "INTERMITENTE, DISPERSO"
    # Drenaj_L	SI EL ESTADO DEL DRENAJE ES "INTERMITENTE" Y LA DISPERSION ES "NO DISPERSO", EL RULE ID DEBE ESTAR EN "INTERMITENTE, NO DISPERSO"
    # Drenaj_L	SI EL TIPO DE DRENAJE ES "CANAL", LA DISPERSION DEL DRENAJE DEBE SER "NULL"
    # Drenaj_L	SI EL ESTADO DE DRENAJE ES "PERMANENTE" Y LA DISPERSION DEL DRENAJE ES "NO DISPERSO", EL CAMPO DEL NOMBRE DEBE SER DILIGENCIADO OBLIGATORIAMENTE
    
    if fc_name == 'Drenaj_L':
        fields = ['OBJECTID', 'DEstado', 'DDisperso','DNombre', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly , fields) as cursor:
            for row in cursor:
                if (row[1] == 1 and row[2] == '1' and row[4]!= 4 and row[4] is not None) or \
                   (row[1] == 1 and row[2] == '2' and row[4]!= 3 and row[4] is not None) or \
                   (row[1] == 2 and row[2] == '1' and row[4]!= 2 and row[4] is not None) or \
                   (row[1] == 2 and row[2] == '2' and row[4]!= 1 and row[4] is not None) or \
                   (row[1] == 3 and row[2] not in [None] and row[4]!= 5 and row[4] is not None)  or \
                    row[2] in ["", " "] or \
                    row[3] in ["", " "]:
                    file.write(f"{fc_name} DEstado - DDisperso - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1
                elif (row[1] == 1 and row[2] == '2' and row[3] in ["", None, " "]):
                    file.write(f"{fc_name} DEstado - DNombre, ObjectID: {row[0]}\n")
                    errores_contador += 1

# Drenaj_R	SI EL TIPO DE DRENAJE ES "CUERPO DE AGUA", EL RULE ID DEBE ESTAR EN "CUERPO DE AGUA"
    # Drenaj_R	SI EL TIPO DE DRENAJE ES "LECHO SECO", EL RULE ID DEBE ESTAR EN "LECHO SECO"
    # Drenaj_R	SI EL TIPO DE DRENAJE ES "CANAL", EL RULE ID DEBE ESTAR EN "CANAL"
    if fc_name == 'Drenaj_R':
        fields = ['OBJECTID', 'DTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if (row[1] != row[2] and row[2] is not None):
                    file.write(f"{fc_name} DTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1
                    
# PDistr 	LOS CAMPOS TIPO DE PUNTO DE DISTRIBUCION Y RULE ID DEBEN SER IGUALES
    if fc_name == 'P_Distr':
        fields = ['OBJECTID', 'PDTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if (row[1] == 1 and row[2] != 1 and row[2] is not None) or \
                   (row[1] == 2 and row[2] != 2 and row[2] is not None) or \
                   (row[1] == 3 and row[2] != 3 and row[2] is not None):
                    file.write(f"{fc_name} Tipo-RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1    
    
# Fronte	LOS CAMPOS CATEGORIA DE LA FRONTERA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'Fronte':
        fields = ['OBJECTID', 'FCategoria', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} FCategoria - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# LLimit 	SI EL NIVEL DE JERARQUIA ES "MUNICIPAL" Y EL ESTADO DE LA LINEA LIMITROFE ES "PROVISIONAL" EL RULE ID DEBE SER "LIMITE MUNICIPAL PROVISIONAL"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "MUNICIPAL" Y EL ESTADO DE LA LINEA LIMITROFE ES "DEFINIDO" EL RULE ID DEBE SER "LIMITE MUNICIPAL DEFINIDO"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "MUNICIPAL" Y EL ESTADO DE LA LINEA LIMITROFE ES "NO DEFINIDO" EL RULE ID DEBE SER "LIMITE MUNICIPAL NO DEFINIDO"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "DEPARTAMENTAL" Y EL ESTADO DE LA LINEA LIMITROFE ES "PROVISIONAL" EL RULE ID DEBE SER "LIMITE DEPARTAMENTAL PROVISIONAL"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "DEPARTAMENTAL" Y EL ESTADO DE LA LINEA LIMITROFE ES "DEFINIDO" EL RULE ID DEBE SER "LIMITE DEPARTAMENTAL DEFINIDO"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "DEPARTAMENTAL" Y EL ESTADO DE LA LINEA LIMITROFE ES "NO DEFINIDO" EL RULE ID DEBE SER "LIMITE DEPARTAMENTAL NO DEFINIDO"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "FRONTERIZO" Y EL ESTADO DE LA LINEA LIMITROFE ES "PROVISIONAL" EL RULE ID DEBE SER "LIMITE FRONTERIZO PROVISIONAL"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "FRONTERIZO" Y EL ESTADO DE LA LINEA LIMITROFE ES "DEFINIDO"
    # LLimit 	SI EL NIVEL DE JERARQUIA ES "FRONTERIZO" Y EL ESTADO DE LA LINEA LIMITROFE ES "NO DEFINIDO" EL RULE ID DEBE SER "LIMITE FRONTERIZO NO DEFINIDO"

    if fc_name == 'LLimit':
        fields = ['OBJECTID', 'RuleID', 'LLJerarqui', 'LLEstado']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                #Limite municipal
                if ((row[2]==1 and row[3]=='1' and row[1] !=9 and row[2] is not None) or
                    (row[2]==1 and row[3]=='2' and row[1] !=7 and row[2] is not None) or 
                    (row[2]==1 and row[3]=='3' and row[1] !=8 and row[2] is not None) or 
                
                    #Límite Departamental 
                    (row[2]==2 and row[3]=='1' and row[1] !=3 and row[2] is not None) or 
                    (row[2]==2 and row[3]=='2' and row[1] !=1 and row[2] is not None) or 
                    (row[2]==2 and row[3]=='3' and row[1] !=2 and row[2] is not None) or 
                    
                    #Límite forterizo
                    (row[2]==3 and row[3]=='1' and row[1] !=6 and row[2] is not None) or 
                    (row[2]==3 and row[3]=='2' and row[1] !=4 and row[2] is not None) or 
                    (row[2]==3 and row[3]=='3' and row[1] !=5 and row[2] is not None)):
                    
                    file.write(f"{fc_name} LLJerarqui - LLEstado - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# MDANMu	LOS CAMPOS CATEGORIA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'MDANMu':
        fields = ['OBJECTID', 'MDANMCateg', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} MDANMCateg - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# LVia 	LOS CAMPOS TIPO DE LIMITE VIA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'LVia':
        fields = ['OBJECTID', 'LVTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} LVTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# Puente_L	LOS CAMPOS FUNCION DEL PUENTE Y RULE ID DEBEN SER IGUALES
    if fc_name == 'Puente_L':
        fields = ['OBJECTID', 'PuFuncion', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} PuFuncion - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# Puente_P	LOS CAMPOS FUNCION DEL PUENTE Y RULE ID DEBEN SER IGUALES
    if fc_name == 'Puente_P':
        fields = ['OBJECTID', 'PuFuncion', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} PuFuncion - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# VFerre 	LOS CAMPOS TIPO DE VIA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'VFerre':
        fields = ['OBJECTID', 'VFTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} VFTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# Via	LOS CAMPOS TIPO DE VIA Y RULE ID DEBEN SER IGUALES
    # Via   SI EL TIPO DE VIA ES "VIA PRIMARIA" # EL ESTADO DE VIA DEBE SER "PAVIMENTADA" O "EN CONSTUCCION"# EL NUMERO DE CARRILES DEBE SER "CARRETERA DE 2 O MAS CARRILES" Y LA ACCESIBILIDAD DEBE SER "PERMANENTE"
    # Via	SI EL TIPO DE VIA ES "VIA SECUNDARIA", EL ESTADO DE VIA DEBE SER "PAVIMENTADA", "AFIRMADO" O "EN CONSTUCCION", EL NUMERO DE CARRILES DEBE SER "CARRETERA DE 2 O MAS CARRILES" O "CARRETERA ANGOSTA" Y LA ACCESIBILIDAD DEBE SER "PERMANENTE"
    # Via	SI EL TIPO DE VIA ES "VIA TERCIARIA", EL ESTADO DE VIA DEBE SER "PAVIMENTADA", "AFIRMADO" O "EN CONSTUCCION", EL NUMERO DE CARRILES DEBE SER "CARRETERA ANGOSTA" O "SIN VALOR" Y LA ACCESIBILIDAD DEBE SER "PERMANENTE"
    # Via	SI EL TIPO DE VIA ES "VIA CARRETEABLE", EL ESTADO DE VIA DEBE SER "SIN AFIRMADO", EL NUMERO DE CARRILES DEBE SER "SIN VALOR" Y LA ACCESIBILIDAD DEBE SER "TEMPORAL"
    # Via	SI EL TIPO DE VIA ES "PLACA HUELLA", EL ESTADO DE VIA DEBE SER "PAVIMENTADA", EL NUMERO DE CARRILES DEBE SER "SIN VALOR" Y LA ACCESIBILIDAD DEBE SER "PERMANENTE"
    # Via	SI EL TIPO DE VIA ES "CAMINO", EL ESTADO DE VIA DEBE SER "SIN PAVIMENTAR" O "SIN AFIRMADO", EL NUMERO DE CARRILES DEBE SER "SIN VALOR" Y LA ACCESIBILIDAD DEBE SER "SIN VALOR"
    # Via	SI EL TIPO DE VIA ES "VIA PEATONAL", EL ESTADO DE VIA DEBE SER "PAVIMENTADA" O "AFIRMADO", EL NUMERO DE CARRILES DEBE SER "SIN VALOR" Y LA ACCESIBILIDAD DEBE SER "PERMANENTE"

    if fc_name == 'Via':
        fields = ['OBJECTID', 'VTipo', 'VEstado','VCarril','VAcceso','RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if (row[1] == 1 and row[5] != 1 and row[5] is not None) or \
                (row[1] == 1 and row[2] not in ['1','5']) or \
                (row[1] == 1 and row[3] != '1') or \
                (row[1] == 1 and row[4] != '1') or \
                (row[1] == 2 and row[5] != 2 and row[5] is not None) or \
                (row[1] == 2 and row[2] not in ['1','3','5']) or \
                (row[1] == 2 and row[3] not in ['1','2']) or \
                (row[1] == 2 and row[4] != '1') or \
                (row[1] == 3 and row[5] != 3 and row[5] is not None) or \
                (row[1] == 3 and row[2] not in ['1','3','5']) or \
                (row[1] == 3 and row[3] not in ['0','2']) or \
                (row[1] == 3 and row[4] != '1') or \
                (row[1] == 4 and row[5] != 4 and row[5] is not None) or \
                (row[1] == 4 and row[2] != '4') or \
                (row[1] == 4 and row[3] != '0') or \
                (row[1] == 4 and row[4] != '2') or \
                (row[1] == 5 and row[5] != 5 and row[5] is not None) or \
                (row[1] == 5 and row[2] != '1') or \
                (row[1] == 5 and row[3] != '0') or \
                (row[1] == 5 and row[4] != '1') or \
                (row[1] == 6 and row[5] != 6 and row[5] is not None) or \
                (row[1] == 6 and row[2] not in ['2','4']) or \
                (row[1] == 6 and row[3] != '0') or \
                (row[1] == 6 and row[4] != '0') or \
                (row[1] == 7 and row[5] != 7 and row[5] is not None) or \
                (row[1] == 7 and row[2] not in ['1','3']) or \
                (row[1] == 7 and row[3] != '0') or \
                (row[1] == 7 and row[4] != '1'):
                    file.write(f"{fc_name} VTipo - VEstado - VCarril - VAcceso - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# Cerca	LOS CAMPOS TIPO DE CERCA Y RULE ID DEBEN SER IGUALES
    if fc_name == 'Cerca':
        fields = ['OBJECTID', 'CeTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} CeTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1
                    
# Constr_P	LOS CAMPOS TIPO DE CONSTRUCCION Y RULE ID DEBEN SER IGUALES
    # Constr_P	SI EL TIPO DE CONSTRUCCION ES "CONVENCIONAL" LA CATEGORIA DE LA CONSTRUCCION DEBE SER: "RESIDENCIAL", "COMERCIAL", "INDUSTRIAL", "EDUCATIVO", "INSTITUCIONAL", "RECREACIONAL", "RELIGIOSO"
    # Constr_P	SI EL TIPO DE CONSTRUCCION ES "NO CONVENCIONAL" LA CATEGORIA DE LA CONSTRUCCION DEBE SER: "AGROPECUARIO", "ENRRAMADA, COBERTIZO O CANEY", "GALPON Y GALLINERO", "ESTABLO Y PESEBRA", "COCHERA, MARRANERA Y PORQUERIZA", "TANQUE", "SECADERO", "MINERO", "CEMENTERIO O PARQUE CEMENTERIO", "OTRA CONSTRUCCION"
    if fc_name == 'Constr_P':
        fields = ['OBJECTID', 'CTipo', 'RuleID', 'CCategor']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if (row[1] != row[2] and row[2] is not None) or \
                (row[1] == 2 and row[3] not in [1,2,3,4,5,6,7]) or \
                (row[1] == 1 and row[3] not in [8,9,10,11,12,13,14,15,16,17]):
                    file.write(f"{fc_name} CTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

# Constr_R	LOS CAMPOS TIPO DE CONSTRUCCION Y RULE ID DEBEN SER IGUALES
    if fc_name == 'Constr_R':
        fields = ['OBJECTID', 'CTipo', 'RuleID']
        with arcpy.da.SearchCursor(feature_ly, fields) as cursor:
            for row in cursor:
                if row[1] != row[2] and row[2] is not None:
                    file.write(f"{fc_name} CeTipo - RuleID, ObjectID: {row[0]}\n")
                    errores_contador += 1

    if errores_contador > 0:
        file.write("------------------------------------------------------------------------------------------------------------------#"+ "\n")
    return errores_contador
    

def validarFeatureDominios(GDB, RutaSalida):
    arcpy.env.workspace = GDB
    arcpy.CheckOutExtension("spatial")
    total_errores = 0  

    with open(os.path.join(RutaSalida, 'Error_Tablas_2_5.txt'), "w") as file:
        fdata = arcpy.ListDatasets()
        for fds in fdata:
            features = arcpy.ListFeatureClasses(feature_dataset=fds)
            for fc in features:
                fc_path = os.path.join(GDB, fds, fc)
                if arcpy.Exists(fc_path):
                    arcpy.AddMessage(f'{f"Procesando {fc} en {fds}":.^{longitud_linea}}')
                    errores = validarDominio(fc_path, fc, file)
                    total_errores += errores if errores is not None else 0

    return total_errores

#CONTAR ERRORES FEATURES -----------------------------------------------------------------------------------------------------------------

def validarFeatureDominios(GDB, RutaSalida):
    arcpy.env.workspace = GDB
    arcpy.CheckOutExtension("spatial")
    total_errores = 0  

    with open(os.path.join(RutaSalida, 'Error_Tablas_2_5.txt'), "w") as file:
        fdata = arcpy.ListDatasets()
        for fds in fdata:
            features = arcpy.ListFeatureClasses(feature_dataset=fds)
            for fc in features:
                fc_path = os.path.join(GDB, fds, fc)
                if arcpy.Exists(fc_path):
                    arcpy.AddMessage(f'{f"Procesando {fc} en {fds}":.^{longitud_linea}}')
                    total_errores += validarDominio(fc_path, fc, file)

    return total_errores

#MENSAJES ---------------------------------------------------------------------------------------------------------------------------------
def ValidacionDominios2_5(GDB, RutaSalida):
    arcpy.AddMessage(f"{linea_guiones}\n{'INICIANDO TOOLBOX':.^{longitud_linea}}\n{linea_guiones}")
    validarDominios = validarFeatureDominios(GDB, RutaSalida)
    arcpy.AddMessage(f"{linea_guiones}\n{f'Total de errores registrado: {validarDominios}':.^{longitud_linea}}\n{linea_guiones}")
    arcpy.AddMessage(f"{linea_guiones}\n{'PROCESO FINALIZADO CON EXITO':.^{longitud_linea}}\n{linea_guiones}")


#Funcion conteo identificadores

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
def GeneracionDeMarcos(GDB,RutaSalida, Escala, Limite_Del_Proyecto, Generacion_Marcos_Control,Tipo_Producto):
    arcpy.AddMessage("Iniciando generación de marcos")
    arcpy.env.overwriteOutput = True
    ##########################################################################################################
    ###Get parameters
    ###-------------------------------------------------------------------------------------------------------
    gdbEntrada=GDB
    escala = Escala
    areaDeCorte = Limite_Del_Proyecto
    arcpy.AddMessage('areaDeCorte: ' + areaDeCorte)
    script = Generacion_Marcos_Control
    annot = Generacion_Marcos_Control
    ### Matrix giving values according to the map scale, used to define the pitch of the control grid (Fishnet).
    areas = {"1000":50, "2000":100, "5000":250, "10000":500, "25000":1000,"50000":2000,"100000":4000}
    ##########################################################################################################
    ##########################################################################################################
    ### Splitting of the different directory levels of the input GDB, down to the name of the GDB itself
    ### then creating the Log directory and Log file
    ###-------------------------------------------------------------------------------------------------------
    ruta = gdbEntrada.split("\\")
    #Keeping all the elements except the last one (the GDB itself)
    rnew = ruta[:-1]
    # Rebuilding the path to the input GDB directory
    sep = "\\"
    rutasal = RutaSalida
    # Name of the input GDB, without the .gdb extension
    namem = ruta[-1].split('.')[0]
    #### Creation of Validation (output) GDB
    # The name of the GDB + its extension
    GDB_name = "BD_Validacion_" + namem + ".gdb"
    # Real creation of the GDB
    arcpy.CreateFileGDB_management(rutasal,GDB_name)
    # Full path to the GDB
    gdbValidacion = rutasal + "\\" + GDB_name
    #### Creation of a Log directory and Log file
    # Path to the future LOG directory
    rutasalida = rutasal + "\\Log_" + namem
    # Creation of the LOG directory (destroying it first if already exists)
    if os.path.exists(rutasalida):
        shutil.rmtree(rutasalida)
    os.mkdir(rutasalida)
    arcpy.AddMessage(">>> LOG resultados en: "+rutasalida+"\\"+"Report_"+namem+".txt")
    arcpy.AddMessage(" -------------------------------------------------------------------------")
    arcpy.AddMessage(" -------------------------------------------------------------------------")
    ### Creation of the LOG file
    filet = open(rutasalida+"\\"+"Report_"+namem+".txt","a")
    filet.write("-------- REPORTE DEL SCRIPT PARA LA GDB " + namem + " --------\n")
    filet.write("> Creación de Marcos... feature classes en " + gdbValidacion + "\n\n")
    ##########################################################################################################
    ##########################################################################################################
    ###  Creation of a function "autoIncrement()" allowing to create the auto-incremented identifiers of the "salidagrillain" objects,
    ### i.e. of the "MarcosInt_..." (which are the set of complete squares in the polygon defining the cutting area.
    ###-------------------------------------------------------------------------------------------------------
    ###
    ##########################################################################################################
    ### Fonction "SelectRandomByCount"
    ###---------------------------------------------------------------------------------------------------------
   
    def SelectRandomByCount(layer, count, salidapuntos):
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
        arcpy.MakeFeatureLayer_management (layer, "stateslyrs")
        arcpy.SelectLayerByAttribute_management("stateslyrs", "", sql)
        arcpy.CopyFeatures_management("stateslyrs", salidapuntos)
        arcpy.Delete_management("stateslyrs")
    ##########################################################################################################
    ##########################################################################################################
    #                                          --- MARCOS ---
    ##########################################################################################################
    if annot == "true":
        arcpy.env.workspace = gdbEntrada
        dcList = arcpy.ListDatasets()
        for ds in dcList:
            for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
                if(arcpy.Exists(fc+"_Anot")):
                    arcpy.AddMessage("Eliminando " + fc+ "_Anot")
                    arcpy.management.Delete(fc+"_Anot")
                else:
                    pass
    if script == 'true':
        # Keeping time stamp
        marcos_start_time = time.localtime()
        time_string = time.strftime("%H:%M:%S", marcos_start_time)
        arcpy.AddMessage('Creacion de los Marcos - Start time: ' + time_string)
        filet.write("Creacion de los Marcos - Start time: " + time_string + "\n")
        ### STEP 0 - If the area of interest ("Area de Corte") value is empty (which will be translated
        # in '#'), the script will use contour lines bounding box (Elevacion/CNivel) as default AOI
        if areaDeCorte == '#':
            inFc = os.path.join(gdbEntrada, 'Elevacion', 'CNivel')
            outFc = os.path.join(gdbValidacion, 'Default_Area_de_Corte')
            result = int(arcpy.GetCount_management(inFc).getOutput(0))
            arcpy.AddMessage(">>>No se especifico area de corte, se calculara usando los datos de las curvas de nivel")
            filet.write("> No se especifico area de corte, se calculara usando los datos de las curvas de nivel\n\n")
            if result > 0:
                arcpy.MinimumBoundingGeometry_management(inFc, outFc, "CONVEX_HULL", "ALL")
                fcCorte=outFc
                #arcpy.AddMessage('fcCorte: ' + fcCorte)
            else:
                arcpy.AddMessage(">>>No hay datos sufifientes para calcular el area de corte, por favor generela manuelmente")
                arcpy.AddMessage(">>>                     END OF SCRIPT")
                filet.write("> No hay datos sufifientes para calcular el area de corte, por favor generela manuelmente. END OF SCRIPT\n\n")
                sys.exit()
        else:
            fcCorte = areaDeCorte
            arcpy.AddMessage('>>>Uso del área de corte: '+ fcCorte)
            filet.write("> Uso del área de corte: " + fcCorte + "\n\n")
        arcpy.AddMessage(" -------------------------------------------------------------------------")
        arcpy.AddMessage(" -------------------------------------------------------------------------")
        ### STEP 1 - Input GDB is clipped with area of interest
        CORTE = fcCorte
        arcpy.AddMessage("Fase 1 - Cortando Geodatabase.")
        filet.write("Fase 1 - Cortando Geodatabase.\n")
        arcpy.env.workspace = gdbEntrada
        #
        datasetList = arcpy.ListDatasets()
        n_error=0 #conteo de errores en clip
        for dataset in datasetList:
            if(dataset!="IndiceMapas" and dataset!="OrdenamientoTerritorial"):
                arcpy.AddMessage('>>Analizando Dataset '+dataset)
                filet.write('>>Analizando Dataset '+dataset + "\n")
                arcpy.env.workspace = gdbEntrada + "\\" + dataset
                descd = arcpy.Describe(gdbEntrada + "\\" + dataset)
                sr = descd.spatialreference
                arcpy.CreateFeatureDataset_management(gdbValidacion, dataset, sr)
                fcList = arcpy.ListFeatureClasses()
                for fc in fcList:
                    result = int(arcpy.GetCount_management(fc).getOutput(0))
                    try:
                        if result>0:
                            #arcpy.AddMessage('-----Cortando FeatureClass '+fc)
                            filet.write("-----Corte del Feature "+fc + "\n")
                            fcSal=gdbValidacion + "\\" + dataset + "\\" + fc
                            desc = arcpy.Describe(fc)
                            if(desc.featureType!="Annotation"):
                               
                                if(arcpy.Exists(fc+"_Anot")):
                                    try:
                                        arcpy.Clip_analysis(fc+"_Anot", CORTE , fcSal+"_Anot")
                                        arcpy.AddMessage("Cortando" + str(fc))
                                   
                                    except arcpy.ExecuteError:
                                        #arcpy.AddMessage(arcpy.GetMessages())
                                        n_error=n_error+1
                                        arcpy.AddMessage('Existen errores graves de topología en la Feature Class '+str(fc)+'_Anot' +
                                                         ' que impiden la ejecución de la herramienta Generacion de Marcos')
                                        filet.write('Existen errores graves de topología en la Feature Class '+str(fc)+'_Anot' +
                                                         ' que impiden la ejecución de la herramienta Generacion de Marcos\n')
                                try:
                                    arcpy.Clip_analysis(fc, CORTE , fcSal)
                                except Exception:
                                    #arcpy.AddMessage(arcpy.GetMessages())
                                    n_error=n_error+1
                                    arcpy.AddMessage('Existen errores graves de topología  en la Feature Class ' + str(fc) +
                                                     ' que impiden la ejecución de la herramienta Generacion de Marcos')
                                    filet.write('Existen errores graves de topología en la Feature Class ' + str(fc) +
                                                     ' que impiden la ejecución de la herramienta Generacion de Marcos')
                               
                    except Exception as ex:
                        arcpy.AddMessage("Error..."+ex.message)
        #arcpy.AddMessage('Total Errores: '+str(n_error))
        if n_error >= 1: #si encontro errores de topologia no ejecuta los demas pasos
            arcpy.AddMessage('No se pudo terminar la ejecución de la herramienta Generacion de Marcos')
            filet.write('No se pudo terminar la ejecución de la herramienta Generacion de Marcos')
        else:
            del datasetList
            del fcList
            arcpy.AddMessage("GDB Cortada.")
            filet.write("GDB Cortada.\n")
            ### STEP 2 - Creation of control square areas (Marcos)
            arcpy.AddMessage("Fase 2 - Generando grilla.")
            filet.write("Fase 2 - Generando grilla.")
            ### Sub-Step 2-1 - First "MarcosAT" which covers with squares the whole bounding box the the area of interest)
            valesc = areas[str(escala)]
            sptref = arcpy.Describe(fcCorte).spatialreference
            extent = arcpy.Describe(fcCorte).extent
            arcpy.env.outputCoordinateSystem = sptref
            coords = str(extent.XMin) + " " + str(extent.YMin)
            yAxisCoordinate = str(extent.XMin) + " " + str(extent.YMin+1)
            oppositeCoorner = str(extent.XMax) + " " + str(extent.YMax)
            ###'MarcosAT' is directlty stored in the Validation GDB
            outpg = gdbValidacion + "\\" + 'MarcosAT'
            arcpy.CreateFishnet_management(outpg, coords, yAxisCoordinate, valesc, valesc, "0", "0", oppositeCoorner, "NO_LABELS", "", "POLYGON")
            resultgr = int(arcpy.GetCount_management(outpg).getOutput(0))
            arcpy.AddMessage("Grilla Total Generada con "+str(resultgr)+" celdas...")
            filet.write("Grilla Total Generada con "+str(resultgr)+" celdas..." + "\n")
            ### Sub-Step 2-2 - Creation of second feature class "MarcosInt" keeping only squares within the AOI
            #Interseccion Area Proyecto
            salidagrillain = gdbValidacion + "\\" + 'MarcosInt'  # Only a path for now
            # Creation of a temporary layer pointing on 'MarcosAT' feature class
            arcpy.MakeFeatureLayer_management (outpg, "grillat")
            # Selection of 'MarcosAT' features which are completely within the AOI (Area de Corte)
            arcpy.SelectLayerByLocation_management("grillat", "COMPLETELY_WITHIN", fcCorte)
            # Result is stored
            arcpy.CopyFeatures_management("grillat", salidagrillain)  # Now 'MarcosInt' feature class really exists
            # Utilisation of the function created before to add an unique ID 'Id' to each object of 'MarcosInt'
            expression = "autoIncrement()"
            arcpy.management.CalculateField(salidagrillain, "Id", expression, "PYTHON3", codeblock)
            # New field 'Num_elm' that will be used later to store the number of elements within each square
            arcpy.AddField_management(salidagrillain, "Num_elm", "DOUBLE", 0, "", "", "", "NULLABLE", "NON_REQUIRED")
            # Calculation of total number of cells in 'MarcosInt'
            resultgri = int(arcpy.GetCount_management(salidagrillain).getOutput(0))
            arcpy.AddMessage("Grilla Intersectada con area de trabajo, "+str(resultgri)+" celdas...")
            filet.write("Grilla Intersectada con area de trabajo, "+str(resultgri)+" celdas..." + "\n")
            # The temporary layer is no more useful
            arcpy.Delete_management("grillat")
       
       
            ### STEP 3 - Keeping 30 cells of 'MarcosInt' (or all if not enough)
            arcpy.AddMessage("Fase 3 - Selección de las celdas.")
            filet.write("Fase 3 - Selección de las celdas.")
            if resultgri>30:
                arcpy.AddMessage("Se seleccionaran 30 marcos de los "+str(resultgri)+" intersectados...")
                filet.write("Se seleccionaran 30 marcos de los "+str(resultgri)+" intersectados..." + "\n")
                salidagrillai = gdbValidacion + "\\" + 'Marcos30' # Only a path for now
                SelectRandomByCount(salidagrillain,30,salidagrillai)  # 30 squares randomly among 'MarcosInt'
                opcion = 'Caso 1'
            else:
                arcpy.AddMessage('Guardamos todas las '+ str(resultgri) + ' celdas de MarcosInt')
                filet.write("Guardamos todas las " + str(resultgri) + " celdas de MarcosInt" + "\n")
                salidagrillai = gdbValidacion + "\\" + 'MarcosInt'  # Not only a path as 'MarcosInt' already exists with its (<=30) objects
                opcion = 'Caso 2'
            ### STEP 4 - Calculation of number of entities for each feature class for each of the 30 (or less) cells
            field_names = [i.name for i in arcpy.ListFields(salidagrillai) if i.type != 'OID']
            #['Shape', 'Id', 'Num_elm', 'Shape_Length', 'Shape_Area'] (if 'Marcos30')
            cursor = arcpy.da.SearchCursor(salidagrillai, field_names)
            # These will store the total number of each group for the whole 30 (or less) cells
            numelementos = 0   # Otros que Bosque y Cerca
            numelementos_bacm = 0  # Bosque and Cerca
            #For each of the 30 (or less) cells:
            for row in cursor:
                #arcpy.AddMessage('row: ' + str(row))
                #Position of "Id" field is different according to slidagrillai source (Marcos30 or MarcosInt)
                if opcion == 'Caso 1':  # Marcos30
                    idc = row[1]
                elif opcion == 'Caso 2': # MarcosInt
                    idc = row[3]
                arcpy.AddMessage('Calculando Grilla Id: '+ str(idc))
                filet.write('Calculando Grilla Id: '+ str(idc) + "\n")
                # Creation of a temporary layer pointing on the selected cells
                arcpy.MakeFeatureLayer_management(salidagrillai, "grillac")
                # Creation of expression to select only the current cell
                exp = "Id = '"+str(idc)+"'"
                arcpy.SelectLayerByAttribute_management("grillac","NEW_SELECTION",exp)
                # Then with all the feature classes clipped from the input GDB
                arcpy.env.workspace = gdbValidacion
                datasetList = arcpy.ListDatasets()
                # These will store the total number of each group for each cell
                numcapas = 0
                numcapas_bacm = 0
                # For each dataset:
                for dataset in datasetList:
                    arcpy.env.workspace = gdbValidacion + "\\" + dataset
                    fcList = arcpy.ListFeatureClasses()
                    #For each Feature Class:
                    for fc in fcList:
                        #a SHP is created to keep only the objects of the FC which intersect the current cell,
                        # only to count them, then the SHP is deleted...
                        outName_gr = rutasalida + "\\" + 'Gr_'+str(idc)+str(fc)+'.shp'  # Just a path
                        inFeatures_pc = ["grillac", fc]
                        #arcpy.AddMessage('inFeatures_pc: ' + str(inFeatures_pc))
                        arcpy.Intersect_analysis(inFeatures_pc, outName_gr)
                        result = int(arcpy.GetCount_management(outName_gr).getOutput(0))
                        #arcpy.AddMessage("El numero de elementos de "+str(fc)+" es: "+str(result))
                        filet.write("El numero de elementos de "+str(fc)+" es: "+str(result) + "\n")
                        #
                        if (str(fc) == 'Bosque' or str(fc) == 'Cerca'):
                            numcapas_bacm += result
                        else:
                            numcapas += result
                        arcpy.Delete_management(outName_gr)
                # The 'Num_elm' field of the selected cell is given the 'numcapas' value
                arcpy.management.CalculateField("grillac", "Num_elm", numcapas, "PYTHON3")
                #arcpy.AddMessage("El numero de elementos en la grilla "+ str(idc)+" categoria otros es: "+ str(numcapas))
                #arcpy.AddMessage("El numero de elementos en la grilla "+ str(idc)+" categoria bacm es: "+ str(numcapas_bacm))
                filet.write("El numero de elementos en la grilla "+ str(idc)+" categoria otros es: "+ str(numcapas) + "\n")
                filet.write("El numero de elementos en la grilla "+ str(idc)+" categoria bacm es: "+ str(numcapas_bacm) + "\n")
           
                arcpy.Delete_management("grillac")
                # Total number of objects in each cell
                numelementos += numcapas
                numelementos_bacm += numcapas_bacm
            ##arcpy.AddMessage("El numero de elementos categoria otros en todas las celdas es "+ str(numelementos))
            ##arcpy.AddMessage("El numero de elementos categoria bacm en todas las celdas es "+ str(numelementos_bacm))
            # Temporary layer is deleted
            arcpy.Delete_management("grillac")
            ### STEP 5 - Statistics
            if numelementos < numelementos_bacm:
                arcpy.AddMessage("El mayor conteo de elementos fue en la categoria bacm y se usará un p de 0.05 ")
                p = 0.03
                count = int (numelementos_bacm)
                salidatb = rutasalida + "\\tablagr"
                arcpy.Statistics_analysis(salidagrillai, salidatb, [["Num_elm", "SUM"]])
                field_namespr = [i.name for i in arcpy.ListFields(salidatb) if i.type != 'OID']
                cursorpr = arcpy.da.SearchCursor(salidatb, field_namespr)
                datapr =[row for row in cursorpr]
                numel_total = datapr[0][2]
            else:
                arcpy.AddMessage("El mayor conteo de elementos fue en la categoria otros y se usará un p de 0.03 ")
                p = 0.05
                count = int(numelementos)
                salidatb = rutasalida + "\\tablagr"
                arcpy.Statistics_analysis(salidagrillai, salidatb, [["Num_elm", "SUM"]])
                field_namespr = [i.name for i in arcpy.ListFields(salidatb) if i.type != 'OID']
                cursorpr = arcpy.da.SearchCursor(salidatb, field_namespr)
                datapr =[row for row in cursorpr]
                numel_total = datapr[0][2]
           
       
            arcpy.AddMessage('numel_total: ' + str(numel_total))
            ### Final number of cells (30 or less)
            result= arcpy.GetCount_management(salidagrillai)
            numel_gr = int(result.getOutput(0))
            arcpy.AddMessage('numel_gr: ' + str(numel_gr))
            ### Mean number of objects per cell
            pr_elmgr = (numel_total/numel_gr)
            ###
            arcpy.AddMessage("pr_elmgr es: "+ str(pr_elmgr))
            ### This result is multiplied by the total number of elements of 'MarcosInt'
            numel_totales = pr_elmgr*resultgri
            ### Activation 2 messages commentés
            arcpy.AddMessage("numel_total es: "+ str(numel_total))      #1317
            arcpy.AddMessage("numel_totales es: "+ str(numel_totales))  #13916,3
            ### Formula: https://www.qualtrics.com/fr/gestion-de-l-experience/etude-marche/calcul-taille-echantillon/
            ### 1,96 is scoreZ for a 95% level of confidence
            z = 1.96
            ### "p" is standard deviation. "p" can be 0.03 or 0.05 depending on previous tests
            ### "e" = margin of error?
            e = 0.01
            a = (z*z)*(p)*(1-p)
            b = (e*e)
            g = a/b
            count = int(numel_totales)
            c = (count-1)/ float(count)
            d = count*(e*e)
            ef = a/d
            f = c + ef
            o = g/f
            n = int(o)
            ###
            arcpy.AddMessage("n es: "+ str(n))
            filet.write("n es: "+ str(n) + "\n")
            ###Arrondi à l'entier le plus proche :
            num_mr = int(math.ceil(n/pr_elmgr))
            conteo =  str(arcpy.management.GetCount(salidagrillain))
            if Tipo_Producto == "Rural":
                marcos = int(conteo) *0.16
            else:
                 marcos = int(conteo) *0.33
            marcos_int = math.trunc(marcos)
            ###
            arcpy.AddMessage("num_mr es: "+ str(marcos_int))
            filet.write("num_mr es: "+ str(marcos_int) + "\n")
       
            ### 2 possibilties according to "num_mr" value:
            #    - if <=15: all previously created Marcos are kept
            #    - if >15: new "MarcosCS_..." are calculated
            arcpy.AddMessage("Tamaño de muestra minimo en elementos "+str(n))
            filet.write("\n \n")
            filet.write("Tamaño de muestra minimo en elementos "+str(n) + "\n")
            if marcos_int <= 15:
                arcpy.AddMessage("El numero de marcos obtenidos es "+str(marcos_int)+ " se dejaran todos los marcos inicialmente generados, "+ str(numel_gr))
                filet.write("El numero de marcos obtenidos es "+str(marcos_int)+ " se dejaran todos los marcos inicialmente generados, "+ str(numel_gr) + "\n")
            else:
                arcpy.AddMessage("El numero de marcos obtenidos es "+str(marcos_int)+ ", se extraera dicha cantidad de marcos.")
                filet.write("El numero de marcos obtenidos es "+str(marcos_int)+ ", se extraera dicha cantidad de marcos." + "\n")
                arcpy.AddMessage("Generando Marcos Aleatorios..")
                out_points = gdbValidacion + "\\" + 'MarcosCS'
                SelectRandomByCount(salidagrillain,marcos_int,out_points)
                arcpy.AddMessage("Marcos de control generados")
                filet.write("Marcos de control generados" + "\n")
                filet.write("El numero de elementos categoria otros en todas las celdas es "+ str((numelementos*marcos_int)/30) + "\n")
                filet.write("El numero de elementos categoria bacm en todas las celdas es "+ str((numelementos_bacm* marcos_int)/30) + "\n")
         
    return
def LimpiarCapasVacias(Vista_Mapa):
    arcpy.AddMessage("Iniciando limpieza de capas vacias")
    try:
        mapa = Vista_Mapa
        arcpy.AddMessage(type(mapa))
        arcpy.AddMessage(mapa)
        lista_mapa = mapa.split(";")
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        arcpy.AddMessage("Proyecto:\n"+aprx.filePath)
        #arcpy.AddMessage("Mapas de entrada: "+lista_mapa)
        for lis in lista_mapa:
            m = aprx.listMaps(lis)[0]
            arcpy.AddMessage(str(m.name))
            #m.name = mapa
            l = m.listLayers()
            remove = []
            for lyr in l:
                rowCount = arcpy.GetCount_management(lyr)
                if int(str(rowCount))==0:
                    arcpy.AddMessage("Capas a remover: "+str(lyr)+"-"+str(rowCount)+"\n del mapa: "+str(m.name))
                    print("Capas a remover: "+str(lyr)+"-"+str(rowCount))
                    remove.append(lyr)
                    arcpy.AddMessage(len(remove))
                if len(remove) != 0 or remove !=[]:
                    arcpy.AddMessage("***Removiendo las capas sin información de la vista")
                    print("***Removiendo las capas sin información de la vista")
                    for lyr in remove:
                        m.removeLayer(lyr)
                        arcpy.AddMessage("***Se han removido las capas sin datos del mapa")
                        print("***Se han removido las capas sin datos del mapa")
                else:
                    arcpy.AddMessage("No existen capas vacias")
                    print("No existen capas vacias")
    except Exception as e:
        print("Error: " + e.args[0])
        """
        import arcpy
        mapa = arcpy.Vista_Mapa
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        arcpy.AddMessage("Proyecto:\n"+aprx.filePath)
        arcpy.AddMessage(mapa)
        arcpy.AddMessage(type(mapa))
        lista_mapa = mapa.split(";")
        arcpy.AddMessage("Mapas de entrada: "+lista_mapa)
        """
    return
def MarcosDeControlOrtoyMDT(Limite_Del_Proyecto,RutaSalida,Escala):
    arcpy.AddMessage("Iniciando marcos de control Orto y MDT")
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
        arcpy.MakeFeatureLayer_management (layer, "stateslyrs")
        arcpy.SelectLayerByAttribute_management("stateslyrs", "", sql)
        arcpy.CopyFeatures_management("stateslyrs", salidapuntos)
        arcpy.Delete_management("stateslyrs")
       
    def Marcos(param0, param1, param2):
        areas = {"1000":200, "2000":400, "5000":1000, "10000":2000, "25000":4000,"50000":8000}
        OutFc= param1
        nombregdb = "Marcos_Control_Orto_MDT.gdb"
        salida = arcpy.management.CreateFileGDB(OutFc, nombregdb)
        ruta_salida = param1 +  "\\" +  nombregdb
        escala = param2
        arcpy.AddMessage("Calculando marcos de control")
        valesc = areas[str(escala)]
        sptref = arcpy.Describe(param0).spatialreference
        extent = arcpy.Describe(param0).extent
        arcpy.env.outputCoordinateSystem = sptref
        Ymin = str(extent.YMin)
        Xmin = str(extent.XMin)
        Ymax = str(extent.YMax)
        Xmax = str(extent.XMax)
        Ymin_1 = str(extent.YMin + 1)
        print(type(Ymin))
        coords = Xmin + " "+ (Ymin)
        yAxisCoordinate = Xmin + " " + Ymin_1
        oppositeCoorner = Xmax + " " +Ymax
        outpg = ruta_salida + "\\" + "MarcosAT"
        arcpy.CreateFishnet_management(outpg, coords, yAxisCoordinate, valesc, valesc, "0", "0", oppositeCoorner, "NO_LABELS", "", "POLYGON")
        resultgr = int(arcpy.GetCount_management(outpg).getOutput(0))
        arcpy.AddMessage("Grilla Total Generada con "+str(resultgr)+" celdas...")
        # Creacion de marcos de control dentro del limite del proyecto
        salidagrillain = ruta_salida + "\\" + 'MarcosInt'  # Only a path for now
        arcpy.MakeFeatureLayer_management(outpg, "grillat")
        arcpy.SelectLayerByLocation_management("grillat", "COMPLETELY_WITHIN", param0)
        arcpy.CopyFeatures_management("grillat", salidagrillain)  # Now 'MarcosInt' feature class really exists
        expression = "autoIncrement()"
        arcpy.management.CalculateField(salidagrillain, "Id", expression, "PYTHON3", codeblock)
        arcpy.AddField_management(salidagrillain, "Num_elm", "DOUBLE", 0, "", "", "", "NULLABLE", "NON_REQUIRED")
        resultgri = int(arcpy.GetCount_management(salidagrillain).getOutput(0))
        arcpy.AddMessage("Grilla Intersectada con area de trabajo, "+str(resultgri)+" celdas...")
        arcpy.Delete_management("grillat")
        conteo =  str(arcpy.management.GetCount(salidagrillain))
        fields = ["SHAPE@AREA"]
        with arcpy.da.SearchCursor(param0, fields) as cursor:
            #for every row in the shapefiles attribute table
            for row in cursor:
                a = round(row[0]/10000)
        if(param2 == "1000" and a <= 1000 or
           param2 == "2000" and a <= 1000 or
           param2 == "5000" and a <= 15000 or
           param2 == "10000" and a <= 25000 or
           param2 == "25000" and a <= 100000 or
           param2 == "50000" and a <= 1000000):
            marcos = int(conteo) *1
        elif(param2 == "1000" and a in range(1001,2000) or
             param2 == "2000" and a in range(1001,2000) or
             param2 == "5000" and a in range(15001,30000)  or
             param2 == "10000" and a in range(25001,50000) or
             param2 == "25000" and a in range(100001,500000)or
             param2 == "50000" and a in range(1000001,5050000)):
            marcos = int(conteo) *0.55
        elif(param2 == "1000" and a in range(2001,10000) or
             param2 == "2000" and a in range(2001,10000) or
             param2 == "5000" and a in range(30001,50000)  or
             param2 == "10000" and a in range(50001,100000) or
             param2 == "25000" and a in range(500001,1000000)or
             param2 == "50000" and a in range(5005001,10000000)):
            marcos = int(conteo) *0.35
        elif(param2 == "1000" and a > 10001 or
             param2 == "2000" and a > 10001 or
             param2 == "5000" and a > 50001 or
             param2 == "10000" and a > 100001 or
             param2 == "25000" and a > 1000001 or
             param2 == "50000" and a > 10000001):
            marcos = int(conteo) *0.25
        marcos_int = math.trunc(marcos)
        salidagrillai = ruta_salida + "\\" + 'MarcosRevisar' # Only a path for now
        SelectRandomByCount(salidagrillain, marcos_int, salidagrillai)
        return
    # This is used to execute code if the file was run but not imported
    if __name__ == '__main__':
        # Tool parameter accessed with GetParameter or GetParameterAsText
     
        param0 = Limite_Del_Proyecto
        param1 = RutaSalida
        param2 = Escala
        Marcos(param0, param1, param2)
       
        # Update derived parameter values using arcpy.SetParameter() or arcpy.SetParameterAsText()
    return
# This is used to execute code if the file was run but not imported
def CorteGeodatabase(GDB,Limite_Del_Proyecto,RutaSalida,Nombre_De_La_Nueva_Geodatabase):
    arcpy.AddMessage("Iniciando corte GDB")
    #arcpy.env.autoCancelling = False
    gdb = GDB
    poligono = Limite_Del_Proyecto
    foldersalida =RutaSalida
    nombregdb =Nombre_De_La_Nueva_Geodatabase
    #gdb = "C:/Users/marlon.ruiz/Documents/Toolbox_Corte_Geodatabase/100K_2019_V1.gdb"
    #poligono = "C:/Users/marlon.ruiz/Documents/Toolbox_Corte_Geodatabase/CHIRIBIQUETE_50K.shp"
    #foldersalida = "C:/Users/marlon.ruiz/Documents/Toolbox_Corte_Geodatabase"
    #nombregdb = "prueba_xml"
    try:
        if arcpy.env.isCancelled==False:
            if arcpy.Exists(foldersalida+"/"+nombregdb+".gdb")==False:
                arcpy.AddMessage("GDB de entrada:\n"+gdb+"\nPoligno de recorte:\n"+poligono+"\nGDB de salida:\n"+foldersalida+"/"+nombregdb+".gdb")
                arcpy.AddMessage("Exportando esquema de la base de datos de entrada")
                arcpy.ExportXMLWorkspaceDocument_management(gdb, foldersalida+"/"+nombregdb+".xml", "SCHEMA_ONLY", "BINARY", "METADATA")
                #Creando la nueva GDB
                dWs = arcpy.Describe(gdb)
                desc = arcpy.Describe(poligono)
                if (gdb[-4:]==".gdb" or gdb[-4:]==".mdb") and desc.shapeType == "Polygon":
                    if dWs.workspaceFactoryProgID != "":
                        arcpy.AddMessage("***Creando la nueva base de datos")
                        arcpy.CreateFileGDB_management(foldersalida,nombregdb + ".gdb")
                        arcpy.AddMessage("***Base de datos creada "+nombregdb + ".gdb")
                        arcpy.AddMessage("Importando el esquema a la nueva base de datos")
                        arcpy.ImportXMLWorkspaceDocument_management(foldersalida+"/"+nombregdb+".gdb",  foldersalida+"/"+nombregdb+".xml", "SCHEMA_ONLY", "DEFAULTS")
                        arcpy.AddMessage("Esquema importado a la nueva base de datos")
                        arcpy.AddMessage("Creando una base de datos temporal en la ruta de salida")
                        arcpy.CreateFileGDB_management(foldersalida,"temporal.gdb")
                        arcpy.AddMessage("***\nPor favor no intente abrir la gdb Temporal ni la creada\n")
                        arcpy.env.workspace = dWs.path+"/"+dWs.baseName+".gdb"
                        LFD = arcpy.ListDatasets("","Feature")
                        arcpy.AddMessage("***Features Dataset dentro de la gdb de entrada \n ")
                        for l in LFD:
                            arcpy.AddMessage("\t"+l)
                        arcpy.AddMessage("***\nPor favor no intente abrir la gdb Temporal ni la creada\n")
                        for fd in LFD:
                            spreference = arcpy.Describe(fd).spatialReference
                            gdbentrada = foldersalida+"/temporal.gdb"
                            #la siguiente funcion varia respecto a pro
                            arcpy.management.CreateFeatureDataset(gdbentrada,fd,spreference)
                        LFC_vacios=[]
                        LFC=[]
                        arcpy.AddMessage("***\nPor favor no intente abrir la gdb Temporal ni la creada\n")
                        for fd in LFD:
                            arcpy.env.workspace = dWs.path+"/"+dWs.baseName+".gdb/"+str(fd)
                            datos=arcpy.ListFeatureClasses()
                            #arcpy.AddMessage(str(fd)+"\n\n"+str(datos)+"\n\n")
                            #Realizando el clip para las capas en los fature dataset creados
                            for i in datos:
                                entrada= dWs.path+"/"+dWs.baseName+".gdb/"+str(fd)+"/"+str(i)
                                salida=foldersalida+"/temporal.gdb"+"/"+str(fd)+"/"+str(i)
                                destino=foldersalida+"/"+nombregdb+".gdb"+"/"+str(fd)+"/"+str(i)
                                arcpy.analysis.Clip(entrada,poligono,salida, None)
                                #arcpy.AddMessage("\nRuta del Feature class generado, recortado por el poligono\n\n"+poligono+":\n"+str(salida))
                                if int(arcpy.management.GetCount(salida).getOutput(0)):
                                    #arcpy.AddMessage("\n\n\t\t\t No esta vacia\n\n")
                                    arcpy.management.Append(salida,destino,"NO_TEST")
                                    LFC.append(destino)
                                else:
                                    #arcpy.AddMessage("\n\n\t\t\t Vacia\n\n")
                                    LFC_vacios.append(destino)
                        arcpy.AddMessage("***\nPor favor no intente abrir la gdb Temporal ni la creada\n")
                        arcpy.AddMessage("\n***Features Class con informacion dentro de la gdb de salida \n ")
                        for l1 in LFC:
                            arcpy.AddMessage("\t"+l1)
                        arcpy.AddMessage("***\nPor favor no intente abrir la gdb Temporal ni la creada\n")
                        arcpy.AddMessage("\n***Features Class vacios dentro de la gdb de salida \n ")
                        for l2 in LFC_vacios:
                            arcpy.AddMessage("\t"+l2)
                #arcpy.management.Delete(foldersalida+"/"+nombregdb+".xml")
                #arcpy.management.Delete(foldersalida+"/temporal.gdb")
                #arcpy.management.Delete(foldersalida+"/"+nombregdb+".gdb")
            else:
                arcpy.AddError("La base de datos de destino YA existe, por favor ingrese un nombre distinto para la GDB\n O elimine la base del directorio\n"+foldersalida)
        #elif arcpy.env.isCancelled==True:
        #    raise arcpy.ExecuteError
    except arcpy.ExecuteError as err:
        arcpy.AddError(err)
    finally:
        # If tool is cancelled or finishes successfully, clean up intermediate data
        #if arcpy.Exists(foldersalida+"/"+nombregdb+".gdb")==True:
        #    arcpy.management.Delete(foldersalida+"/"+nombregdb+".gdb")
        arcpy.AddMessage(arcpy.GetMessages())
        if arcpy.Exists(foldersalida+"/"+nombregdb+".xml")==True:
            arcpy.management.Delete(foldersalida+"/"+nombregdb+".xml")
        if arcpy.Exists(foldersalida+"/temporal.gdb")==True:
            arcpy.management.Delete(foldersalida+"/temporal.gdb")
    return
def VerificacionSentidoDrenaje(GDB,RutaSalida):
    arcpy.AddMessage("Iniciando verificación sentido drenaje")
   
    _name_='_main_'
    def getworkspacedatset(dtaset):
        try:
            ndataset=""
            wsp=""
            lruta=dtaset.split(os.sep)
            ndataset= lruta[len(lruta)-1]
            wsp=dtaset.replace(os.sep+ndataset,"")
            return wsp, ndataset
        except:
            import traceback
            arcpy.AddError(traceback.format_exc())
    def VerificarDrenajeEnds(dstCAgua,gdbEntrada,RutaSalida):
        try:
            ruta = gdbEntrada.split("\\")
            #Keeping all the elements except the last one (the GDB itself)
            rnew = ruta[:-1]
            # Rebuilding the path to the input GDB directory
            sep = "\\"
            rutasal = RutaSalida
            # Name of the input GDB, without the .gdb extension
            namem = ruta[-1].split('.')[0]
            #### Creation of Validation (output) GDB
            # The name of the GDB + its extension
            GDB_name = "Sentido_Drenajes_" + namem + ".gdb"
            # Real creation of the GDB
            arcpy.CreateFileGDB_management(rutasal,GDB_name)
            # Full path to the GDB
            gdbValidacion = rutasal + "\\" + GDB_name
            #### Creation of a Log directory and Log file
            # Path to the future LOG directory
            arcpy.AddMessage("---Verificando diredccion drenajes---")
            drSencillo= dstCAgua+ os.sep+ "Drenaj_L"
            tempdrenaje=gdbValidacion+os.sep+"temp_dreneje"
            ptdrenaje=gdbValidacion+os.sep+"puntos_drenaje"
            out_Pol="Poligonos"
            rutaPol=gdbValidacion + os.sep+out_Pol
            out_Linea="Linea"
            rutaLinea=gdbValidacion  + os.sep+out_Linea
            puntoerease=gdbValidacion  + os.sep+"puntos_earease"
            lypterase=gdbValidacion  + os.sep+"Ly_puntos_earease"
            ptintermedios=gdbValidacion  + os.sep+"Puntos_intermedios"
            intputosdr=gdbValidacion  + os.sep+"Int_puntos_dr"
            lypuntos=gdbValidacion  + os.sep+"ly_Int_puntos_dr"
            lypuntosdef=gdbValidacion  + os.sep+"ly_puntos_def"
            puntosdef=gdbValidacion + os.sep+"Puntos_revision"
            if arcpy.Exists(tempdrenaje )== True:
                    arcpy.Delete_management(tempdrenaje)
            if arcpy.Exists(ptdrenaje)== True:
                    arcpy.Delete_management(ptdrenaje)
            if arcpy.Exists(rutaLinea)== True:
                    arcpy.Delete_management(rutaLinea)
            if arcpy.Exists(rutaPol)== True:
                    arcpy.Delete_management(rutaPol)
            if arcpy.Exists(puntoerease)== True:
                    arcpy.Delete_management(puntoerease)
            if arcpy.Exists(lypterase)== True:
                    arcpy.Delete_management(lypterase)
            if arcpy.Exists(ptintermedios)== True:
                    arcpy.Delete_management(ptintermedios)
            if arcpy.Exists(intputosdr)== True:
                    arcpy.Delete_management(intputosdr)
            if arcpy.Exists(lypuntos)== True:
                    arcpy.Delete_management(lypuntos)
            if arcpy.Exists(lypuntosdef)== True:
                    arcpy.Delete_management(lypuntosdef)
            if arcpy.Exists(puntosdef)== True:
                    arcpy.Delete_management(puntosdef)
            if arcpy.Exists(drSencillo)== True:
                arcpy.AddMessage("-----Generando vertices---")
                arcpy.CopyFeatures_management(drSencillo, tempdrenaje)
                arcpy.AddField_management(tempdrenaje,"IDDREN","LONG")
                exp= "!OBJECTID!"
                arcpy.CalculateField_management(tempdrenaje, "IDDREN", exp, "PYTHON_9.3")
                arcpy.FeatureVerticesToPoints_management(tempdrenaje, ptdrenaje, "END")
                arcpy.AddMessage("-----Generando Layer linea y poligono intermedios---")
                spr=arcpy.Describe(dstCAgua).spatialReference
                arcpy.CreateFeatureclass_management(gdbValidacion , out_Pol, "POLYGON","","","",spr)
                arcpy.CreateFeatureclass_management(gdbValidacion , out_Linea, "POLYLINE","","","",spr)
                ws,dtset = getworkspacedatset(dstCAgua)
                arcpy.env.workspace =ws
                fcListPol = arcpy.ListFeatureClasses("*","polygon",dtset)
                fcListLine=arcpy.ListFeatureClasses("*","polyline",dtset)
            for fcPol in fcListPol:
                if arcpy.Exists(fcPol)== True:
                    nelementos=int(arcpy.GetCount_management(fcPol).getOutput(0))
                if nelementos>0 :
                    arcpy.Append_management([fcPol], rutaPol,"NO_TEST")
            for fcLine in fcListLine:
                if arcpy.Exists(fcLine)== True:
                    nelementos=int(arcpy.GetCount_management(fcLine).getOutput(0))
                    descf= arcpy.Describe(fcLine)
                if nelementos>0 and descf.name != "Drenaj_L" :
                    arcpy.Append_management([fcLine], rutaLinea,"NO_TEST")
            arcpy.AddMessage("-----seleccionando vertices---")
            arcpy.Erase_analysis(ptdrenaje, rutaPol, puntoerease)
            arcpy.MakeFeatureLayer_management(puntoerease, lypterase)
            arcpy.SelectLayerByLocation_management(lypterase, "INTERSECT", rutaLinea, "", "NEW_SELECTION", "INVERT")
            arcpy.CopyFeatures_management(lypterase, ptintermedios)
            if int(arcpy.GetCount_management(ptintermedios).getOutput(0))>0:
                arcpy.Intersect_analysis([ptintermedios,tempdrenaje], intputosdr, "ALL")
                if gdbValidacion.find("mdb")!=-1:
                    qryrev="[IDDREN]"+ " <> " +"[IDDREN_1]"
                else:
                    qryrev="\"" + "IDDREN" +"\""+ " <> " +"\"" + "IDDREN_1" +"\""
                    idsdr=[]
                arcpy.MakeFeatureLayer_management(intputosdr,lypuntos, qryrev)
                cursor = arcpy.SearchCursor(lypuntos)
                for row in cursor:
                    iddren= row.getValue("IDDREN")
                    idsdr.append(iddren)
                del cursor
                qryrev=""
                for nid in idsdr:
                    if qryrev=="":
                        if gdbValidacion.find("mdb")!=-1:
                            qryrev="[IDDREN]"+ " NOT IN (" +str(nid)
                        else:
                            qryrev="\"" + "IDDREN" +"\""+ " NOT IN (" +str(nid)
                    else:
                        qryrev=qryrev +" , " + str(nid)
                if qryrev!= "":
                    qryrev=qryrev +" )"
                    arcpy.MakeFeatureLayer_management(ptintermedios, lypuntosdef,qryrev )
                    arcpy.CopyFeatures_management(lypuntosdef, puntosdef)
                else:
                    arcpy.AddMessage("---No se Encontraron Inconsistencias---")
            else:
                arcpy.AddMessage("---No se Encontro El Feature Class Drenaje Sencillo---")
            if arcpy.Exists(tempdrenaje )== True:
                    arcpy.Delete_management(tempdrenaje)
            if arcpy.Exists(ptdrenaje)== True:
                    arcpy.Delete_management(ptdrenaje)
            if arcpy.Exists(rutaLinea)== True:
                    arcpy.Delete_management(rutaLinea)
            if arcpy.Exists(rutaPol)== True:
                    arcpy.Delete_management(rutaPol)
            if arcpy.Exists(puntoerease)== True:
                    arcpy.Delete_management(puntoerease)
            if arcpy.Exists(lypterase)== True:
                    arcpy.Delete_management(lypterase)
            if arcpy.Exists(ptintermedios)== True:
                    arcpy.Delete_management(ptintermedios)
            if arcpy.Exists(intputosdr)== True:
                    arcpy.Delete_management(intputosdr)
            if arcpy.Exists(lypuntos)== True:
                    arcpy.Delete_management(lypuntos)
            if arcpy.Exists(lypuntosdef)== True:
                    arcpy.Delete_management(lypuntosdef)
        except:
            import traceback
            arcpy.AddError(traceback.format_exc())
    if _name_=='_main_':
        dstCAgua=os.path.join(str(GDB),'Hidrografia')
        #gdbValidacion=GDB
        gdbEntrada = GDB
        VerificarDrenajeEnds(dstCAgua,gdbEntrada,RutaSalida)
    return
if __name__ == '__main__':
    # Tool parameter accessed with GetParameter or GetParameterAsText
    Contar_Elementos = sys.argv[1]
    Validacion_Coordenadas = sys.argv[2]
    Validacion_Dominios_2_4 = sys.argv[3]
    Validacion_Dominios_2_5 = sys.argv[4]
    Conteo_identificadores = sys.argv[5]
    Generacion_Marcos_Control = sys.argv[6]
    limpiar_Capas_Vacias =sys.argv[7]
    Marcos_De_Control_Orto_y_MDT = sys.argv[8]
    Corte_Geodatabase = sys.argv[9]
    Verificacion_Sentido_Drenaje = sys.argv[10]
    GDB = sys.argv[11]
    RutaSalida = sys.argv[12]
    Escala = sys.argv[13]
    Vista_Mapa =sys.argv[14]
    Limite_Del_Proyecto = sys.argv[15]
    Nombre_De_La_Nueva_Geodatabase = sys.argv[16]
    Tipo_Producto = sys.argv[17]
   
    if Contar_Elementos == 'true':
        Contar_Elementos(GDB, RutaSalida)
    if Validacion_Coordenadas == 'true':
        ValidacionCoordenadas(GDB, RutaSalida)
    if Validacion_Dominios_2_4 == 'true':
        ValidacionDominios_2_4(GDB, RutaSalida)
    if Validacion_Dominios_2_5 == 'true':
        ValidacionDominios2_5(GDB, RutaSalida)
    if Conteo_identificadores  == 'true':
        ConteoIdentificadores(GDB, RutaSalida)
    if Generacion_Marcos_Control == 'true':
         GeneracionDeMarcos(GDB,RutaSalida, Escala, Limite_Del_Proyecto, Generacion_Marcos_Control, Tipo_Producto)
    if limpiar_Capas_Vacias == 'true':
            LimpiarCapasVacias(Vista_Mapa)
    if Marcos_De_Control_Orto_y_MDT == 'true':
        MarcosDeControlOrtoyMDT(Limite_Del_Proyecto,RutaSalida,Escala)
    if Corte_Geodatabase == 'true':
        CorteGeodatabase(GDB,Limite_Del_Proyecto,RutaSalida,Nombre_De_La_Nueva_Geodatabase)
    if Verificacion_Sentido_Drenaje == 'true':
        VerificacionSentidoDrenaje(GDB,RutaSalida)
    else:
        pass
