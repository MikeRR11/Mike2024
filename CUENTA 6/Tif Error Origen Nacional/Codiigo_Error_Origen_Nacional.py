
import arcpy
import numpy as np
import os

# Obtener parámetros de entrada
Ruta_Salida = arcpy.GetParameterAsText(0)
shp = arcpy.GetParameterAsText(1)

arcpy.env.overwriteOutput = True

def w_shape_function(x, x1, x2, x3, x4, x5, y1, y2, y3, y4, y5):
    """Generate values based on a W-shape function across the entire raster."""
    value = np.zeros_like(x, dtype=float)
    mask1 = (x >= x1) & (x < x2)
    mask2 = (x >= x2) & (x < x3)
    mask3 = (x >= x3) & (x < x4)
    mask4 = (x >= x4) & (x <= x5)
    value[mask1] = y1 + (y2 - y1) * (x[mask1] - x1) / (x2 - x1)
    value[mask2] = y2 + (y3 - y2) * (x[mask2] - x2) / (x3 - x2)
    value[mask3] = y3 + (y4 - y3) * (x[mask3] - x3) / (x4 - x3)
    value[mask4] = y4 + (y5 - y4) * (x[mask4] - x4) / (x5 - x4)
    return value

def create_raster_with_w_shape(filename, extent, resolution, w_shape_params):
    """Create a raster with pixel values based on a W-shape function using arcpy."""
    west, south, east, north = extent
    pixel_width, pixel_height = resolution
    width = int((east - west) / pixel_width)
    height = int((north - south) / pixel_height)
    
    arcpy.AddMessage(f"Creando Raster...")

    data = np.zeros((height, width), dtype=float)
    x = np.linspace(west, east, width)
    y = np.linspace(south, north, height)
    X, Y = np.meshgrid(x, y)
    
    data = w_shape_function(X.flatten(), *w_shape_params).reshape((height, width))
    
    temp_raster = os.path.join(arcpy.env.scratchFolder, "temp_raster.tif")
    temp = arcpy.NumPyArrayToRaster(data, lower_left_corner=arcpy.Point(west, south), x_cell_size=pixel_width, y_cell_size=pixel_height)
    temp.save(temp_raster)
 
    # Asigna un sistema de referencia al raster
    sr = arcpy.SpatialReference(4326)  # WGS 1984
    arcpy.DefineProjection_management(temp_raster, sr)
    
    arcpy.CopyRaster_management(temp_raster, filename)
    arcpy.Delete_management(temp_raster)

    arcpy.AddMessage(f"Raster creado...")
    return filename  # Devolver el nombre del archivo guardado

# Parámetros
extent = (-79.2, -4.3, -66.62, 12.5)  # (west, south, east, north)
resolution = (0.001, 0.001)  # Aproximadamente 100 metros por pixel

# Parámetros de la función en W (ajustar según los puntos del mapa)
w_shape_params = (-79.02, -75.3, -73, -70.7, -66.85, 1, 0, -0.159, 0, 1)  # (x1, x2, x3, x4, x5, y1, y2, y3, y4, y5)

# Crear raster
raster_filename = os.path.join(Ruta_Salida, 'w_shape_raster.tif')
create_raster_with_w_shape(raster_filename, extent, resolution, w_shape_params)

# Proyección
sr_colombia = arcpy.SpatialReference(3116)  # EPSG:3116
arcpy.AddMessage("Proyectando Raster...")
Raster_P = arcpy.ProjectRaster_management(raster_filename, os.path.join(Ruta_Salida, "w_shape_raster_projected.tif"), sr_colombia)
arcpy.AddMessage("Raster proyectado y guardado")
arcpy.Delete_management(raster_filename)

# Recorte del Raster
arcpy.AddMessage("Recortando Raster...")
Raster_Col = arcpy.Clip_management(Raster_P, "#", os.path.join(Ruta_Salida, "Raster_Col.tif"), shp, "#", "ClippingGeometry")
arcpy.AddMessage(f"Raster recortado y guardado")
arcpy.Delete_management(Raster_P)


#Resample
cell_size = 90
in_raster = Raster_Col

Raster_F= arcpy.management.Resample(in_raster, os.path.join(Ruta_Salida, "Raster_Final.tif"), cell_size, "BILINEAR")
arcpy.Delete_management(Raster_Col)
arcpy.AddMessage(f"Raster final en: {Raster_F}")
