from arcpy import metadata as md
import arcpy
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from lxml import etree
import openpyxl
from openpyxl import load_workbook
####### Definicion funciones:
def tiempo_actual():
    hora_actual = datetime.now()
    return str(hora_actual.hour)+str(hora_actual.minute)+str(hora_actual.hour)
#Crear GDB:
def crearGDB(path):
    GDB_output= arcpy.CreateFileGDB_management(out_folder_path=path,out_name='GDB_salida'+str(tiempo_actual()))
    return GDB_output
#Funcion que retorna datos del XML
def getdata_from_xml(atributo):
    global tree
    tofind= (str('.//{http://www.isotc211.org/2005/gmd}'+str(atributo)))
    x_element= tree.find(tofind)
    value_element=x_element.find(".//{http://www.isotc211.org/2005/gco}CharacterString").text
    return value_element
#Funcion para validar exactitud de diligenciamiento en valores de las etiquetas del xml: 
def validar_param(nombreetiqueta, valorabuscar, idregla):
    error=0
    x=getdata_from_xml(nombreetiqueta)
    if not str(valorabuscar).replace(" ","").replace("\n","").replace(".","")== str(x).replace(" ","").replace("\n","").replace(".",""):
        error+=1
    else:
        error=0
    if error>0:
        row_values = [(idregla,nombreetiqueta, 'No corresponde al valor del metadato establecido.')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
    return 1
####Inputs:
exported_xml= arcpy.GetParameterAsText(0)
#exported_xml=r"E:\22_IGAC\2. Proyectos\3. Desarrollos\9. Validacion_Metadatos_mdt\Desarrollo\salida\MDT1_25200014_20230815_tif.xml"
folder_output= arcpy.GetParameterAsText(1)
#folder_output= "E:\\22_IGAC\\2. Proyectos\\3. Desarrollos\\9. Validacion_Metadatos_mdt\\Desarrollo\\salida"
revision_metadatos_igac=arcpy.GetParameter(2)
depto = arcpy.GetParameter(3)
#Se crea tabla que contendrá el resumen y sus respectivos campos:
gdb=crearGDB(folder_output)
summary=arcpy.CreateTable_management(out_path=gdb, out_name='summary')
arcpy.management.AddField(in_table=summary, field_name='id_validacion', field_type="TEXT")
arcpy.management.AddField(in_table=summary, field_name='etiqueta', field_type="TEXT")
arcpy.management.AddField(in_table=summary, field_name='observacion', field_type="TEXT")
arcpy.management.AddField(in_table=summary, field_name='concepto', field_type="TEXT")
###### Ejecución desarrollo:
item_md = md.Metadata(exported_xml)   # Se cargan los metadatos
"""
print("Tags:", item_md.tags)
print("Summary:", item_md.summary)
print("Description:", item_md.description)
print("Credits:", item_md.credits)
print("Access Constraints:", item_md.accessConstraints)
""" 
##Exportar metadato de capa deseada a XML en formato GML32:
#exported_xml= os.path.join(folder_output, 'xml_gml_32.xml')
#exported_xml= os.path.join(folder_output, 'xml'+str(layer1).replace(".","_"))
#item_md.exportMetadata(exported_xml, 'ISO19139_GML32')
###################################################
###############Inicio de validaciones##############: 
###################################################
### Navegar sobre XML:
#tree = etree.parse(exported_xml)
tree = ET.parse(exported_xml)
#print(getdata_from_xml("CI_Telephone"))
#print(getdata_from_xml("keyword"))
#print(getdata_from_xml("electronicMailAddress"))
################ INICIO VALIDACION #####################
date_format = '%Y%m%d'
##1. fileIdentifier:   Orto10_Metadato_25438003_20210110

if revision_metadatos_igac == True:
    arcpy.AddMessage("Iniciando validación de metadato con estructura interna IGAC")
else:
    arcpy.AddMessage("Iniciando validación de metadato")

if depto == True:
    arcpy.AddMessage("Tipo de producto: Producto Departamental")
else:
    arcpy.AddMessage("Tipo de producto: No Departamental")

try: 
    error=0
    print(getdata_from_xml("fileIdentifier"))
    x=getdata_from_xml("fileIdentifier")
    if not str(x).startswith('MDT') or ('Metadato' not in x):
        error+=1
    else:
        error=0
    try:
        dateObject = datetime.strptime(x[-8:], date_format)
        print(dateObject)
    except ValueError:
        error+=1
        arcpy.AddMessage("Incorrecto formato de fecha en etiqueta fileIdentifier, debe ser YYYYMMDD")
    if error>0:
        row_values = [('1','fileidentifier', 'No cumple con la estructura')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
except AttributeError:
    arcpy.AddMessage("No se encuentra la etiqueta fileIdentifier dentro del XML")
if revision_metadatos_igac is True:   
    ##2. organisationName. Instituto Geográfico Agustín Codazzi
    try:
        validar_param('organisationName','Instituto Geográfico Agustín Codazzi','2')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta organisationName dentro del XML")
    ##3. organisationName. Subdirección Cartográfica y Geodésica
    try:
        validar_param('positionName','Subdirección Cartográfica y Geodésica','3')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta positionName dentro del XML")
    ##4. CI_Telephone. +57 (601) 6531888
    try:
        validar_param('CI_Telephone','+57 (601) 6531888','4')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta CI_Telephone dentro del XML")
    ##5. deliveryPoint. Carrera 30 # 48 - 51 – Sede Central
    try:
        validar_param('deliveryPoint','Carrera 30 # 48 - 51 - Sede Central','5')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta deliveryPoint dentro del XML")
    ##6. city. Bogotá
    try:
        validar_param('city','Bogotá D.C.','6')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta city dentro del XML")
    
    ##7. administrativeArea. Cundinamarca
    try:
        validar_param('administrativeArea','Cundinamarca','7')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta administrativeArea dentro del XML")
    ##8. postalCode. 111321
    try:
        validar_param('postalCode','111321','8')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta postalCode dentro del XML")
    ##9. electronicMailAddress. contactenos@igac.gov.co
    try:
        validar_param('electronicMailAddress','contactenos@igac.gov.co','9')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta electronicMailAddress dentro del XML")
    ##10. contactInstructions. texto
    try:
        validar_param('contactInstructions','Abierto al público de lunes a viernes de 9:00 a.m. a 4:00 p.m. jornada continua Sede Central y territorial Cundinamarca','10')
    except AttributeError:
        arcpy.AddMessage("No se encuentra la etiqueta contactInstructions dentro del XML")
else:
    pass
##11. metadataStandardName. texto
validar_param('metadataStandardName','ISO 19139 Geographic Information - Metadata - Implementation Specification','11')
"""
##11b. pointInPixel. texto
error=0
md_pixel_orientation_code = tree.find(".//pointInPixel/MD_PixelOrientationCode")
if md_pixel_orientation_code is not None:
    valor = md_pixel_orientation_code.text
    if valor =="center":
        pass
    else:
        error+=1
    print("Valor de MD_PixelOrientationCode:", valor)
else:
    print("MD_PixelOrientationCode no encontrado en el XML")
if error>0:
    row_values = [('11b','PointInPixel', 'No es igual a: center')]
    with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
        for row in row_values:
            cursor.insertRow(row)
"""
##12. title:   Ortoimagen. Departamento de XXX. Municipio de XXXXX. GSD XXX cm. Año XXXX
try:
    if depto == True:
        error=0
        x=getdata_from_xml("title")
        if not str(x).startswith('Modelo Digital de Terreno. Departamento de ') or ('. Malla ' not in x) or ('. Año ' not in x):
            error+=1
        else:
            error=0
        if error>0:
            row_values = [('12','title', 'No cumple con la estructura')]
            with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
                for row in row_values:
                    cursor.insertRow(row)
    else:
        error=0
        x=getdata_from_xml("title")
        if not str(x).startswith('Modelo Digital de Terreno. Departamento de ') or ('. Municipio de ' not in x)  or ('. Malla ' not in x) or ('. Año ' not in x):
            error+=1
        else:
            error=0
        if error>0:
            row_values = [('12','title', 'No cumple con la estructura')]
            with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
                for row in row_values:
                    cursor.insertRow(row)
except AttributeError:
    arcpy.AddMessage("No se encuentra la etiqueta title dentro del XML")

##13. alternateTitle:   Orto10_25740013_20230823

try:
    error=0
    x=getdata_from_xml("alternateTitle")
    if not str(x).startswith('MDT') or ('_' not in x):
        error+=1
    else:
        error=0
    if error>0:
        row_values = [('13','alternateTitle', 'No cumple con la estructura')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
    ##14. date:   2023-01-05T08:05:56
    # Encuentra la etiqueta <gco:DateTime>
    gco_datetime = tree.find('.//{http://www.isotc211.org/2005/gco}DateTime')
    if gco_datetime is not None:
        datetime_value = gco_datetime.text
    else:
        datetime_value=''
    date_format = '%Y-%m-%d'
    error=0
    x=datetime_value
    if 'T' not in x:
        error+=1
    else:
        error=0
    try:
        dateObject = datetime.strptime(x[0:10], date_format)
        print(dateObject)
    except ValueError:
        error+=1
        print("Incorrect data format, should be YYYY-MM-DD")
    if error>0:
        row_values = [('14','date', 'No cumple con la estructura')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
except AttributeError:
    arcpy.AddMessage("No se encuentra la etiqueta alternateTitle dentro del XML")
    ##15. abstract:

try:
    error=0
    x=getdata_from_xml("abstract")
    if ('El modelo digital del terreno corresponde a una malla regular de puntos o celdas ráster espaciadas cada' not in str(x) or 
        'metro' not in x or '. Se extiende a ' not in x or ' hectáreas efectivas. El proceso se realizó con imágenes provenientes del sensor ' not in x or 
        '. Fecha de toma:' not in x or
        'de ' not in x or
        'de ' not in x       
        ):
        error+=1
    else:
        error=0
    if error>0:
        row_values = [('15','abstract', 'No cumple con la estructura')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
    ##16. purpose:
    error=0
    x=getdata_from_xml("purpose")
    if not str(x).startswith('Servir como insumo básico para la realización de estudios suburbanos y rurales como análisis de riesgos y amenazas, análisis hidrológicos, planificación de ordenación y manejo ambiental, ordenamiento territorial, deslindes, análisis espacial, entre otros.'):
        error+=1
    else:
        error=0
    if error>0:
        row_values = [('16','purpose', 'No cumple con la estructura')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
except AttributeError:
    arcpy.AddMessage("No se encuentra la etiqueta abstract dentro del XML")

##17. keyword:
try:
    if depto == "True":
        error=0
        x=getdata_from_xml("keyword")
        if not str(x).startswith('República de Colombia, Departamento de ') not in x: 
            error+=1
        else:
            error=0
        if error>0:
            row_values = [('17','keyword', 'No cumple con la estructura')]
            with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
                for row in row_values:
                    cursor.insertRow(row)
    else:
        error=0
        x=getdata_from_xml("keyword")
        if not str(x).startswith('República de Colombia, Departamento de ') or ' Municipio de ' not in x: 
            error+=1
        else:
            error=0
        if error>0:
            row_values = [('17','keyword', 'No cumple con la estructura')]
            with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
                for row in row_values:
                    cursor.insertRow(row)
except AttributeError:
    arcpy.AddMessage("No se encuentra la etiqueta keyword dentro del XML")


##18. useLimitation:
try:
    error=0
    x=getdata_from_xml("useLimitation")
    if not str(x).startswith('Producto generado para escalas iguales o menores a escala 1:'): 
        error+=1
    else:
        error=0
    if error>0:
        row_values = [('18','useLimitation', 'No cumple con la estructura')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
    ##19. statement:
    error=0
    x=getdata_from_xml("statement")
    if not str(x).startswith('El aseguramiento de la calidad se validó al 100% de los elementos en el MDT de') or  'el cual presenta una malla de ' not in x or 'Se verificó el cumplimiento de los parámetros de calidad definidos en la Especificación Técnica 471-2020/529-2020, en los elementos y subelementos de calidad, determinándose que el sistema de referencia cumple, ya que tiene asignado MAGNA SIRGAS Origen-Nacional, así mismo cumple con los parámetros de calidad de Totalidad (omisión, comisión), consistencia del MDT y exactitud posicional. Posteriormente se realizó el proceso de validación en el cual se logró determinar el cumplimiento de estos parámetros, lo cual permitió dar el concepto de APROBADO al MDT ' not in x:
        error+=1
    else:
        error=0
    if error>0:
        row_values = [('19','statement', 'No cumple con la estructura')]
        with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
            for row in row_values:
                cursor.insertRow(row)
except AttributeError:
    arcpy.AddMessage("No se encuentra la etiqueta useLimitation dentro del XML")
"""
##20. cornerPoints:
error=0
# Buscar todas las etiquetas <gml:pos>
pos_elements = tree.findall(".//gml:pos", namespaces={"gml": "http://www.opengis.net/gml"})
# Obtener los valores de <gml:pos>
for pos_element in pos_elements:
    value = pos_element.text.strip()  # Obtener el texto dentro de la etiqueta
    arcpy.AddMessage("Valor de <gml:pos>:", value)
##21. tranformationDimesionDecription. Transformación Bilienal
#validar_param('tranformationDimesionDecription','Transformación Bilienal','21')
"""
##22. code. Transformación Bilienal
try:
    validar_param('code','9377','22')
except AttributeError:
    arcpy.AddMessage("No se encuentra la etiqueta code dentro del XML")
##23. attributeDescription. Niveles Digitales
error=0
record_type_element = tree.find('.//{http://www.isotc211.org/2005/gco}RecordType')
if record_type_element is not None:
    # Obtiene el valor de <gco:RecordType>
    record_type_value = record_type_element.text
    if "Modelo Digital de Terreno"  in record_type_value:
        error=0
    else:
        error+=1
else: 
    error+=1
if error>0:
    row_values = [('23','attributeDescription', 'No cumple con la estructura')]
    with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
        for row in row_values:
            cursor.insertRow(row)
##24. distance:
distance_element = tree.find('.//{http://www.isotc211.org/2005/gco}Distance')
if distance_element is not None:
    # Obtiene el valor y la unidad del atributo "uom"
    distance_value = distance_element.text
    uom = distance_element.get("uom")
    if distance_value==0 or  len(distance_value)==0 or  distance_value is None:
        error+=1
    else:
        error=0
if error>0:
    row_values = [('24','distance', 'Distancia incorrecta')]
    with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
        for row in row_values:
            cursor.insertRow(row)
if distance_element is not None:
    # Obtiene el valor y la unidad del atributo "uom"
    distance_value = distance_element.text
    uom = distance_element.get("uom")
    if uom==0 or  len(uom)==0 or uom is None:
        error+=1
    else: 
        error=0
if error>0:
    row_values = [('24','distance', 'Unidad de medida incorrecta')]
    with arcpy.da.InsertCursor(summary, ['id_validacion', 'etiqueta', 'observacion']) as cursor:
        for row in row_values:
            cursor.insertRow(row)
excel = arcpy.TableToExcel_conversion(summary, os.path.join(folder_output, 'ValidacionMetadato_'+str(tiempo_actual())+'_'+str(os.path.basename(exported_xml)).replace(".","_")+'.xlsx'))
try:
    arcpy.Delete_management(gdb)
except:
    pass
finally:
    pass
    #arcpy.Delete_management(exported_xml)
wb_2 = load_workbook(str(excel)) #excel maestro
validacion = wb_2["summary"] #hoja datos mdt excel maestro
inconsistencias = float(len(validacion["A"])) - 1
arcpy.AddMessage("--------------------CONCEPTO--------------------")
arcpy.AddMessage("El total de inconsistencias es: " +str(inconsistencias))

if ((validacion["A2"].value is None) or (validacion["A2"].value == "") or (validacion["A2"].value == " ")):
    arcpy.AddMessage("Aprobado")
    validacion["E2"] = "Aprobado"
else:
    arcpy.AddMessage("No Aprobado")
    validacion["E2"] = "No Aprobado"
wb_2.save(str(excel))
try:
    arcpy.Delete_management(gdb)
except:
    pass
finally:
    pass
    #arcpy.Delete_management(exported_xml)