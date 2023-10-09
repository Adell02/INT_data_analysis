import pandas as pd
import os
import xlsxwriter

# En aquest arxiu es prenen les dues primeres fulles del excel i es fa el següent:
# 
# 1. Es pren 'Vehicle' com index
# 2. Es fa un merge dels dos fulls per tenir la informació en una de sol
# 3. S'eliminen les columnes sense dades (es generen soles al fer el merge)
# 4. Movem la columna Id per a que estigui al costat de 'Vehicle'
# 5. Ordenem segons vehicle i id (en aquest ordre)
# 6. Es genera l'arxiu, esborrant l'antic si existeix


ruta_archivo = 'Ray 7.7_modificat.xlsx'

# Lista para almacenar los DataFrames de las 9 hojas
dataframes = []

# Nombres de las hojas en el archivo Excel
nombres_hojas = ["G1", "G2","C2", "C3","IE","B1", "B2","B3","B4"]

# Leer la primera hoja y almacenarla en el DataFrame principal
df_final = pd.read_excel(ruta_archivo, sheet_name=nombres_hojas[0], index_col='VIN', nrows=10000)


# Iterar a través de las demás hojas y realizar merge con el DataFrame principal
for hoja in nombres_hojas[1:]:
    df_hoja = pd.read_excel(ruta_archivo, sheet_name=hoja,index_col='VIN',nrows=10000)
    df_final = pd.merge(df_final, df_hoja, on=['VIN','Id','Timestamp'], how='inner')
    #Al fer el merge, se'ns generen columnes sense dades, les eliminem
    df_final = df_final.dropna(axis=1)

# Ahora df_final contiene los datos combinados de las 9 hojas en un solo DataFrame

#Movem les columnes de Id per major llegibilitat
columna_a_moure = 'Id'
posicio_nova = 1
columna = df_final.pop(columna_a_moure) #s'extrau la columna i la guardem en 'columna'
df_final.insert(posicio_nova, columna_a_moure,columna)

#ordenem segons Vehicle i Id amb aquesta prioritat (Vehicle > ID)
df_final = df_final.sort_values(by=['VIN','Timestamp'])


#generem l'arxiu
if os.path.exists('Ray 7.7_modificat_merge.xlsx'):
    os.remove('Ray 7.7_modificat_merge.xlsx')

df_final.to_excel('Ray 7.7_modificat_merge.xlsx', sheet_name='CT')




'''
# Archivo Excel de origen
archivo_excel = 'Ray 7.7_modificat_merge.xlsx'
hoja_origen = 'CT'  # Cambia esto al nombre de tu hoja de origen

# Número máximo de filas por hoja
maximo_filas_por_hoja = 15000

# Cargar la hoja de Excel completa
df = pd.read_excel(archivo_excel, sheet_name=hoja_origen)

# Dividir el DataFrame en hojas más pequeñas y guardarlas en un nuevo archivo Excel
nuevo_archivo_excel = 'Ray 7.7_modificat_merge.xlsx'  # Cambia esto al nombre que desees para el nuevo archivo

with pd.ExcelWriter(nuevo_archivo_excel, engine='xlsxwriter') as writer:
    num_hojas = (len(df) - 1) // maximo_filas_por_hoja + 1
    for i in range(num_hojas):
        inicio = i * maximo_filas_por_hoja
        fin = (i + 1) * maximo_filas_por_hoja
        df_hoja = df.iloc[inicio:fin]
        nombre_hoja = f'CT{i + 1}'  # Cambia el nombre de las hojas según tus preferencias
        df_hoja.to_excel(writer, sheet_name=nombre_hoja, index=False)
'''
