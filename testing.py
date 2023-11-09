import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import statsmodels.api as sm
import os
import json
from functions import *
from consumption_vs_temp import *
from scipy import interpolate


INDEX = 'VIN'
KEY_COLUMNS = ['VIN','Id','Timestamp']
NUM_ROWS = 10000
DISTANCE_COLUMN = 'Total (km)'
TEMP_COLUMN = 'Avg temp'
VOLTAGE_COLUMN = 'Average V'
SOC_COLUMN = 'SoC delta (%)'


KEY_ELEMENTS = [DISTANCE_COLUMN,SOC_COLUMN,TEMP_COLUMN,VOLTAGE_COLUMN]

df = df_from_elements('Ray_Data_Base.xlsx','VIN',5000,KEY_COLUMNS,KEY_ELEMENTS)


CONSUMPTION_COLUMN = 'Consumption SoC(%)/km'
df[CONSUMPTION_COLUMN] = df[SOC_COLUMN]/df[DISTANCE_COLUMN]
df[VOLTAGE_COLUMN] /= 1000
df[TEMP_COLUMN] /= 100
df[CONSUMPTION_COLUMN] *= 100

fig = generate_response_surface(df,TEMP_COLUMN,VOLTAGE_COLUMN,CONSUMPTION_COLUMN,'Superficie de respuesta')
fig.show()
"""
import plotly.graph_objects as go
import numpy as np
from scipy import interpolate

# Genera algunos datos de ejemplo (puntos de dispersión)
x = df[VOLTAGE_COLUMN]
y = df[TEMP_COLUMN]
z = df[CONSUMPTION_COLUMN]

# Crea un gráfico de dispersión 3D
scatter_fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode='markers')])

# Define una malla regular para la superficie
xi = np.linspace(min(x), max(x), 50)
yi = np.linspace(min(y), max(y), 50)
xi, yi = np.meshgrid(xi, yi)

# Interpola los datos de dispersión en la malla regular
zi = interpolate.griddata((x, y), z, (xi, yi), method='cubic')

# Crea la superficie a partir de la malla interpolada
surface_fig = go.Figure(data=[go.Surface(z=zi, x=xi, y=yi)])

# Muestra el gráfico de dispersión 3D
scatter_fig.show()

# Muestra el gráfico de superficie de respuesta
surface_fig.show()"""
