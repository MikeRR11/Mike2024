#Dirección de Gestión de Información Geográfica 
#Grupo de desarrollo IGAC
#Elaboró / Modifico: Michael Andres Rojas

import arcpy

# Obtiene el proyecto de ArcGIS Pro actualmente abierto
aprx = arcpy.mp.ArcGISProject('CURRENT')

# Obtiene el primer layout con el nombre "Layout"
layout = aprx.listLayouts("Layout")[0]

# Obtiene el primer mapa con el nombre "Vector"
aprxMap = aprx.listMaps("Vector")[0]

# Obtiene todas las capas del mapa
layers = aprxMap.listLayers()

# Obtiene el primer elemento de marco de mapa llamado "Map Frame Vector" en el layout
mf = layout.listElements('MAPFRAME_ELEMENT', 'Map Frame Vector')[0]

# Obtiene la serie de mapas del layout
mapSeries = layout.mapSeries

# Define los nombres de las capas que se consideran fijas
nombres_capas_fijas = ['FixedLayer1', 'FixedLayer2']  # Modifica con los nombres de las capas fijas en tu proyecto

# Separa las capas en fijas y variables
capas_fijas = []
capas_variables = []

for layer in layers:
    if layer.name in nombres_capas_fijas:
        capas_fijas.append(layer)
    else:
        capas_variables.append(layer)

# Verifica si la serie de mapas está habilitada
if mapSeries.enabled:
    # Establece la página actual a la primera página de la serie de mapas
    mapSeries.currentPageNumber = 1

    # Solicita al usuario que ingrese el nuevo origen de datos para la GDB variable
    nuevo_origen_datos = input("Ingrese el nuevo origen de datos para la GDB variable (ruta completa del archivo GDB): ")

    # Solicita al usuario que ingrese la ruta de salida para el archivo PDF
    ruta_salida = input("Ingrese la ruta de salida para el archivo PDF (incluya el nombre del archivo y la extensión .pdf): ")
    
    # Define la ruta de salida para el archivo PDF
    if not ruta_salida.lower().endswith('.pdf'):
        ruta_salida = ruta_salida + '.pdf'

    # Verifica que haya al menos una capa variable
    if not capas_variables:
        print("No se encontraron capas variables para actualizar.")
    else:
        # Actualiza las propiedades de conexión para las capas variables
        for layer in capas_variables:
            if layer.isFeatureLayer:
                print(f"Actualizando origen de datos para la capa variable: {layer.name} - {layer.dataSource} -> {nuevo_origen_datos}")
                aprx.updateConnectionProperties(str(layer.dataSource).split('.gdb')[0] + '.gdb', nuevo_origen_datos)

    # Exporta la primera página de la serie de mapas al formato PDF con una resolución de 300 DPI
    layout.exportToPDF(ruta_salida, resolution=300)
    print(f"Exportado: {ruta_salida}")
else:
    print('La serie de mapas no está habilitada.')
