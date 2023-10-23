import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import statsmodels.api as sm
import os

from functions import *
from consumption_vs_temp import *


def generate_dashboard_graphics(data_file_route):

    # Fistly, create a dataframe containing all columns needed:
    LIST_COLUMNS = ['City (km)','Sport (km)','Flow (km)','Sail (km)','Regen (km)',
                    'City energy (Wh)','Sport energy (Wh)','Flow energy (Wh)','City regen (Wh)','Sport regen (Wh)',
                    'Total energy (Wh)','Total regen (Wh)',
                    'End odometer','Min cell V','Max cell V',
                    'Total (km)','Avg temp','SoC delta (%)',
                    'Motor min T (°C)','Motor max T (°C)',
                    'Inv  min T (°C)','Inv max T (°C)']
    
    INDEX = 'VIN'
    KEY_COLS = ['VIN','Id','Timestamp']
    
    # Generate a dataframe containing all columns listed before
    df =df_from_elements(data_file_route,INDEX,None,KEY_COLS,LIST_COLUMNS)
    
    # Generate functions in order and add them to a figures vector
    fig_vector = []

    fig_vector.append(
        generate_pie_chart(
            df,
            ['City (km)','Sport (km)','Flow (km)','Sail (km)','Regen (km)'],
            'Modos de Conducción por km'))    
    fig_vector.append(
        generate_pie_chart(
            df,
            ['City energy (Wh)','Sport energy (Wh)','Flow energy (Wh)','City regen (Wh)','Sport regen (Wh)'],
            'Modos de Conducción por Wh'))
    fig_vector.append(
        generate_multi_histogram(
            df,
            [ 'Total energy (Wh)','Total regen (Wh)'],
            'Wh',
            title = 'Distribución consumo y regeneración de energía'
        )
    )
    fig_vector.append(
        generate_scatter_plot_user(
            df,
            'UDNR7711AM0000137',
            'End odometer',
            ['Min cell V','Max cell V'],
            'Comparación usuario: Tensiones de celda vs Uso',
            True, True
        )
    )

    fig_vector.append(get_consumption_vs_temp(df))

    fig_vector.append(
        generate_multi_histogram(
            df,
            ['Motor min T (°C)','Motor max T (°C)'],
            'ºC',
            title = 'Distribución Temperatura Motor'
        )
    )

    fig_vector.append(
        generate_multi_histogram(
            df,
            ['Inv  min T (°C)','Inv max T (°C)'],
            'ºC',
            title = 'Distribución Temperatura Inversor'
        )
    )

    return fig_vector