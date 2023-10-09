import pandas as pd
import plotly.express as px
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

def pie_chart_columns(dataframe,elements,title='Unnamed distribution'):

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

def regression_line(dataframe,elements):
    return