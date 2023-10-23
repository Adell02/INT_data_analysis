import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import statsmodels.api as sm
import os

from functions import *

"""
Consumo vs temperatura.

La idea es conseguir generar un grafico significativo que relacione el consumo (medio seguramente) a traves del tiempo en funcion de la temperatura de la
batería, inversor, motor ...?

La idea es ir vehiculo por vehiculo y obtener los siguientes datos:
    1)  Consumo, definido como delta_SOC(%) / km. Para ello usaremos el campo SoC delta (%) en B1 y Total(km) en C2. Nos indican, respectivamente, qué SoC
        se ha consumido en el trayecto y cuantos km se ha recorrido.
    
    2)  Temperatura. No se puede estimar temperatura ambiente, por lo que recurriremos a realizar la comparativa según alguna de las siguientes temperaturas:
        del BMC (o de la batería), del inversor i/o del motor. Una idea es representar las tres tendencias juntas

    3)  Relacionarlas, una idea es mediante un scatter plot con lineas de tendencia, de esta manera se puede observar con más facilidad si hay alguna relación
        Sería interesante poder generar una función que te haga una recta de regresión pero que sea por tramos y no lineal, para ver si en algun rango de temp.
        el comportamiento es diferente al esperado.

    4) Una opción es incluír en el gráfico un vehiculo concreto para ver el comportamiento genérico vs el de un usuario en concreto
"""

INDEX = 'VIN'
KEY_COLUMNS = ['VIN','Id','Timestamp']
NUM_ROWS = 10000
DISTANCE_COLUMN = 'Total (km)'
TEMP_COLUMN = 'Avg temp'
SOC_COLUMN = 'SoC delta (%)'
TEXT_OFFSET = -100


def weigh(value,mean,std_dev):
    # Gives a weight to the value, following a mean and standard deviation passed
    # as parameters
    # 
    # INPUTS
    #   - value:    what value needs to be weighed
    #   - mean:     desired mean
    #   - std_dev:  desired standard deviation
    # OUTPUTS
    #   - Weighted value

    z_score = (value - mean) / std_dev
    weighted_val = 1 / (std_dev * np.sqrt(2 * np.pi)) * np.exp(-0.5 * z_score**2)
    return weighted_val


def get_consumption_vs_temp(data_file_route,num_samples=10000):
    
    # 1. Generate a dataframe containing all data necessary:
    #   - Total (km)
    #   - SoC delta (%)
    #   - Avg temp (ºC * 10)  --> average temperature of the BMS (then, battery temp)
    KEY_ELEMENTS = [DISTANCE_COLUMN,SOC_COLUMN,TEMP_COLUMN]
    df = df_from_elements(data_file_route,INDEX,num_samples,KEY_COLUMNS,KEY_ELEMENTS)

    # 2. Generate and compute the consume column. Since generate_df_from_elements assures that 
    # the dataframe is well ordered, we don't have to check the index
    CONSUMPTION_COLUMN = 'Consumption SoC(%)/km'
    df[CONSUMPTION_COLUMN] = df[SOC_COLUMN]/df[DISTANCE_COLUMN]

    # 3. We want to show only the 95% of points below that percentile
    column_filtered_above = df[CONSUMPTION_COLUMN].quantile(0.975)
    column_filtered_below = df[CONSUMPTION_COLUMN].quantile(0.025)

    # Modify the dataframe so the points that are going to be shown are those that are comprised
    # between the 2.5% and 97.5% of the samples.
    # Essentially, we're filetring a total of 5% of points that are furthest from the mean
    df_filtered = df[(df[CONSUMPTION_COLUMN] <= column_filtered_above) & (df[CONSUMPTION_COLUMN] >= column_filtered_below)]
    
    # 4. Get a scatter plot
    fig_filtered = generate_scatter_plot(df_filtered,TEMP_COLUMN,CONSUMPTION_COLUMN,'Consumption vs Temp Filtered',True)

    # 5. Get the correlation between variables

    """
    Developer comment: From the emprical analysis it is known that there could be a linear relation between
    the motorcycle consumption and the battery temperature, to measure by how much these two variables are
    related we'll get the Pearson correlation of them
    """
    # Get correlation using filtered points
    correlation = df_filtered[CONSUMPTION_COLUMN].corr(df_filtered[TEMP_COLUMN])

    # 6. Display the correlation on the figures
    
    # Get the position of the top-right corner to display the text in that point
   
    x_position_filtered = max(df_filtered[TEMP_COLUMN])+TEXT_OFFSET
    y_position_filtered = max(df_filtered[CONSUMPTION_COLUMN])

    # Generate text and place it in the figures
    fig_text = f'Correlation: {round(correlation*100,2)}%'
    fig_filtered.add_trace(go.Scatter(x=[x_position_filtered], y=[y_position_filtered], mode="text",text=fig_text, showlegend=False))
    fig_filtered.update_traces(textfont=dict(size=15, color="black"))

    """
    This second part consists of showing a different analyses of the situation. Now we are going to weigh the points to be shown
    into the scatter plot, to do so:
        1) Get the mean and standard deviation of the km 
        2) Applly the weigh function to the consumption values
        3) Modify the original dataframe CONSUMPTION_COLUMN
        4) Display the graphic as done previously

    This will ensure that the more relevant samples are those that correspond to a trip distance closer to the mean
    """

    # 1. Get the mean and standard dev
    mean = df[DISTANCE_COLUMN].mean()
    std_dev = df[DISTANCE_COLUMN].std()

    # 2 & 3. Apply the weigh function to the consumption column and modify original df
    weighed_consumption = [weigh(value,mean,std_dev) for value in df[CONSUMPTION_COLUMN]]
    df[CONSUMPTION_COLUMN] = weighed_consumption


    # 3. Display the graphic
    column_filtered_above = df[CONSUMPTION_COLUMN].quantile(0.975)
    column_filtered_below = df[CONSUMPTION_COLUMN].quantile(0.025)

    df_weighed = df[(df[CONSUMPTION_COLUMN] <= column_filtered_above) & (df[CONSUMPTION_COLUMN] >= column_filtered_below)]
    fig_weighed = generate_scatter_plot(df_weighed,TEMP_COLUMN,CONSUMPTION_COLUMN,'Consumption vs Temp Weighed',True)

    correlation = df_weighed[CONSUMPTION_COLUMN].corr(df_weighed[TEMP_COLUMN])
   
    x_position_weighed = max(df_weighed[TEMP_COLUMN])+TEXT_OFFSET
    y_position_weighed = max(df_weighed[CONSUMPTION_COLUMN])

    # Generate text and place it in the figures
    fig_text = f'Correlation: {round(correlation*100,2)}%'
    fig_weighed.add_trace(go.Scatter(x=[x_position_weighed], y=[y_position_weighed], mode="text",text=fig_text, showlegend=False))
    fig_weighed.update_traces(textfont=dict(size=15, color="black"))

    
    return fig_filtered, fig_weighed


"""
Comentarios Marco:

- Estaría bien algun escalado que cogiera un 95% de puntos (por ejemplo)

- Vemos una variacion del 0.5 al 0.7 --> casi un 50% de empeoramiento por temperatura

Cómo mejorar el análisis
    1)  Calcular el coeficiente de correlación para ver qué tanto afecta la temperatura al
        consumo
    2)  Para un análisis más significativo, ponderar los resultados por la distancia del
        trayecto, por ejemplo dist<5km --> ponderamos por 0 (no lo incluímos)
        
        Una idea es hacer una distribución de los km de los viajes y ponderar según la
        distribución
"""