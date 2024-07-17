import arcpy
import os

# Define las rutas de las capas fijas como listas
rutas_capas_fijas = [
    r'\LimitesEntidadesTerritoriales\Municipio__Distrito_y_Área_no_municipalizada',
    r'\CapasNacionales\Aerodromos24',
    r'\CapasNacionales\EEducativosDANE',
    r'\PoliticoAdministrativa\MGN_CabecerasCP',
    r'\PoliticoAdministrativa\MGN_CabecerasCP',
    r'\PoliticoAdministrativa\DivisionVeredal',
    r'\LimitesEntidadesTerritoriales\LLimitII',
    r'\CapasNacionales\RUNAP060624',
    r'\CapasNacionales\Paramos',
    r'\CapasNacionales\ResguardoIndigenaFormalizado',
    r'\CapasNacionales\ZonificacionLey2Sept2023',
    r'\CapasNacionales\ZonasReservaCampesina',
    r'\CapasNacionales\Bathymetry'
]

# Variables predefinidas
nuevo_origen_datos = r"C:\Users\michael.rojas\Documents\c5\PLANTILLAS CARTA\DATOS\GDB MUNICIPIOS\20045_Becerrill.gdb"

ruta_salida = r"C:\Users\michael.rojas\Documents\c5\PLANTILLAS CARTA\DATOS\GDB MUNICIPIOS\MapSeriesExport.pdf"

# Verifica que la GDB variable proporcionada por el usuario exista
if not os.path.exists(nuevo_origen_datos):
    raise FileNotFoundError(f"La GDB variable proporcionada no existe en la ruta: {nuevo_origen_datos}")

# Define la ruta de salida para el archivo PDF
if not ruta_salida.lower().endswith('.pdf'):
    ruta_salida = ruta_salida + '.pdf'

# Verifica que la carpeta de salida para el PDF exista
if not os.path.isdir(os.path.dirname(ruta_salida)):
    raise FileNotFoundError(f"La carpeta de salida para el PDF no existe: {os.path.dirname(ruta_salida)}")

# Obtiene el proyecto de ArcGIS Pro actualmente abierto
aprx = arcpy.mp.ArcGISProject('CURRENT')

# Obtiene el primer layout con el nombre "Layout"
layout = aprx.listLayouts("CARTO_PLIEGO_MUNICIPIOS")[0]

# Obtiene el primer mapa con el nombre "Vector"
aprxMap = aprx.listMaps("Vector")[0]

# Obtiene todas las capas del mapa
layers = aprxMap.listLayers()

# Obtiene el primer elemento de marco de mapa llamado "Map Frame Vector" en el layout
mf = layout.listElements('MAPFRAME_ELEMENT', 'Map Frame')[0]

# Obtiene la serie de mapas del layout
mapSeries = layout.mapSeries

# Separa las capas en fijas y variables basándose en las rutas relativas de las capas fijas
capas_fijas = []
capas_variables = []

for layer in layers:
    if layer.isFeatureLayer:
        if any(layer.dataSource.endswith(ruta) for ruta in rutas_capas_fijas):
            capas_fijas.append(layer)  # Capa fija, no se actualiza
        else:
            capas_variables.append(layer)  # Capa variable, se actualizará

# Verifica si la serie de mapas está habilitada
if mapSeries.enabled:
    # Establece la página actual a la primera página de la serie de mapas
    mapSeries.currentPageNumber = 93

    # Verifica que haya al menos una capa variable
    if not capas_variables:
        print("No se encontraron capas variables para actualizar.")
    else:
        # Actualiza las propiedades de conexión para las capas variables
        for layer in capas_variables:
            # Obtiene la ruta original del origen de datos
            origen_datos_original = str(layer.dataSource)
            # Extrae la parte de la ruta antes del archivo GDB
            gdb_original = origen_datos_original.split('.gdb')[0] + '.gdb'
            # Actualiza el origen de datos
            print(f"Actualizando origen de datos para la capa variable: {layer.name} - {origen_datos_original} -> {nuevo_origen_datos}")
            aprx.updateConnectionProperties(gdb_original, nuevo_origen_datos)

    # Exporta la primera página de la serie de mapas al formato PDF con una resolución de 300 DPI
    layout.exportToPDF(ruta_salida, resolution=300)
    print(f"Exportado: {ruta_salida}")
else:
    print('La serie de mapas no está habilitada.')
