import pandas as pd
from dataframe_storage import df_append_data
from dataframe_treatment import df_filter_data


#Protocol Dictionary
protocol_dict={"G1":["Timestamp CT", "Start", "End", "Start odometer", "Id"],
                   "G2":["Timestamp CT", "End odometer", "Max speed", "Id"],
                   "C2":["Timestamp CT", "City distance", "Sport distance","Flow distance","Sail distance","Regen distance","Id"],
                   "C3":["Timestamp CT", "City energy", "Sport energy","Flow energy","City regen","Sport regen","Map changes","Id"],
                   "IE":["Timestamp CT", "Inv max T", "Inv avg T", "Inv min T","Motor max T","Motor avg T","Motor min T","Id"],
                   "B1":["Timestamp CT", "Start SoC", "End SoC","Max discharge","Max regen","Id"],
                   "B2":["Timestamp CT", "Avg current", "Thermal current","Max V","Id"],
                   "B3":["Timestamp CT", "Average V", "Min V","Max cell V","Min cell V","Id"],
                   "B4":["Timestamp CT", "Cell V diff", "Max temp CT","Avg temp","Min temp CT","Max delta","Avg delta","Id"],
                   "H2":["Timestamp CC", "SoC i", "SoC f","Vmin I","Vavg I","Vmax I","Vmin F"],
                   "H3":["Timestamp CC", "Avg final V", "Max final V","Max BMS current","Max charger current"], 
                   "H4":["Timestamp CC", "Charger max P", "Min temp I","Avg temp I","Max temp I","Min temp F"],
                   "H5":["Timestamp CC", "Avg temp F","Max temp F","Min temp CC","Max temp CC","Cycles","Age"],
                   "H8":["Timestamp CC", "uSoC I", "uSoC F","Connector"]}

df_dict_trip = {}
df_dict_charge = {}

VIN_COLUMN = 'DeviceId'
DATA_COLUMN = 'OriginalMessage'

def df_create(string:str, param_order)->pd.DataFrame:
    # Split the string into its components
    components = string.split(':')
    payload = components[1]

    # Check if the "End of Message Character" is present and remove it
    if payload.endswith(",#&"):
        payload = payload[:-3]
    # Eliminar espacios en blanco adicionales al final del payload
    payload = payload.strip()

    # Split the payload into its parts
    payload_parts = payload.split(',')
    param_values = []

    # Convert the values to integers or leave as None if they can't be converted
    for part in payload_parts:
        if part.isdigit() or (part[0] == '-' and part[1:].isdigit()):
            param_values.append(int(part))
        else:
            param_values.append(None)

    # Create a dictionary to store the parameter values
    param_dict = {param: [value] for param, value in zip(param_order, param_values)}

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(param_dict)

    return df

def df_from_string_to_df(vin:str,string:str)-> (pd.DataFrame,str):

    components = string.split(':')
    message_type = components[0][1:]
    type_name=check_type(message_type)

    if message_type == 'G1':
        param_order = protocol_dict["G1"]
        df_str=df_create(string, param_order)
    elif message_type == 'G2':
        param_order = protocol_dict["G2"]
        df_str=df_create(string, param_order)
    elif message_type == 'C2':
        param_order = protocol_dict["C2"]
        df_str=df_create(string, param_order)
    elif message_type == 'C3':
        param_order = protocol_dict["C3"]
        df_str=df_create(string, param_order)
    elif message_type == 'IE':
        param_order = protocol_dict["IE"]
        df_str=df_create(string, param_order)
    elif message_type == 'B1':
        param_order = protocol_dict["B1"]
        df_str=df_create(string, param_order)
    elif message_type == 'B2':
        param_order = protocol_dict["B2"]
        df_str=df_create(string, param_order)
    elif message_type == 'B3':
        param_order = protocol_dict["B3"]
        df_str=df_create(string, param_order)
    elif message_type == 'B4':
        param_order = protocol_dict["B4"]
        df_str=df_create(string, param_order)
    elif message_type == 'H2':
        param_order = protocol_dict["H2"]
        df_str=df_create(string, param_order)
    elif message_type == 'H3':
        param_order = protocol_dict["H3"]
        df_str=df_create(string, param_order)
    elif message_type == 'H4':
        param_order = protocol_dict["H4"]
        df_str=df_create(string, param_order)
    elif message_type == 'H5':
        param_order = protocol_dict["H5"]
        df_str=df_create(string, param_order)
    elif message_type == 'H8':
        param_order = protocol_dict["H8"]
        df_str=df_create(string, param_order)
    
    return (df_str, type_name)

def check_type(string:str)-> str:
    
    trip =['G1','G2','C2','C3','IE','B1','B2','B3','B4']
    charge=['H2','H3','H4','H5','H8']
    if string in trip:
        return 'trip'
    elif string in charge:
        return 'charge'

    return -1

def create_df_dict(VIN:str,dataframes:pd.DataFrame, type_name:str)->pd.DataFrame:

    all_columns_trip = ['Timestamp CT','Id','Start','End','Start odometer','End odometer','Max speed','City distance','Sport distance','Flow distance','Sail distance','Regen distance','City energy', 
                   'Sport energy','Flow energy','City regen','Sport regen','Map changes','Inv max T', 'Inv avg T', 'Inv min T','Motor max T','Motor avg T','Motor min T',
                   'Start SoC', 'End SoC','Max discharge','Max regen','Avg current', 'Thermal current','Max V','Average V', 'Min V','Max cell V','Min cell V',
                   'Cell V diff', 'Max temp CT','Avg temp','Min temp CT','Max delta','Avg delta']

    all_columns_charge = ['Timestamp CC', 'SoC i', 'SoC f','Vmin I','Vavg I','Vmax I','Vmin F','Avg final V', 'Max final V','Max BMS current','Max charger current',
                        'Charger max P', 'Min temp I','Avg temp I','Max temp I','Min temp F', 'Avg temp F','Max temp F','Min temp CC','Max temp CC','Cycles','Age','uSoC I',
                        'uSoC F','Connector']

    if type_name == 'trip':

        for df in dataframes:
            timestamp_column_name = 'Timestamp CT'
            id_column_name = 'Id'
            
            timestamp = df[timestamp_column_name].iloc[0]
            identifier = df[id_column_name].iloc[0]

            if (timestamp, identifier) in df_dict_trip:
                # Actualizar los valores existentes en el DataFrame correspondiente
                existing_df = df_dict_trip[(timestamp, identifier)]
                for col in df.columns:
                    if col not in [timestamp_column_name, id_column_name]:
                        existing_df.loc[0, col] = df[col].iloc[0]
                
                # Verificar si todas las columnas están completas
                if all(existing_df.notnull().all()):
                    # Retornar el DataFrame y eliminarlo del diccionario
                    del df_dict_trip[(timestamp, identifier)]
                    existing_df['VIN']=VIN
                    existing_df.set_index('VIN',inplace=True)
                    return existing_df
            else:
                # Si no existe, crear una nueva entrada con el DataFrame vacío y luego asignar los datos
                df_dict_trip[(timestamp, identifier)] = pd.DataFrame(columns=all_columns_trip)
                
                # Asignar valores a las columnas de timestamp y JI
                df_dict_trip[(timestamp, identifier)].at[0, timestamp_column_name] = timestamp
                df_dict_trip[(timestamp, identifier)].at[0, id_column_name] = identifier
                
                # Asignar valores a las otras columnas
                for col in df.columns:
                    if col not in [timestamp_column_name, id_column_name]:
                        df_dict_trip[(timestamp, identifier)].loc[0, col] = df[col].iloc[0]
        return df_dict_trip

    elif type_name == 'charge':
        for df in dataframes:
            timestamp_column_name = 'Timestamp CC'
            
            timestamp = df[timestamp_column_name].iloc[0]

            if timestamp in df_dict_charge:
                # Actualizar los valores existentes en el DataFrame correspondiente
                existing_df = df_dict_charge[timestamp]
                for col in df.columns:
                    if col != timestamp_column_name:
                        existing_df.loc[0, col] = df[col].iloc[0]
                
                # Verificar si todas las columnas están completas
                if all(existing_df.notnull().all()):
                    # Retornar el DataFrame y eliminarlo del diccionario
                    del df_dict_charge[timestamp]
                    return existing_df
            else:
                # Si no existe, crear una nueva entrada con el DataFrame vacío y luego asignar los datos
                df_dict_charge[timestamp] = pd.DataFrame(columns=all_columns_charge)
                
                # Asignar valores a las columnas de timestamp y JI
                df_dict_charge[timestamp].at[0, timestamp_column_name] = timestamp
                
                # Asignar valores a las otras columnas
                for col in df.columns:
                    if col != timestamp_column_name:
                        df_dict_charge[timestamp].loc[0, col] = df[col].iloc[0]

        return df_dict_charge


    return -1


def from_server_to_parquet(df_server:pd.DataFrame):
# This function will append to the existing parquet, given a dataframe fetched from Ray's
# server. This function will also filter and append the given data.
# 
# INPUT
# - df_server: containing two columns: DeviceId, and OriginalMessage, containing one packet info
# 
# OUTPUT
# - df_appended if any row has been completed, otherwise returns None

    df_server = df_server.sort_values(by=VIN_COLUMN, ascending=True)

    for unused,row in df_server.iterrows():
        df_packet,type_name=df_from_string_to_df(row[DATA_COLUMN])
        df_created = create_df_dict(row[VIN_COLUMN],[df_packet],type_name)
        
        # The returned value can be a dataframe if it has been completed or a dictionary
        # if else.
        if isinstance(df_created,pd.DataFrame):
            df_filtered=df_filter_data(df_created,type_name)
            df_appended=df_append_data(df_filtered,type_name)

            return df_appended
    
    return