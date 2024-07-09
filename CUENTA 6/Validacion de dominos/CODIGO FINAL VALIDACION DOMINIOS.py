import arcpy, os, string, re, math
import sys
from arcpy import env
import random
import shutil #"shutil" used to remove existing directory
import statistics
import time
arcpy.env.overwriteOutput = True

GDB = arcpy.GetParameterAsText(0)
RutaSalida = arcpy.GetParameterAsText(1)
linea_guiones = "-----------------------------------------------------------------"
longitud_linea = len(linea_guiones)

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
                (row[1] == 6 and row[2] not in ['4']) or \
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

    # if errores_contador > 0:
    #     file.write("------------------------------------------------------------------------------------------------------------------#"+ "\n")
    
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
    
    # Usamos basename para obtener solo el nombre del archivo
    nombre_gdb = os.path.basename(GDB)

    # Quitamos la extensión .gdb
    nombre_sin_extension = os.path.splitext(nombre_gdb)[0]

    with open(os.path.join(RutaSalida, str(nombre_sin_extension) + ' - Errores Dominios 2_5.txt'), "w") as file:
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



ValidacionDominios2_5(GDB, RutaSalida)