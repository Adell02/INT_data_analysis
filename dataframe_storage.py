import pandas as pd
import numpy as np
import os
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timedelta
import datetime



"""
*************************************************************************************************************
This file contains all functions related to adding new information to already existing data stored or adding 
new sets of data.

Its main funtion is append_data which, given a new dataframe and which type it is ('trip' or 'charge'), 
will do as follows:
    
    1) Check if there are different months within the dataframe
    2) Check if there is already an existing file containing data from that month
    3) Generate or append df_new to its corresponding .parquet file
    4) Update month's critical data or generate a new entry if not existing

Another main function is dF_get_last_months_critical_data, this function is quite self-explainatory. It will
return a dataframe containing the last "n" months that are passed as parameter.

The rest of functions are used internally and don't necessarily have to be used by the client.

If the user desires to change the critical columns, he/she has to access df_add_month_to_critical_data, where
all critical data columns are generated
*************************************************************************************************************
"""
# Critical data path
CRITICAL_DATA_FILE_PATH = 'df/critical_data.parquet'



def find_max_distance(df):
    
    # Find the index and maximum travelled distance within a month
    # 
    # INPUTS:
    # - df
    # 
    # OUTPUT:
    # - distance_index = [max_distance, max_distance_index]
    
    DISTANCE_COLUMN = 'Total distance'

    # Group by index and accumulate all distances
    total_distances_by_index = df.groupby(df.index)[DISTANCE_COLUMN].sum()

    # Find the index which has the maximum distance travelled
    max_distance_index = total_distances_by_index.idxmax()

    # Find the totale maximum distance
    max_distance = total_distances_by_index.max()
    
    # Generate the output tuple including both data
    distance_index = [max_distance,max_distance_index]

    return distance_index

def df_generate_month_df(file_path_trip:str,file_path_charge:str,year:int,month:int,key_user='') -> pd.DataFrame:
    # Given a month and year, generates a dataframe containing all "data_to_save" information
    # which will be further (in another function) appended to the parquet file that contains
    # all months.
    # 
    # From the month and year, it will search the corresponding document in the folder df
    # 
    # IMPORTANT: The file path has to store already filtered data, otherwise errors might occur.
    # 
    # INPUT  
    #   - file_path:        .parquet from which to read the last month's data
    #   - type_name:        indicates if the file is 
    #   - month, year:      integers to indicate the month and year of the dataframe
    # 
    # OUTPUT
    #   - -1 if no file matches the date
    #   - df_month

    if not (os.path.exists(file_path_trip) and os.path.exists(file_path_charge)):
        return -1
    
    df_trip = pd.read_parquet(file_path_trip)
    df_charge = pd.read_parquet(file_path_charge)

    # Check if key_user is a VIN and if it is stored in both trip and charge dataframes.
    # Otherwise, it will proceed calculating the overall critical data.
    if key_user != '' and key_user in df_trip.index and key_user in df_charge.index:
        df_trip = df_trip[df_trip.index == key_user]
        df_charge = df_charge[df_charge.index == key_user]

    # Generate a dictionary with all data of interest, using both df_trip and df_charge
    # to do so
    new_row = {
        'Connected vehicles':           df_trip.index.nunique(),
        'Total distance':               round(sum(df_trip["Total distance"])),
        'City percentage':              round(100*sum(df_trip["City distance"])/sum(df_trip['Total distance'])),
        'Sport percentage':             round(100*sum(df_trip["Sport distance"])/sum(df_trip['Total distance'])),
        'Flow percentage':              round(100*sum(df_trip["Sport distance"])/sum(df_trip['Total distance'])),  
        'Average trip distance':        round(df_trip["Total distance"].mean()),
        'Average consumption':          round(((sum(df_trip["Total energy"]) - sum(df_trip["Total regen"])) / sum(df_trip["Total distance"]))),
        'Average range':                round(7500/((sum(df_trip["Total energy"]) - sum(df_trip["Total regen"])) / sum(df_trip["Total distance"]))),
        'Average charged SoC':          round((df_charge['uSoC F']-df_charge['uSoC I']).mean()),
        'Average final charging SoC':   round(df_charge['uSoC F'].mean()),
        'Shucko':                       round(len(df_charge["Connector"][df_charge["Connector"] == 0])*100/df_charge.shape[0]),
        'Max km in month':              find_max_distance(df_trip)[1],
        'Max km in month VIN':          find_max_distance(df_trip)[0],
        'Max km odometer':              df_trip['End odometer'].max(),
        'Max km odometer VIN':          df_trip['End odometer'].idxmax(),
        'Trips between charges':        round(df_trip.shape[0]/df_charge.shape[0],1)                         
    }

    df_month = pd.DataFrame([new_row])
    
    # Generate the date string and update df_month
    date_string = f'{year}-{month:02}'
    date = np.datetime64(date_string)
    df_month['Date'] = [date]

    return df_month

def df_add_df_to_parquet_file(file_path:str,df_new:pd.DataFrame) -> pd.DataFrame:
    # This function will generate and modify a new .parquet given a filename
    # and dataframe to ba added. If the file is not found, it will automatically create
    # a folder and file to store the given dataframe.
    # 
    # This function is internally used to generate/edit the trip, charge and critical
    # data files. In case there is no file created and placed into the df directory,
    # a new file is created. Plus, if there is no df/ directory, a new folder is created
    # in order to store subsequent data
    # 
    # INPUT:
    #   - file_path
    #   - df_new: dataframe containing new data to be stored
    # 
    # OUTPUT:
    #   - Resulting dataframe
    
    # If file exists
    if os.path.exists(file_path):
        # Read and add new data. Then deletes any duplicated rows
        # before overwriting the .parquet file
        df_exist = pd.read_parquet(file_path)
        df_final = pd.concat([df_exist,df_new])
        

        # If the file_path corresponds to a critical data type
        # Erase possible duplicates and sort rows by ascending date
        if 'Date' in df_final.columns:
            df_final.drop_duplicates(subset='Date',keep='last',inplace=True)
            df_final.sort_values(by='Date',ascending=True,inplace=True)
            df_final.dropna(axis=1,inplace=True)
        
        # Otherwise, just check that no duplicates are left in the dataframe
        else:
            df_final.drop_duplicates(inplace=True)
        # Overwrite file
        table = pa.Table.from_pandas(df_final)
        pq.write_table(table,file_path)
       
        return df_final

    # If file does not exist, check if there's a folder to add
    # the new file. If there is not any directory, create one
    if not (os.path.exists('df') and os.path.isdir('df')):
       os.makedirs('df')

    # Generate the new file
    table = pa.Table.from_pandas(df_new)
    pq.write_table(table,file_path)
    
    return df_new
    
def df_add_month_to_critical_data(file_path_trip:str, file_path_charge:str, year:int, month:int) -> pd.DataFrame:
    # This function will either create critical_data.parquet and add this 
    # month's critical data or just add the critical data to an existing file
    # 
    # INPUT:
    #   - df_file_path: relative path to the .parquet file that contains the month's
    #                   data
    # 
    # OUTPUT:
    #   - new_month_df: dataframe that has been stored into a .parquet file
    
    month_df = df_generate_month_df(file_path_trip,file_path_charge,year,month)
    new_month_df = df_add_df_to_parquet_file(CRITICAL_DATA_FILE_PATH,month_df)

    return new_month_df

def df_append_data(df_new:pd.DataFrame, type_name:str) -> int:
    # Given a dataframe and the type of dataframe that is given ('trip' or 'charge') it will
    # 
    # 1) Check if there are different months within the dataframe
    # 2) Check if there is already an existing file containing data from that month
    # 3) Generate or append df_new to its corresponding .parquet file
    # 4) Update month's critical data or generate a new entry if not existing
    if type_name == 'trip':
        TIMESTAMP_COLUMN = 'Timestamp CT'
    
    elif type_name == 'charge':
        TIMESTAMP_COLUMN = 'Timestamp CC'
   
    timestamp_max=df_new[TIMESTAMP_COLUMN].max()
    date_max=datetime.datetime.utcfromtimestamp(timestamp_max)
    year_max=date_max.year
    month_max=date_max.month
    timestamp_min=df_new[TIMESTAMP_COLUMN].min()
    date_min=datetime.datetime.utcfromtimestamp(timestamp_min)
    year_min=date_min.year
    month_min=date_min.month

    date_start = datetime.datetime(year_min, month_min, 1) 
    date_end = datetime.datetime(year_max, month_max, 31)  

    # Iterate through all months
    current_date = date_start
    while current_date <= date_end:
        # Get the timestamps of the beginning and end of each month
        timestamp_i = datetime.datetime(current_date.year, current_date.month, 1).timestamp()
        timestamp_f = (datetime.datetime(current_date.year, current_date.month % 12 + 1, 1) - timedelta(days=1)).timestamp()

        # Generate a new dataframe that contains only data from the corresponding month
        df_month = df_new[(df_new[TIMESTAMP_COLUMN] > timestamp_i) & (df_new[TIMESTAMP_COLUMN] <= timestamp_f)]

        # Get the filename of the month and add the resulting dataframe into the .parquet file
        filename=f'df/{current_date.year}_{current_date.month:02}_{type_name}.parquet'
        df_add_df_to_parquet_file(filename,df_month)
        
        # Check if both files exist and update/create the critical data file
        filename_trip = f'df/{current_date.year}_{current_date.month:02}_trip.parquet'
        filename_charge = f'df/{current_date.year}_{current_date.month:02}_charge.parquet'

        if os.path.exists(filename_trip) and os.path.exists(filename_charge):
            df_add_month_to_critical_data(filename_trip,filename_charge,current_date.year,current_date.month)
    
        # Get to the next month
        current_date = current_date + timedelta(days=32 - current_date.day)

    return 0

def df_get_last_months_critical_data(num_months:int) -> pd.DataFrame:
    # Returns a dataframe containing the critical data stored in month.parquet.
    # The number of columns will be fixed by "num_columns" so that if the last
    # x months are requestet. A dataframe containing the last x months will be
    # returnes
    # 
    # INPUT:
    #   - num_months: number of last month that is wanted to be plotted
    # 
    # OPUTPUT:
    #   - total_df: concatenation of num_months' dataframes

    # Check if there's any months.parquet file, if not, return -1
    if not os.path.exists(CRITICAL_DATA_FILE_PATH):
        return -1
    
    aux_df = pd.read_parquet(CRITICAL_DATA_FILE_PATH)

    # Get the last "num_months" columns from the critical data file
    # It checks whether num_months is greater than the number of rows available
    # to avoid errors
    last_months_df = aux_df.tail(min(num_months,aux_df.shape[0]))

    return last_months_df

