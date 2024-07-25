import arcpy
import numpy as np
from arcpy import env
 
import arcpy
import numpy as np
from arcpy import env
 
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
    
    data = np.zeros((height, width), dtype=float)
    x = np.linspace(west, east, width)
    y = np.linspace(south, north, height)
    X, Y = np.meshgrid(x, y)
    
    data = w_shape_function(X.flatten(), *w_shape_params).reshape((height, width))
    
    temp_raster = r"C:\Users\michael.rojas\Documents\c5\ORIGEN_NACIONAL\raster.tif"
    temp = arcpy.NumPyArrayToRaster(data, lower_left_corner=arcpy.Point(west, south), x_cell_size=pixel_width, y_cell_size=pixel_height)
    temp.save(temp_raster)
 
    arcpy.CopyRaster_management(temp_raster, filename)
    arcpy.Delete_management(temp_raster)
 
# Ejemplo de uso
env.workspace = r"C:\Users\michael.rojas\Documents\c5\ORIGEN_NACIONAL"
extent = (0, 0, 13, 17)  # (west, south, east, north)
resolution = (0.01, 0.01)  # (pixel width, pixel height)
w_shape_params = (0, 3.25, 6.5, 9.75, 13, 20, 0, 15, 0, 20)  # x1, x2, x3, x4, x5, y1, y2, y3, y4, y5
 
create_raster_with_w_shape('w_shape_raster.tif', extent, resolution, w_shape_params)




____________________________



import arcpy
import numpy as np
from arcpy import env
 
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
    
    data = np.zeros((height, width), dtype=float)
    x = np.linspace(west, east, width)
    y = np.linspace(south, north, height)
    X, Y = np.meshgrid(x, y)
    
    data = w_shape_function(X.flatten(), *w_shape_params).reshape((height, width))
    
    temp_raster = r"C:\Users\michael.rojas\Documents\c5\ORIGEN_NACIONAL\raster.tif"
    temp = arcpy.NumPyArrayToRaster(data, lower_left_corner=arcpy.Point(west, south), x_cell_size=pixel_width, y_cell_size=pixel_height)
    temp.save(temp_raster)
 
    arcpy.CopyRaster_management(temp_raster, filename)
    arcpy.Delete_management(temp_raster)
 
# Ejemplo de uso
env.workspace = r"C:\Users\michael.rojas\Documents\c5\ORIGEN_NACIONAL"
extent = (0, 0, 12.6, 17.1)  # (west, south, east, north)
resolution = (0.01, 0.01)  # (pixel width, pixel height)
w_shape_params = (0, 3.25, 6.5, 9.75, 13, 20, 0, 15, 0, 20)  # x1, x2, x3, x4, x5, y1, y2, y3, y4, y5
 
create_raster_with_w_shape('w_shape_raster.tif', extent, resolution, w_shape_params)
