import pandas as pd

ruta_archivo = 'Base de datos RAY - UPC.xlsx'
nombre_hoja='Hoja2'
df = pd.read_excel(ruta_archivo,sheet_name=nombre_hoja, index_col='Vehicle')
df_ordenado=df.sort_values(by='Timestamp',ascending=True)

print(df_ordenado['Timestamp'])

df_ordenado.to_excel('commit0.xlsx', index=False)