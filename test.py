import pandas as pd
import os

# En aquest arxiu es prenen les dues primeres fulles del excel i es fa el següent:
# 
# 1. Es pren 'Vehicle' com index
# 2. Es fa un merge dels dos fulls per tenir la informació en una de sol
# 3. S'eliminen les columnes sense dades (es generen soles al fer el merge)
# 4. Movem la columna Id per a que estigui al costat de 'Vehicle'
# 5. Ordenem segons vehicle i id (en aquest ordre)
# 6. Es genera l'arxiu, esborrant l'antic si existeix


ruta_archivo = 'Base de datos RAY - UPC.xlsx'
hoja2_df = pd.read_excel(ruta_archivo, sheet_name='Hoja2',index_col='Vehicle')
hoja3_df = pd.read_excel(ruta_archivo, sheet_name='Hoja3', index_col='Vehicle')

#volem combinar varis fulls de l'excel en un, per això, ho farem seguint el número de vehicle, ID i timestamp
#com a columnes clau
hojas23_df = pd.merge(hoja2_df,hoja3_df,on=['Vehicle','Id','Timestamp'], how='inner')

#Al fer el merge, se'ns generen columnes sense dades, les eliminem
hojas23_df = hojas23_df.dropna(axis=1)


#Movem les columnes de Id per major llegibilitat
columna_a_moure = 'Id'
posicio_nova = 0
columna = hojas23_df.pop(columna_a_moure) #s'extrau la columna i la guardem en 'columna'
hojas23_df.insert(posicio_nova, columna_a_moure,columna)

#ordenem segons Vehicle i Id amb aquesta prioritat (Vehicle > ID)
hojas23_df = hojas23_df.sort_values(by=['Vehicle','Id'])


#generem l'arxiu
if os.path.exists('merge1_2.xlsx'):
    os.remove('merge1_2.xlsx')

hojas23_df.to_excel('merge1_2.xlsx', sheet_name='Hoja1')