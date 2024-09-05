#Desarrollado por Sergio Rafael Navarro / Diego Rugeles 
#Aplicativo para convertir tabla excel en feature class y calcular areas de estaciones Geodesicas
#Version 2.0
#24 de abril de 2024

import arcpy
import os

def join_excel(excel, ruta_salida, mun, cp, mun_dobles,mp_rural,pnn):
    nombre_gdb = "GDB_Info_Integrada_DGIG.gdb"
    sr = arcpy.SpatialReference(9377)
    workspace = os.path.join(ruta_salida, nombre_gdb)

    arcpy.AddMessage("Creando geodatabase en la ruta especificada...")
    arcpy.management.CreateFileGDB(ruta_salida, nombre_gdb)
    arcpy.AddMessage("Geodatabase creada exitosamente.")
    
    editor = arcpy.da.Editor(workspace)
    editor.startEditing(False, True)
    editor.startOperation()
    
    try:
        arcpy.AddMessage("Convirtiendo hoja ESTADO_CARTOGRAFIA_R de Excel a tabla...")
        table_excel_mun = arcpy.conversion.ExcelToTable(excel, os.path.join(ruta_salida, nombre_gdb, "Carto_Rural"), "ESTADO_CARTOGRAFIA_R")
        arcpy.AddMessage("Datos de ESTADO_CARTOGRAFIA_R convertidos exitosamente.")

        arcpy.AddMessage("Convirtiendo hoja CARTO_CP de Excel a tabla...")
        table_excel_cp = arcpy.conversion.ExcelToTable(excel, os.path.join(ruta_salida, nombre_gdb, 'Carto_Urbana'), "CARTO_CP")
        arcpy.AddMessage("Datos de CARTO_CP convertidos exitosamente.")

        arcpy.AddMessage("Convirtiendo hoja AGROLOGIA de Excel a tabla...")
        table_excel_agro = arcpy.conversion.ExcelToTable(excel, os.path.join(ruta_salida, nombre_gdb, 'Agrologia'), "AGROLOGIA")
        arcpy.AddMessage("Datos de CARTO_CP convertidos exitosamente.")

        arcpy.AddMessage("Convirtiendo hoja AGROLOGIA de Excel a tabla...")
        table_excel_geo = arcpy.conversion.ExcelToTable(excel, os.path.join(ruta_salida, nombre_gdb, 'Geografia'), "GEOGRAFIA")
        arcpy.AddMessage("Datos de CARTO_CP convertidos exitosamente.")

        
        arcpy.AddMessage("Creando feature class de Estado_Cartografia_Rural...")
        arcpy.management.CreateFeatureclass(os.path.join(ruta_salida, nombre_gdb), 'Estado_Cartografia_Rural', geometry_type='POLYGON', template=table_excel_mun, spatial_reference=sr)
        arcpy.AddMessage("Feature class de Estado_Cartografia_Rural creado exitosamente.")


        arcpy.AddMessage("Creando feature class de Estado_Cartografia_Urbana...")
        arcpy.management.CreateFeatureclass(os.path.join(ruta_salida, nombre_gdb), 'Estado_Cartografia_Urbana', geometry_type='POLYGON', template=table_excel_cp, spatial_reference=sr)
        arcpy.AddMessage("Feature class de Estado_Cartografia_Urbana creado exitosamente.")

        arcpy.AddMessage("Creando feature class de Agrologia...")
        arcpy.management.CreateFeatureclass(os.path.join(ruta_salida, nombre_gdb), 'Estado_Agrologia', geometry_type='POLYGON', template=table_excel_agro, spatial_reference=sr)
        arcpy.AddMessage("Feature class de Estado_Cartografia_Urbana creado exitosamente.")

        arcpy.AddMessage("Creando feature class de Geografia...")
        arcpy.management.CreateFeatureclass(os.path.join(ruta_salida, nombre_gdb), 'Estado_Geografia', geometry_type='POLYGON', template=table_excel_geo, spatial_reference=sr)
        arcpy.AddMessage("Feature class de Estado_Cartografia_Urbana creado exitosamente.")

        fields_mun = arcpy.ListFields(table_excel_mun)
        fields_cp = arcpy.ListFields(table_excel_cp)
        fields_agro = arcpy.ListFields(table_excel_agro)
        fields_geo = arcpy.ListFields(table_excel_geo)
        fields_table_mun = [f.name for f in fields_mun if f.name != "OID"]
        fields_table_cp = [f.name for f in fields_cp if f.name != "OID"]
        fields_table_agro = [f.name for f in fields_agro if f.name != "OID"]
        fields_table_geo = [f.name for f in fields_geo if f.name != "OID"]


        arcpy.AddMessage("Insertando datos en Estado_Cartografia_Rural...")
        with arcpy.da.SearchCursor(table_excel_mun, fields_table_mun) as sCur:
            with arcpy.da.InsertCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Cartografia_Rural'), fields_table_mun) as iCur:
                for row in sCur:
                    iCur.insertRow(row)
                    arcpy.AddMessage(f"Insertado: {row}")
        arcpy.AddMessage("Inserción de datos en Estado_Cartografia_Rural completada.")

        arcpy.AddMessage("Insertando datos en Estado_Cartografia_Urbana...")
        with arcpy.da.SearchCursor(table_excel_cp, fields_table_cp) as sCur:
            with arcpy.da.InsertCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Cartografia_Urbana'), fields_table_cp) as iCur:
                for row in sCur:
                    iCur.insertRow(row)
                    arcpy.AddMessage(f"Insertado: {row}")
        arcpy.AddMessage("Inserción de datos en Estado_Cartografia_Urbana completada.")

        arcpy.AddMessage("Revisando registros duplicados en Estado_Cartografia_Rural...")
        divipola_counts = {}
        with arcpy.da.SearchCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Cartografia_Rural'), ['DIVIPOLA']) as cursor:
            for row in cursor:
                divipola = row[0]
                if divipola in divipola_counts:
                    divipola_counts[divipola] += 1
                else:
                    divipola_counts[divipola] = 1
        duplicados = {k for k, v in divipola_counts.items() if v > 1}
        arcpy.AddMessage(f"Encontrados {len(duplicados)} DIVIPOLA duplicados.")

        arcpy.AddMessage("Actualizando geometrías en Estado_Cartografia_Rural...")
        
        with arcpy.da.UpdateCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Cartografia_Rural'), ['SHAPE@', 'DIVIPOLA', 'Ortoimagen_rural']) as uCur:
            for uRow in uCur:
                if uRow[1] in duplicados:
                    encontrado = False
                    with arcpy.da.SearchCursor(mun_dobles, ['SHAPE@', 'MpCodigo', 'ORTO_R']) as sCur:
                        for sRow in sCur:
                            mp_codigo_cr = sRow[1][:5]
                            #arcpy.AddMessage(f"Revisando DIVIPOLA {uRow[1]} con Ortoimagen_rural {uRow[2]}")
                            if sRow[2] == uRow[2] and str(mp_codigo_cr) == str(uRow[1]):
                                row_list = list(uRow)
                                row_list[0] = sRow[0].projectAs(sr)
                                uRow = tuple(row_list)
                                uCur.updateRow(uRow)
                                arcpy.AddMessage(f"Geometría duplicada actualizada: DIVIPOLA {uRow[1]}")
                                encontrado = True
                                break
                    if not encontrado:
                        arcpy.AddMessage(f"No se encontró geometría correspondiente para DIVIPOLA {uRow[1]} con Ortoimagen {uRow[2]}")
                else:
                    with arcpy.da.SearchCursor(mp_rural, ['SHAPE@', 'MpCodigo']) as sCur:
                        for sRow in sCur:
                            if sRow[1] == uRow[1]:
                                row_list = list(uRow)  
                                row_list[0] = sRow[0].projectAs(sr) 
                                uRow = tuple(row_list) 
                                uCur.updateRow(uRow)
                                arcpy.AddMessage(f"Geometría única actualizada: DIVIPOLA {uRow[1]}")
                                break
        arcpy.AddMessage("Actualización de geometrías en Estado_Cartografia_Rural completada.")

        arcpy.AddMessage("Actualizando geometrías en Estado_Cartografia_Urbana...")
        with arcpy.da.SearchCursor(cp, ['SHAPE@', 'COD_CPOB']) as sCur:
            cp_rows = [(sRow[0].projectAs(sr), sRow[1]) for sRow in sCur]
        with arcpy.da.UpdateCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Cartografia_Urbana'), ['SHAPE@', 'DIVIPOLA_CentroPoblado']) as iCur:
            for iRow in iCur:
                for cpShape, cpCode in cp_rows:
                    if cpCode == iRow[1]:
                        iRow[0] = cpShape
                        iCur.updateRow(iRow)
                        arcpy.AddMessage(f"Geometría actualizada: Codigo Centro Poblado {iRow[1]}")
        arcpy.AddMessage("Actualización de geometrías en Estado_Cartografia_Urbana completada.")
# #########################################################################################################################################################
        arcpy.AddMessage("Insertando datos en Estado_Agrologia...")
        with arcpy.da.SearchCursor(table_excel_agro, fields_table_agro) as sCur:
            with arcpy.da.InsertCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Agrologia'), fields_table_agro) as iCur:
                for row in sCur:
                    iCur.insertRow(row)
                    arcpy.AddMessage(f"Insertado: {row}")
        arcpy.AddMessage("Inserción de datos en Estado_Agrologia completada.")

        
        arcpy.AddMessage("Actualizando geometrías en Estado_Agrologia...")
        with arcpy.da.SearchCursor(mun, ['SHAPE@', 'MpCodigo']) as sCur:
            mp_rows = [(sRow[0].projectAs(sr), sRow[1]) for sRow in sCur]
        with arcpy.da.UpdateCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Agrologia'), ['SHAPE@', r'DIVIPOLA']) as iCur:
            for iRow in iCur:
                for mpShape, mpCode in mp_rows:
                    if mpCode == iRow[1]:
                        iRow[0] = mpShape
                        iCur.updateRow(iRow)
                        arcpy.AddMessage(f"Geometría actualizada: Codigo DANE: {iRow[1]}")
        arcpy.AddMessage("Actualización de geometrías en Estado_Agrologia completada.")

#################################################################################################################################################################
        arcpy.AddMessage("Insertando datos en Estado_Geografia...")
        with arcpy.da.SearchCursor(table_excel_geo, fields_table_geo) as sCur:
            with arcpy.da.InsertCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Geografia'), fields_table_geo) as iCur:
                for row in sCur:
                    iCur.insertRow(row)
                    arcpy.AddMessage(f"Insertado: {row}")
        arcpy.AddMessage("Inserción de datos en Estado_Agrologia completada.")

        
        arcpy.AddMessage("Actualizando geometrías en Estado_Geografia...")
        with arcpy.da.SearchCursor(mun, ['SHAPE@', 'MpCodigo']) as sCur:
            mp_rows = [(sRow[0].projectAs(sr), sRow[1]) for sRow in sCur]
        with arcpy.da.UpdateCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Geografia'), ['SHAPE@', r'DIVIPOLA']) as iCur:
            for iRow in iCur:
                for mpShape, mpCode in mp_rows:
                    if mpCode == iRow[1]:
                        iRow[0] = mpShape
                        iCur.updateRow(iRow)
                        arcpy.AddMessage(f"Geometría actualizada: Codigo DANE: {iRow[1]}")
        arcpy.AddMessage("Actualización de geometrías en Estado_Geografia completada.")


#################################################################################################################################################################

        arcpy.AddMessage("Insertando Datos de Parques Naturales")
        try:
            with arcpy.da.SearchCursor(pnn, fields_table_mun) as sCur:
                with arcpy.da.InsertCursor(os.path.join(ruta_salida, nombre_gdb, 'Estado_Cartografia_Rural'), fields_table_mun) as iCur:
                    for row in sCur:
                        # Asegúrate de que el campo 'Departamento' esté presente en 'fields_table_mun' y en la tabla destino.
                        iCur.insertRow(row)
                        arcpy.AddMessage(f"Insertado: {row}")
            arcpy.AddMessage("Inserción de datos de Parques Naturales completada.")
        except arcpy.ExecuteError as e:
            arcpy.AddError(f"Error durante la operación: {e}")
        except Exception as ex:
            arcpy.AddError(f"Error inesperado: {ex}")


    except Exception as e:
        arcpy.AddError(f"Error durante la operación: {str(e)}")
        editor.abortOperation()      
    editor.stopOperation()  
    editor.stopEditing(True)  
    arcpy.AddMessage("Proceso completado exitosamente.")  
    #############################################################
    
def bufferDissolve(gdbOrigen, estacion, gdbMunicipios):
    # Copiar la capa de antenas a la geodatabase de salida
    arcpy.AddMessage("Copiando entidades")
    antenas_copia = arcpy.management.CopyFeatures(estacion, os.path.join(gdbOrigen, 'Geodesia_estaciones'))
    ### Spatial Join para los codigos DANE
    arcpy.management.AddField((antenas_copia), "MpCodigo", "TEXT")
    with arcpy.da.SearchCursor(gdbMunicipios,['SHAPE@','MpCodigo'] ) as sCur:
        for mun in sCur:
            with arcpy.da.UpdateCursor(antenas_copia,['SHAPE@','MpCodigo']) as uCur:
                for antena in uCur:
                    if mun[0].contains(antena[0]) ==True:
                        arcpy.AddMessage("Insertando Codigo DANE {0} a las antenas".format(mun[1]))
                        antena[1] = mun[1]
                    else:
                        pass
                    uCur.updateRow(antena)

    # Obtener el nombre del campo Buff_km
    nombre_campo_buff = None
    campos = arcpy.ListFields(antenas_copia)
    for campo in campos:
        if campo.name == "Buff_km":
            nombre_campo_buff = campo.name
            
        
    if nombre_campo_buff:
    
        # Crear campo temporal para almacenar valores convertidos a kilómetros
        arcpy.AddMessage("Convirtiendo unidades a kilómetros")
        arcpy.management.AddField(antenas_copia, "Buff_km_km", "DOUBLE")
        arcpy.management.CalculateField(antenas_copia, "Buff_km_km", "!{}! * 1000".format(nombre_campo_buff), "PYTHON3")
        
        # Realizar buffer en función del campo Buff_km
        arcpy.AddMessage("Realizando Buffer")
        capa_buff = arcpy.Buffer_analysis(antenas_copia, os.path.join(gdbOrigen, "Geodesia_cubrimiento"), 'Buff_km_km')
        arcpy.AddMessage("Se ha creado una nueva capa con buffers basados en los valores de Buff_km.")
    else:
        arcpy.AddError("No se encontró el campo 'Buff_km' en la capa de antenas.")


    # Usar disolve con el buffer y cortar la capa con los limites de municipios ingresados y
    # calcular %cubrimiento sobre el municipio, tener en cuenta que el buffer puede estar sobre más de 1 municipio.

    # Disolver la capa del buffer

    # Utilizar Pairwise Dissolve en la capa del buffer
    arcpy.AddMessage("Realizando Dissolve")
    buffer_disuelto = arcpy.analysis.PairwiseDissolve(capa_buff, os.path.join(gdbOrigen, "Buffer_Disuelto"))

    # Realizar la intersección entre la capa disuelta del buffer y los límites de los municipios
    arcpy.AddMessage("Realizando Corte por Municipios")
    buffer_cortado = arcpy.analysis.Intersect([buffer_disuelto, gdbMunicipios], os.path.join(gdbOrigen, "Geodesia_cubrimiento_municipio"))

    # Calculando parametros
    arcpy.AddMessage("Calculando Parámetros")

    #Area Munpi
    arcpy.management.AddField(buffer_cortado, "Area_Municipio", "DOUBLE")
    arcpy.management.CalculateField(buffer_cortado, "Area_Municipio", "!MpArea!", "PYTHON3")
    #Area cubrimiento
    arcpy.management.AddField(buffer_cortado, "Area_Cubrimiento", "DOUBLE")
    arcpy.management.CalculateGeometryAttributes(buffer_cortado, [["Area_Cubrimiento", "AREA"]], area_unit="HECTARES")
    # Calculando cubrimiento
    arcpy.AddMessage("Calculando Porcentaje de Cubrimiento")
    #!Shape_Area!/(!MpArea!*10000)
    arcpy.management.AddField(buffer_cortado, "Porcentaje_Cubrimiento", "FLOAT")
    arcpy.management.CalculateField(buffer_cortado, "Porcentaje_Cubrimiento", "(!SHAPE.AREA! / (!MpArea! * 10000))*100", "PYTHON3")

    #Eliminando archivos
    arcpy.management.Delete(buffer_disuelto)




    # arcpy.AddMessage("Iniciando proceso de buffer y disolución...")

    # input_layer = estacion
    # output_buffer_layer = os.path.join(gdbOrigen, "Buffers_Dissolve")
    # municipios_layer = os.path.join(gdbMunicipios, "Munpio")

    # arcpy.AddMessage("Creando buffers...")
    # arcpy.analysis.Buffer(
    #     in_features=input_layer,
    #     out_feature_class=output_buffer_layer,
    #     buffer_distance_or_field="buff_m",
    #     dissolve_option="ALL"
    # )
    # arcpy.AddMessage("Buffers creados correctamente.")

    # arcpy.AddMessage("Agregando campo areaMtr a la capa de municipios...")
    # arcpy.AddField_management(
    #     in_table=municipios_layer,
    #     field_name="areaMtr",
    #     field_type="DOUBLE"
    # )
    # arcpy.AddMessage("Campo areaKM agregado.")

    # arcpy.AddMessage("Calculando área de los municipios en metros cuadrados...")
    # arcpy.management.CalculateField(
    #     in_table=municipios_layer,
    #     field="areaMtr",
    #     expression="!shape.area@squaremeters!",
    #     expression_type="PYTHON3"
    # )
    # arcpy.AddMessage("Cálculo de área completado.")

    # arcpy.AddMessage("Intersectando buffers con municipios...")
    # output_intersect_layer = os.path.join(gdbOrigen, "Buffer_Municipio_Intersect")
    # arcpy.analysis.Intersect(
    #     in_features=[output_buffer_layer, municipios_layer],
    #     out_feature_class=output_intersect_layer,
    #     join_attributes="ALL",
    #     output_type="INPUT"
    # )
    # arcpy.AddMessage("Intersección completada.")

    # arcpy.AddMessage("Disolviendo la intersección por código de municipio...")
    # output_dissolved_layer = os.path.join(gdbOrigen, "Buffer_Estaciones_Geodesicas")
    # arcpy.management.Dissolve(
    #     in_features=output_intersect_layer,
    #     out_feature_class=output_dissolved_layer,
    #     dissolve_field="MpCodigo",
    #     statistics_fields=[("areaMtr", "FIRST"), ("MpNombre", "FIRST"), ("Depto", "FIRST")]
    # )
    # arcpy.AddMessage("Disolución completada.")

    # arcpy.AddMessage("Agregando campo de porcentaje de cobertura...")
    # arcpy.AddField_management(
    #     in_table=output_dissolved_layer,
    #     field_name="CoveragePct",
    #     field_type="DOUBLE"
    # )
    # arcpy.AddMessage("Campo CoveragePct agregado.")

    # arcpy.AddMessage("Calculando porcentaje de cobertura...")
    # arcpy.management.CalculateField(
    #     in_table=output_dissolved_layer,
    #     field="CoveragePct",
    #     expression="(!Shape_Area! / !FIRST_areaMtr!) * 100",
    #     expression_type="PYTHON3"
    # )
    # arcpy.AddMessage("Cálculo de porcentaje de cobertura completado.")

    # arcpy.AddMessage("Eliminando capas temporales...")
    # arcpy.management.Delete(os.path.join(gdbOrigen, "Buffers_Dissolve"))
    # arcpy.management.Delete(os.path.join(gdbOrigen, "Buffer_Municipio_Intersect"))
    # arcpy.AddMessage("Capas temporales eliminadas. Proceso finalizado exitosamente.")
    

if __name__ == "__main__":
    excel = arcpy.GetParameterAsText(0)
    ruta_salida = arcpy.GetParameterAsText(1)
    mun = arcpy.GetParameterAsText(2)
    cp = arcpy.GetParameterAsText(3)
    mun_dobles = arcpy.GetParameterAsText(4)
    estaciones = arcpy.GetParameterAsText(5)
    mp_rural = arcpy.GetParameterAsText(6)
    pnatural = arcpy.GetParameterAsText(7)
    gdb_destino = os.path.join(ruta_salida, "GDB_Info_Integrada_DGIG.gdb")
    join_excel(excel, ruta_salida, mun, cp, mun_dobles,mp_rural,pnatural)
    bufferDissolve(gdb_destino, estaciones, mun)