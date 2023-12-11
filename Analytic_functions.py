from functions import *
from plots_generation import *
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import statsmodels.api as sm
import os
import json
import numpy as np
from scipy.interpolate import griddata

TEXT_OFFSET = 500

def delta_SoC_vs_Total_Energy(df_trip):
    '''
    This function takes a DataFrame df_trip as input. It calculates the change in State of Charge (SoC) and the total energy consumption from the DataFrame. It then generates a scatter plot using the generate_scatter_plot function, with the total energy on the x-axis and the change in SoC on the y-axis. The function returns the generated scatter plot.
        Input: df_trip (DataFrame)
        Output: fig (plotly.graph_objects.Figure)
    '''
    TITLE = 'Differential SoC vs Total energy'
    TOTAL_ENERGY = 'Total energy'
    DELTA_SOC = 'SoC delta'
    fig = generate_scatter_plot(df_trip,TOTAL_ENERGY,DELTA_SOC,title= TITLE, reg_line=True)
    # Get correlation using filtered points
    correlation = df_trip[DELTA_SOC].corr(df_trip[TOTAL_ENERGY])
    # Get the position of the top-right corner to display the text in that point
    x_position_filtered = min(df_trip[TOTAL_ENERGY])+TEXT_OFFSET
    y_position_filtered = max(df_trip[DELTA_SOC])
    # Generate text to display the correlation and place it in the legend
    fig_text = f'r: {round(correlation*100,2)}%'
    fig.add_trace(go.Scatter(x=[x_position_filtered], y=[y_position_filtered], mode="text",name = fig_text ,showlegend=True))
    fig.update_traces(marker=dict(size=3))
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
))
    return fig


def mode_energy_vs_kilometers(df_trip):
    '''
    This function takes a DataFrame df_trip as input. It calculates the differential energy consumption per kilometer for different driving modes (Sport, City, and Flow) based on the energy consumed and the distance traveled in each mode. It creates a new DataFrame df_final with the calculated differential energy values. It then generates a box plot using the generate_box_plot function, with the differential energy values on the y-axis and the driving modes on the x-axis. The function returns the generated box plot.
        Input: df_trip (DataFrame)
        Output: fig (plotly.graph_objects.Figure)
    '''
    SPORT_MODE = 'Sport energy' 
    CITY_MODE = 'City energy'
    FLOW_MODE = 'Flow energy'
    DISTANCE = 'End odometer'
    DISTANCE_CITY = 'City distance'
    DISTANCE_SPORT = 'Sport distance' 
    DISTANCE_FLOW = 'Flow distance'
    
    DIF_SPORT_MODE = 'Sport (Wh/km)'
    DIF_CITY_MODE = 'City (Wh/km)'
    DIF_FLOW_MODE = 'Flow (Wh/km)'
    TITLE = 'Differential Mode Energy vs Kilometers'
    ELEMENTS_Y = [DIF_CITY_MODE,DIF_SPORT_MODE,DIF_FLOW_MODE]

    df_final = pd.DataFrame()
    df_final[DIF_SPORT_MODE]= df_trip[SPORT_MODE]/df_trip[DISTANCE_SPORT]
    df_final[DIF_CITY_MODE]= df_trip[CITY_MODE]/df_trip[DISTANCE_CITY]
    df_final[DIF_FLOW_MODE]= df_trip[FLOW_MODE]/df_trip[DISTANCE_FLOW]
    fig = generate_box_plot(df_final,ELEMENTS_Y,title = TITLE)
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
))
    return fig


def delta_soc_vs_inv_min_temp(df_trip):
    """
    Calculate the change in State of Charge (SoC) per unit temperature for a given trip dataset.

    Input:
        df_trip (DataFrame): The input trip dataset containing the following columns:
            - 'Inv min T (°C)': The minimum temperature recorded during the trip for the inverter.
            - 'SoC delta (%)': The change in State of Charge (SoC) during the trip.
            - 'Consumption SoC(%)/km': The SoC consumption per kilometer.
            - 'Total (km)': The total distance traveled during the trip.

    Output:
        fig (Figure): The scatter plot figure showing the relationship between the change in SoC per unit temperature and the inverter minimum temperature. The figure includes a regression line.

    Raises:
        Exception: If an error occurs while generating the scatter plot.

    Notes:
        - The function filters out outliers by considering only the 95% of points within the specified percentiles.
        - The function calculates the average change in SoC per unit temperature for each inverter minimum temperature.

    """
    INV_MIN_T = 'Inv min T'
    DELTA_SOC = 'SoC delta'
    TITLE = 'Consumption VS Inversor minimum Temperature'
    SOC_VS_TEMP = 'Diferential Soc vs Inv min T(%/°C)'
    CONSUMPTION_COLUMN = 'Consumption ∂SoC(%)/km'
    DISTANCE_COLUMN = 'Total distance'
    
    df_final = pd.DataFrame()
    df_final[CONSUMPTION_COLUMN] = df_trip[DELTA_SOC]/df_trip[DISTANCE_COLUMN]
    df_final[INV_MIN_T] = df_trip[INV_MIN_T]

    # Check for missing data
    if df_trip[[INV_MIN_T, DELTA_SOC]].isnull().values.any():
        print("Warning! There is missing data in the relevant columns.")

    # Filter out outliers
    column_filtered_above = df_final[CONSUMPTION_COLUMN].quantile(0.975)
    column_filtered_below = df_final[CONSUMPTION_COLUMN].quantile(0.025)
    df_filtered = df_final[(df_final[CONSUMPTION_COLUMN] <= column_filtered_above) & (df_final[CONSUMPTION_COLUMN] >= column_filtered_below)]

    # Calculate the average of the DELTA_SOC values for each INV_MIN_T
    media_por_rango = df_filtered.groupby(INV_MIN_T)[CONSUMPTION_COLUMN].mean().reset_index()

    try:
        fig = generate_scatter_plot(media_por_rango, INV_MIN_T, CONSUMPTION_COLUMN, title=TITLE, reg_line=True)
        fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
))
        return fig
    except Exception as e:
        print(f"Error generating graph! Mistake: {e}")
        return None

#Para entregar
def inv_min_t_vs_cell_min_t_vs_total_energy(df_trip):
    """
    Calculate the response surface for the relationship between the inverse of the minimum temperature,
    the minimum cell temperature, and the total energy.
        Input: df_trip (DataFrame): The input DataFrame containing the trip data.
        Output: DataFrame: The response surface DataFrame.

    """
    INV_MIN_T = 'Inv min T'
    TOTAL_ENERGY = 'Total energy'
    CELL_MIN_T = 'Min temp CT'
    

    fig=generate_response_surface(df_trip, INV_MIN_T, CELL_MIN_T, TOTAL_ENERGY, title='Cell Temperature Response Surface')
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
))
    return fig
#Para entregar
def correlation(df, columns):
    """
    Calculate the correlation matrix for the selected columns in a DataFrame.

    Inputs:
        df (pandas.DataFrame): The input DataFrame.
        columns (list): A list of column names to include in the correlation calculation.

    Outputs:
        correlation_matrix (pandas.DataFrame): The correlation matrix of the selected columns.
    """
    selected_df = df[columns]
    correlation_matrix = selected_df.corr()
    return px.imshow(correlation_matrix, labels=dict(x="Columnas", y="Columnas", color="Correlación"))


def batery_temp_vs_distance(df):
    """
    Batery temperature average vs distance
    Inputs:
        df (pandas.DataFrame): The input DataFrame.
        columns (list): A list of column names to include in the correlation calculation.

    Outputs:
        generate_bar_chart()
    """  
    AVERAGE_TEMP = 'Avg temp'
    DISTANCE_COLUMN = 'Total distance'
    
    # Divide todos los valores de la columna "average temp" por 100 para convertirlos a grados Celsius
    df[AVERAGE_TEMP] = df[AVERAGE_TEMP] / 100

    # Create a new column representing 10 km intervals
    df['Intervalo_10'] = (df[DISTANCE_COLUMN] // 10) * 10

    # Group the data by the new column and calculate the average temperature
    temperatura_media_por_intervalo = df.groupby('Intervalo_10')[AVERAGE_TEMP].mean().reset_index()

    # The .mean() method calculates the mean temperature for each distance interval group
     # .reset_index() resets the index of the DataFrame

    fig = generate_bar_chart(temperatura_media_por_intervalo, element_x='Intervalo_10', elements_y=AVERAGE_TEMP, title='Average Battery Temperature by Distance Interval')

    fig.update_layout(
        xaxis_title='Trips grouped by intervals of 10 km',
        yaxis_title='Temperature (°C)'
    )

    return fig

def regen_vs_temp(df):
    """
    Regen (%) vs average temperature
    Inputs:
        df (pandas.DataFrame): The input DataFrame.
        columns (list): A list of column names to include in the correlation calculation.

    Outputs:
        generate_scatter_plot()
    """ 
    AVERAGE_TEMP = 'Inv avg T'
    CITY = 'City energy'
    SPORT = 'Sport energy'
    FLOW = 'Flow energy'
    CITY_REG = 'City regen'
    SPORT_REG = 'Sport regen'

    df['Total energy'] = df[SPORT] + df[FLOW] + df[CITY]
    df['Total regen'] =  df[SPORT_REG] + df[CITY_REG] 
    df['Regeneration (%)'] = (df['Total regen'] / df['Total energy']) * 100
    
    # 3. We want to show only the 95% of points below that percentile
    column_filtered_above = df['Regeneration (%)'].quantile(0.975)
    column_filtered_below = df['Regeneration (%)'].quantile(0.025)

    # Modify the dataframe so the points that are going to be shown are those that are comprised
    # between the 2.5% and 97.5% of the samples.
    # Essentially, we're filetring a total of 5% of points that are furthest from the mean
    df_filtered = df[(df['Regeneration (%)'] <= column_filtered_above) & (df['Regeneration (%)'] >= column_filtered_below)]
    
    df_filtered = df_filtered.copy()
    df_filtered['Interval'] = df_filtered[AVERAGE_TEMP]

    df_regen = df_filtered.groupby('Interval')['Regeneration (%)'].mean().reset_index()
    # The .mean() method calculates the mean temperature for each distance interval group
    # .reset_index() resets the index of the DataFrame

    fig = generate_scatter_plot(df_regen,element_x='Interval' ,elements_y='Regeneration (%)',title='Regeneration of Battery vs Inversor Temperature',reg_line=True)

    fig.update_layout(
        xaxis_title='Inversor Average Temperature(°C)',
        yaxis_title='Regeneration (%)'
    )
    fig.update_layout(legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
))

    return fig