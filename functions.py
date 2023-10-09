import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# A partir de aquí, las funciones están mas optimizadas y permiten usarlas para multiples
# variables o una de sola, si se desea.

def multi_histogram(dataframe,elements,units='',start=-200,end=200,step=10, title='Unnamed distribution'):
    

    #First we generate the figure
    fig = go.Figure()
    
    #Now we add a new trace for every element
    num_elements = len(elements)
    for i in range(num_elements):
        x_values=[]
        for value in dataframe[elements[i]]:
          x_values.append(value)  
        
        fig.add_trace(go.Histogram(
            x=x_values,
            histnorm='percent',
            name=elements[i],
            xbins=dict(
                start=start,
                end=end,
                size=step
            ),
            opacity=0.85
        ))
    
    #Final configuration of the figure
    fig.update_layout(
        title_text=title, # title of plot
        xaxis_title_text=units, # xaxis label
        yaxis_title_text='Percentage', # yaxis label
        bargap=0.2, # gap between bars of adjacent location coordinates
        bargroupgap=0.1 # gap between bars of the same location coordinates
    )

    return fig

def generate_go_pie(dataframe,elements,title='Unnamed pie chart'):
    # Pie chart figure generator given a dataframe, which contains all the necessary data,
    # elements to display and the title of the pie chart

    # This is an auxiliary function, it doesn't generate a Figure capable of being plotted
    # instead, this function helps 'pie_chart' to generate a subplot in case the user wants
    # to plot more than one pie_chart at a time
    # 
    # INPUTS:
    #   - dataframe
    #   - elements
    #   -title
    # 
    # OUTPUTS
    #   - go.Pie element 
    
    # Get the number of elements to be displayed
    num_elements = len(elements)

    # For each element (column), add all its values and save it into a data vector
    total_value=[]

    for element in elements:
        aux_value = 0
        for value in dataframe[element]:
            aux_value += value
        total_value.append(value)
    
    # Generate pie chart
    fig = go.Pie(
        labels=elements,
        values=total_value,
        name=title
    )

    return fig

def pie_chart(dataframe,elements,title='Unnamed pie chart'):

    # This function creates a plotable pie chart figure. It can create subplots containing
    # multiple pie_charts in case it is needed to segregate certain information into different
    # categories but visualised together
    # 
    # INPUTS:
    #   - dataframe
    #   - elements: this is an array of arrays (every position of which contains the names of a
    #               single pie_chart)
    #   - title
    # 
    # OUTPUTS:
    #   - pie chart figure  

    # Get the number of elements passed as parameter
    num_elements = len(elements)

    # Create subplots, we suppose that the user wants the plots to be one next to the other
    fig = make_subplots(
        rows=1,
        cols=num_elements,
        specs=[[{'type':'domain'}, {'type':'domain'}]]
    )

    for i in range(num_elements):
        fig.add_trace(generate_go_pie(dataframe,elements[i],''),1,i+1)

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(title_text=title)
    
    return fig