import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

def search_and_add(dataframe,elements):

# This function searches the columns introduced as parameter and returns
# a integer list of the sum separated by column and returns a dataframe
# containing the list of elements as 'Category' and the results as 'Values'
# 
# INPUT: dataframe and elements
# OUTPUT: results dataframe
    
    num_elements = len(elements)
    
    # Generate a integer string with num_col positions
    results=[]
    for i in range(num_elements):
        results.append(0)
   
    aux=0

    # We run through the dataframe columns searching for every element
    for column in dataframe.columns:        
        for i in range(num_elements):
            if column == elements[i]:
                for value in dataframe[column]:
                    results[i] += value
                    aux+=1
        if aux == num_elements:
            break
    # Generation of a results dataframe, containing the elements of the
    # search and the results associated to adding all values of each element
    df = {
        'Category':elements,
        'Values': results
    }
    return df

def update_count(value,count,bounds,num_bounds):
# Function in charge of modifying count depending on 'value'.
# Bounds delimits differents "data boxes", if the value of 'value' is conained within the "i-th"
# bound, we add up 1 to the "i-th" position of 'count'.
#
# INPUTS:
#   - value: value to be compared
#   - count: list of integers, each position represents one "data box"
#   - bounds: list of integers, contains the "data box" limits
#   - num_bounds: number of bounds

# OUTPUT: 1 i OK

    for i in range(num_bounds-1):
        if value >= bounds[i] and value < bounds[i+1]:
            count[i] += 1
    return 1      

def search_and_count(dataframe,elements,bounds):
    
    num_elements = len(elements)
    num_bounds = len(bounds)
    aux_count=0
    aux=0
    
    # Generate a integer string with num_col positions and
    # one to count
    count=[]
    pos=[]
    for i in range(num_bounds-1):
        count.append(0)
        pos.append(i)
   
    aux=0

    # We run through the dataframe columns searching for every element
    for column in dataframe.columns:        
        for i in range(num_elements):
            if column == elements[i]:
                for value in dataframe[column]:
                    update_count(value,count,bounds,num_bounds)
                    aux_count += 1
                aux+=1
        if aux == num_elements:
            break
    for i in range(num_bounds-1):
        count[i] *= 100
        count[i] /= aux_count
    
    # Generation of a results dataframe, containing the elements of the
    # search and the results associated to adding all values of each element
    df = {
        'Percentage': count,
        'Rank': pos
    }
    return df

def pie_chart_columns(dataframe,elements,title='Unnamed pie chart'):

# This function manages to generate and plot a pie chart given a database and
# a vector of strings which will contain the name of the columns of
# which one wants to plot
#
# INPUT: dataframe & elements
# OUTPUT: -1 if error, 0 if OK

    num_elements = len(elements)
    if num_elements <= 0:
        return -1
  
    df = search_and_add(dataframe,elements)

    fig = px.pie(df, values='Values',names='Category',title=f'{title}', template='seaborn')
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    fig.show()

    return 0

def distribution_columns(dataframe,elements,bounds,units,title='Unnamed distribution'):
    # This function generates a distribution plot given a list of
    # columns to analise and the boundaries that will conform the
    # discrete distribution
    # 
    # INPUTS:
    #   - dataframe: will contain all the data
    #   - elements: which columns will be taken into account
    #   - bounds: list of boundaries between bins
    #   - units: to be displayed in the x-axis
    #   - title: title of the plot
    # 
    # OUTPUT
    #   - -1 if error, 0 if OK 

    if len(elements) <= 0:
        return -1
    
    df = search_and_count(dataframe,elements,bounds)

    fig = px.bar(df,x='Rank',y='Percentage',title=f'{title}',template="seaborn")

    fig.update_xaxes(
        tickvals=df['Rank'],title_text = '',
        ticktext=[f'{bounds[i]}-{bounds[i + 1]} {units}' for i in range(len(bounds) - 1)]
    )


    fig.show()

    return 0

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