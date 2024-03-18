# Desarrollo de Pendientes para MDT 
# Semillero de Investigación y Desarrollo (2024)
# Michael Rojas - Yaritza Quevedo 

import arcpy
import os
from arcpy import env

municipios = r""
#municipios = r"\\172.26.0.20\Elite_Sub_Geografia_Cartografia\Coberturas\GDB_FLET_Agosto_2023.gdb\Limites_Entidades_Territoriales\Munpio"

Salida = arcpy.GetParameterAsText(0)
Limite = arcpy.GetParameterAsText(1) 
Divipola = arcpy.GetParameterAsText(2)
Ruta = "Elite\{0}" .format(str(Divipola))

#DIGITAR MUNICIPIO DANE

Corte = arcpy.management.Clip("SRTM_30_Col1.tif", "in_template_dataset", , {in_template_dataset}, {nodata_value}, {clipping_geometry}, {maintain_clipping_extent})
#HACER RECORTE MDT

#Generar pendientes con MDT
pendientes_MDT= Slope(Limite, "PERCENT_RISE", method="PLANAR")
pendientes_MDT.save(filename="Pendientes_CLIP", ignore_discard=False, ignore_expires=False)

#HACER REPORTE
