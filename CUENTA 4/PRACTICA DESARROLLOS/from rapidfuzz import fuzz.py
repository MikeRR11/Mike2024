from rapidfuzz import fuzz

# Definimos las dos listas
lista1 = ['manzana', 'naranja', 'pera', 'uva']
lista2 = ['manzana', 'naranja', 'papaya', 'uva']

# Convertimos las listas a cadenas para poder usar fuzz.ratio
str_lista1 = ', '.join(lista1)
str_lista2 = ', '.join(lista2)

# Calculamos la similitud
similitud = fuzz.ratio(str_lista1, str_lista2)

# Si la similitud es mayor al 80%, imprimimos las listas
if similitud > 80:
    print(f'Lista 1: {lista1}')
    print(f'Lista 2: {lista2}')
