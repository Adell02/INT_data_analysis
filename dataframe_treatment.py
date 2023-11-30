import pandas as pd
import os
import json
import pyarrow as pa
import pyarrow.parquet as pq

"""
*************************************************************************************************************
This file contains all functions necessary to assure that the data stored in a dataframe is correct,
contains all information and it is normalised so that future analyses can be done

The main function is df_filter_data, which will return a filtered and depurated dataframe, the rest of
functions are auxiliary and do not need to be particularily used for external purposes.

df_get_colum_tags_dictionary returns a vector containing all the names of the columns given the type_name
('trip' or 'charge). It is useful if it is needed to list all the variables conained in the dataframe.
*************************************************************************************************************
"""

def df_get_column_tags_dictionary(type_name:str):
    # This function returns a vector with all column tags in the parameters dictionary
    # 
    # INPUTS:
    #   - type_name: either 'trip' or 'charge', otherwise not supported
    # 
    # OUTPUT:
    #   - column_tags
    #   - -1 if type_name not supported
 
    # Open the json containing all parameters
    with open('param_battery.json', 'r') as file:
        parameters = json.load(file)

    # Check type_name
    if type_name != 'trip' and type_name != 'charge':
        return -1

    # Get column tags
    column_tags = [key for key, value in parameters.items() if value.get("Type Chart Variables") == type_name]

    return column_tags

def update_column_tags(df:pd.DataFrame,type_name:str) -> int:
    # This function updates the names of the dataframe to match the ones in the data dictionary
    # It is useful if the source of the dataframe is an excel file with diffrent name tags, but
    # it is not used when receiving data from the server.
    # INPUTS:
    #   - df 
    #   - type_name: 'trip' or 'charge'
    # 
    # OUTUPT:
    #   - df
    #   - -1 if type_name not supported

    column_tags = df_get_column_tags_dictionary(type_name)

    if column_tags == -1:
        return -1

    df.columns = column_tags

    return df

def add_columns(df:pd.DataFrame,type_name:str):
    # This function reads and stores new data from a parquet file
    # as main source
    # 
    # INPUTS:
    #   - file_path
    #   - type_name: either 'trip' or 'charge'
    # 
    # OUTPUT:
    #   - 0 if successful
    #   - -1 if path not found or type_name not correct
    # 
    #_NOTE THAT THE COLUMNS MUST HAVE BEEN RENAMED BEFORE THE EXECUTION OF THIS FUNCTION

    
    if type_name == 'trip':
        df['Mins'] = (df['End'] - df['Start'])/60
        df['Total distance'] = (df['City distance'] + df['Sport distance'] + df['Flow distance'])/10
        df['Total energy'] = df['City energy'] + df['Sport energy'] + df['Flow energy']
        df['Total regen'] = df['City regen'] + df['Sport regen']
        df['Regen'] = 100 * df['Total regen'] / df['Total energy']
        df['SoC delta'] = (df['Start SoC'] - df['End SoC'])/100
        df['Temp general delta'] = (df['Max temp CT'] - df['Max delta'])/10
        
    elif type_name == 'charge':
        df['Delta V I'] = (df['Vmax I'] - df['Vmin I'])*0.001

    else:
        return -1

    return df

def sort_columns(df:pd.DataFrame,type_name:str):
    # This function sorts the column following the param_battery.json file
    # _NOTE THAT THE COLUMNS MUST HAVE BEEN RENAMED AND SECONDARY COLUMNS MUST HAVE
    # BEEN ADDED BEFORE THE EXECUTION OF THIS FUNCTION

    # Get the column tags ordered (since they are contained in the dictionary)
    column_ordered = df_get_column_tags_dictionary(type_name)

    if column_ordered == -1:
        return -1

    df = df[column_ordered]

    return df

def verify_values(df:pd.DataFrame):
    # This function values whether the columns in the df store possible values,
    # if not, the row is eliminated from the dataframe
    # 
    # INPUTS:
    #   - df
    # 
    # OUTPUTS:
    #   - df filtered
    #   - -1 if df is empty (which means that either the df is corrupted or the dictionary
    #     is not updated)

    with open('param_battery.json', 'r') as json_file:
        parameters = json.load(json_file)

    # Check for each column the maximum and minimum value allowed and empty the rows that do
    # not meet the condition
    for column in df:
        value_max = parameters[column]["Value_MAX"]
        value_min = parameters[column]["Value_MIN"]

        condicion = (df[column] >= value_min) & (df[column] <= value_max)
        df = df.loc[condicion]
    
    return df

def apply_resolution(df:pd.DataFrame):
    # Function in charge of reescalating all columns depending on their resolution 
    # 
    # INPUTS:
    #   - df (raw)
    # 
    # OUTPUT:
    #   - df (reescalated)
    #
    # _NOTE THAT THE DATAFRAME MUST HAVE BEEN RENAMED AND NEW COLUMNS ADDED TO WORK
    # PROPERLY


    # Open the json containing all parameters
    with open('param_battery.json', 'r') as file:
        parameters = json.load(file)

    # Multiply each column by its resolution
    for column in df:
        df[column] *= parameters[column]["Resolution"]

    return df

def df_filter_data(df:pd.DataFrame, type_name:str, from_excel:bool=False):
    # This function has to be used before appending a dataframe to a definitive .parquet
    # file
    # 
    # This function will (respectively)
    #   1)  Update the column names (in case the dataframe comes from an xlsx file with
    #       different column_tags)
    #   2)  Add secondary columns, which are product of primary columns
    #   3)  Sort columns, so that the order is the same as in the param_battery.json file
    #   4)  Verify values, in case there are any data out of acceptable bounds
    #   5)  Apply the resolution of each column
    # 
    # Every step is checked, in case there is any error, the function will return a -"number"
    # where "number" is the step (stated before) that has given the error
    # 
    # INPUTS:
    #   - df
    # 
    # OUTPUT:
    #   - df filtered
    #   - Negative number stating the step that has given the error

    # Step 1
    if from_excel:
        df = update_column_tags(df,type_name)
        if  not isinstance(df,pd.DataFrame):
            return -1
    else:
        del df['Start odometer']

    # Step 2
    df = add_columns(df,type_name)
    if not isinstance(df,pd.DataFrame):
        return -2
    
    # Step 3
    df = sort_columns(df,type_name)
    if not isinstance(df,pd.DataFrame):        
        return -3
    
    # Step 4
    df = verify_values(df)
    if df.empty:
        return -4
    
    # Step 5 (it does not return any error if previous steps are ok)
    df == apply_resolution(df)
    
    return df
