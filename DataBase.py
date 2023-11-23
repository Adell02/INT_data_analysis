import pandas as pd
import os
import xlsxwriter
import openpyxl
from functions import *



ruta_archivo = 'Ray 7.7_modificat.xlsx'

# Lista para almacenar los DataFrames de las 9 hojas
dataframes = []

# Nombres de las hojas en el archivo Excel
nombres_hojas_traj = ["G1", "G2","C2","C3","IE","B1","B2","B3","B4"]
nombres_hojas_carga = ["H2", "H3","H4","H5","H8"]


# Leer la primera hoja y almacenarla en el DataFrame principal
df_final_t = pd.read_excel(ruta_archivo, sheet_name=nombres_hojas_traj[0], index_col='VIN', nrows=None)


# CARTES DE TRAJECTE
for hoja in nombres_hojas_traj[1:]:
    df_hoja_t = pd.read_excel(ruta_archivo, sheet_name=hoja,index_col='VIN',nrows=None)
    df_hoja_t.drop_duplicates(subset=['Id','Timestamp'], inplace=True)
    df_final_t.drop_duplicates(subset=['Id','Timestamp'], inplace=True)
    df_final_t = pd.merge(df_final_t, df_hoja_t, on=['VIN','Id','Timestamp'], how='inner')
    

    #Al fer el merge, se'ns generen columnes sense dades, les eliminem
    df_final_t = df_final_t.dropna(axis=1)

#CARTES DE CARREGA
df_final_c = pd.read_excel(ruta_archivo, sheet_name=nombres_hojas_carga[0], index_col='VIN', nrows=None)

for hoja in nombres_hojas_carga[1:]:
    df_hoja_c = pd.read_excel(ruta_archivo, sheet_name=hoja,index_col='VIN',nrows=None)
    df_hoja_c.drop_duplicates(subset=['Timestamp'], inplace=True)
    df_final_c.drop_duplicates(subset=['Timestamp'], inplace=True)
    df_final_c = pd.merge(df_final_c, df_hoja_c, on=['VIN','Timestamp'], how='inner')
    

    #Al fer el merge, se'ns generen columnes sense dades, les eliminem
    df_final_c = df_final_c.dropna(axis=1)

# Ahora df_final contiene los datos combinados de las 9 hojas en un solo DataFrame

#Movem les columnes de Id per major llegibilitat
columna_a_moure = 'Id'
posicio_nova = 1
columna = df_final_t.pop(columna_a_moure) #s'extrau la columna i la guardem en 'columna'
df_final_t.insert(posicio_nova, columna_a_moure,columna)

#ordenem segons Vehicle i Id amb aquesta prioritat (Vehicle > ID)
df_final_t = df_final_t.sort_values(by=['VIN','Timestamp'])
df_final_t=df_final_t.round(3)
df_final_c = df_final_c.sort_values(by=['VIN','Timestamp'])
df_final_c=df_final_c.round(3)


#generem l'arxiu
if os.path.exists('Ray_Data_Base.xlsx'):
    os.remove('Ray_Data_Base.xlsx')

with pd.ExcelWriter('Ray_Data_Base.xlsx', engine='openpyxl') as writer:
    #writer.book = openpyxl.Workbook()
    df_final_t.to_excel(writer, sheet_name='CT', index=True)
    df_final_c.to_excel(writer, sheet_name='CC', index=True)
 
df_append_data(df_final_t, 'trip')
df_append_data(df_final_c, 'charge')


