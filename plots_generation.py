import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import statsmodels.api as sm
from scipy import interpolate

"""
*************************************************************************************************************
This file contains all functions used to generate all basic plots that are supported for the web application.
List of the plots that can be generated:
    - Pie Chart
    - Histogram
    - Scatter Plot (with or w/o regression line)
    - Scatter Plot User (used if a VIN's behaviour has to be compared against the rest of the fleet)
    - Line Chart: not highly recommended, results might not be easily interpreted, user discretion is advised
    - Bar Chart
    - Response Surface: results might not be easily interpreted, data must be prepared for this visualization
    - Box Plot

All plots support multiple variables, that is, if more than one variable is needed to be plotted within the
same graph, these functions will allow if variables are passed as a tuple.

All functions will contain a "generate_" heading, so they are easily distinguished from internal functions.

************************************************************************************************************
"""

"""********************     Trace generation    ********************"""

def trace_pie(dataframe,elements,title='Unnamed pie chart'):
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
    #   - go.Pie trace 
    
    # For each element (column), add all its values and save it into a data vector
    total_value=[]

    for element in elements:
        aux_value = 0
        for value in dataframe[element]:
            aux_value += value
        total_value.append(aux_value)
    
    # Generate pie chart
    trace = go.Pie(
        labels=elements,
        values=total_value,
        name=title
    )

    return trace

def trace_trendline(dataframe,element_x,elements_y,title='Trendline'):

    # This function generates a trendline (performing OLS) given a element to display on the
    # x_axis and allows multiple elements for the y_axis (thus, multiple trendlines)
    # 
    # INPUT:
    #   - dataframe: containing all data
    #   - element_x: which element will be display on the x_axis
    #   - elements_y: elements, trendline of which, will be displayed on the y_axis
    # OUTPUT:
    #   - trandline_vector: contains all traces to be added in a figure


    trendline_vector=[]
    
    if isinstance(elements_y,str):
        elements_X_aux = sm.add_constant(dataframe[element_x])      # elements_x but adding a '1' column for the reg line
        model = sm.OLS(dataframe[elements_y],elements_X_aux).fit()       # generate model 
        trendline = model.predict(elements_X_aux)                   # generate trendline   

        # Now generate the trace for the trendline and add it at the data_vector
        trendline_trace = go.Scatter(
            x=dataframe[element_x],
            y=trendline,
            mode='lines',
            name=f'{title}: {elements_y}'
        )
        trendline_trace.line.dash = 'longdashdot'  #['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']

        trendline_vector.append(trendline_trace)
    
    else:
        for element in elements_y:

            elements_X_aux = sm.add_constant(dataframe[element_x])      # elements_x but adding a '1' column for the reg line
            model = sm.OLS(dataframe[element],elements_X_aux).fit()       # generate model 
            trendline = model.predict(elements_X_aux)                   # generate trendline   

            # Now generate the trace for the trendline and add it at the data_vector
            trendline_trace = go.Scatter(
                x=dataframe[element_x],
                y=trendline,
                mode='lines',
                name=f'{title}: {element}'
            )
            trendline_trace.line.dash = 'longdashdot'  #['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']

            trendline_vector.append(trendline_trace)
    
    return trendline_vector

def trace_scatter_plot(dataframe,element_x,elements_y,reg_line=False):
    # Returns a scatter plot trace vector, given a dataframe, and elements to plot, can integrate a regression
    # line if specified
    # 
    # INPUTS:
    #   - dataframe: containing all data
    #   - element_x: x axis data
    #   - elements_y: vector that contains all the different data to be plotted
    #   - title: title of the graph
    #   - reg_line: boolean to indicate if a reg_line is wanted. Default value is False
    # OUTPUTS:
    #   - plotly trace if OK
    #   - None if error occured
    
    # Plot generation for each data source passed as parameter elements_y
    
    trace_vector=[]          # This vector will contain all traces, one for each element_y
    
    # We have to differentiate if elements_y is a vector or a string, because the for loop won't
    # act as intended if elements_y contains one single string
    if isinstance(elements_y,str):
        trace = go.Scatter(
            x=dataframe[element_x],
            y=dataframe[elements_y],
            mode='markers',
            name=elements_y
        )
        trace_vector.append(trace)

    else:
        for element in elements_y:
            trace = go.Scatter(
                x=dataframe[element_x],
                y=dataframe[element],
                mode='markers',
                name=element
            )
            trace_vector.append(trace)
        
    # A trendline is needed if reg_line is True
    if reg_line:
        trace_trend = trace_trendline(dataframe,element_x,elements_y)
        for trace in trace_trend:
            trace_vector.append(trace)

    return trace_vector

def trace_bar_chart(dataframe,element_x,elements_y):
    
    # Generate a trace_vector to contain all traces for a Bar Chart
    trace_vector = []
    # Check if elements_y is a single element or multiple
    if isinstance(elements_y,str):
        trace_vector.append(go.Bar(x=dataframe[element_x],y=dataframe[elements_y],name = elements_y))
    
    else:
        for element in elements_y:
            trace_vector.append(go.Bar(x=dataframe[element_x],y=dataframe[element],name = element))
    
    
    return trace_vector

def trace_box_plot(dataframe:pd.DataFrame,elements):
# Generates a trace to be added to a box plot

    trace_vector = []
    # Check if elements is a string or a tuple
    if isinstance(elements,str):
        trace_vector.append(go.Box(y=dataframe[elements],name=elements))

    else:
        for element in elements:
            trace_vector.append(go.Box(y=dataframe[element],name=element))
    
    return trace_vector

"""********************     Figures generation    ********************"""

def generate_pie_chart(dataframe,elements,title='Unnamed pie chart'):

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

    # Check if elements is a single vector or multiple to generate one or multiple pie_charts
    if isinstance(elements,(list,tuple)) and isinstance(elements[0],str):
        # elements is a vector (only 1 pie chart is needed)
        fig_trace = trace_pie(dataframe,elements,'')
        fig = go.Figure(fig_trace)

    else:
        # elements is a vector (more than 1 pie chart is needed)
        # Create subplots, we suppose that the user wants the plots to be one next to the other
        fig = make_subplots(
            rows=1,
            cols=num_elements,
            specs=[[{'type':'domain'}, {'type':'domain'}]]
        )
        
        # We use a integer loop so we can assign the subplot position of each pie chart
        for i in range(num_elements):
            fig.add_trace(trace_pie(dataframe,elements[i],''),1,i+1)

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(title_text=title)
    
    return fig

def generate_multi_histogram(dataframe,elements,units='',start=-200,end=200,step=10, title='Unnamed distribution'):
    

    #First we generate the figure
    fig = go.Figure()
    
    # First, we need to check if elements is a vector or a string
    if isinstance(elements,str):
        x_values=[]
        for value in dataframe[elements]:
          x_values.append(value)  
        
        fig.add_trace(go.Histogram(
            x=x_values,
            histnorm='percent',
            name=elements,
            xbins=dict(
                start=start,
                end=end,
                size=step
            ),
            opacity=0.85
        ))
    else:
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

    # Add legend and display it in the top-right corner of the graph
    fig.update_layout(showlegend=True, legend=dict(x=0.85, y=0.95, traceorder='normal', orientation='v'))


    return fig

def generate_scatter_plot(dataframe,element_x,elements_y,title='Unnamed Scatter Plot',reg_line=False):
    # Returns a scatter plot trace, given a dataframe, and elements to plot, can integrate a regression
    # line if specified
    # 
    # INPUTS:
    #   - dataframe: containing all data
    #   - element_x: x axis data
    #   - elements_y: vector that contains all the different data to be plotted
    #   - title: title of the graph
    #   - reg_line: boolean to indicate if a reg_line is wanted. Default value is False
    # OUTPUTS:
    #   - plotly trace if OK
    #   - None if error occured
    
    # Plot generation for each data source passed as parameter elements_y
    
    # Generate a vector containing all traces to be plotted
    data_vector = trace_scatter_plot(dataframe,element_x,elements_y,reg_line)
    
    # Definition of the basic layout of the graphic, adding graphic title and the x_axis name
    layout = go.Layout(
        title = title,
        xaxis=dict(title=element_x)
    )

    # From all traces, we generate the figure
    fig = go.Figure(data=data_vector,layout=layout)

    # Add legend and display it in the top-right corner of the graph
    fig.update_layout(showlegend=True, legend=dict(x=0.85, y=0.95, traceorder='normal', orientation='v'))
    fig.update_traces(marker=dict(size=3))

    return fig

def generate_scatter_plot_user(dataframe,key_user,element_x,elements_y,title="Unnamed Scatter Plot",user_reg_line=False,reg_line=False):
    # Returns a scatter plot, given a dataframe, user and elements to plot, can integrate a regression
    # line if specified
    # 
    # INPUTS:
    #   - dataframe: containing all data
    #   - key user: ID of the user that data is needed
    #   - element_x: x axis data
    #   - elements_y: vector that contains all the different data to be plotted
    #   - title: title of the graph
    #   - user_reg_line: boolean to indicate if a reg_line for the user data is wanted. Default value is False
    #   - reg_line: boolean to indicate if a generic reg_line is needed (for generic, we mean a reg_line of all data of all vehicles)
    # OUTPUTS:
    #   - plotly figure if OK
    #   - None if error occured
  
    
    # Get user dataframe, if user is not found or '' is passed, plot a generic scatter plot
    # (omits the user particularity and generates a simple scatter plot)
    if key_user in dataframe.index:
        user_df = dataframe.loc[dataframe.index == key_user]
    else:
        fig = generate_scatter_plot(dataframe,element_x,elements_y,title,reg_line)
        return fig

    # Use trace_scatter_plot to generate a figure containing all data, to do so, we'll use
    # an auxiliary vector containing all traces
    trace_vector = []

    # Append user data
    user_trace_vector = trace_scatter_plot(user_df,element_x,elements_y,user_reg_line)
    for user_trace in user_trace_vector:
        trace_vector.append(user_trace)

    # If a general trace is wanted
    if reg_line:
        generic_trace_vector = trace_trendline(dataframe,element_x,elements_y,'Generic Trendline')
        for generic_trace in generic_trace_vector:
            trace_vector.append(generic_trace)


   
    # Definition of the basic layout of the graphic, adding graphic title and the x_axis name
    layout = go.Layout(
        title = title,
        xaxis=dict(title=element_x)
    )

    # From all traces, we generate the figure
    fig = go.Figure(data=trace_vector,layout=layout)

    # Get the maximum and minimum value of element_x for better graph visualization
    x_max = user_df[element_x].max() 
    x_min = user_df[element_x].min() 
    fig.update_xaxes(range=[x_min,x_max])

    # Add legend and display it in the top-right corner of the graph
    fig.update_layout(showlegend=True, legend=dict(x=0.85, y=0.95, traceorder='normal', orientation='v'))
    fig.update_traces(marker=dict(size=3))


    return fig

def generate_line_chart(dataframe,element_x,elements_y,title='Unnamed Line Chart'):

    trace_vector=[]
    for element in elements_y:
        dataframe = dataframe.sort_values(by=[element_x,element])
        trace = go.Scatter(x=dataframe[element_x], y=dataframe[element], mode='lines', name=element)
        trace_vector.append(trace)

    # Definition of the basic layout of the graphic, adding graphic title and the x_axis name
    layout = go.Layout(
        title = title,
        xaxis=dict(title=element_x)
    )

    # From all traces, we generate the figure
    fig = go.Figure(data=trace_vector,layout=layout)

    # Add legend and display it in the top-right corner of the graph
    fig.update_layout(showlegend=True, legend=dict(x=0.85, y=0.95, traceorder='normal', orientation='v'))
    
    return fig

def generate_bar_chart(dataframe,element_x,elements_y,title='Unnamed Bar Chart'):
    # This function generates a bar chart given a dataframe and multiple or single
    # elements to be plotted
    # 
    # INPUTS:
    #   - dataframe
    #   - element_x
    #   - elements_y
    #   - title
    #   
    # OUTPUT
    #   - plotly figure

    trace_vector = trace_bar_chart(dataframe,element_x,elements_y)

    fig = go.Figure(data=trace_vector)

    fig.update_layout(
        title = title,
        xaxis_title = element_x,
        barmode = 'group'               #Options available: group, stack, relative
    )

    # Add legend and display it in the top-right corner of the graph
    fig.update_layout(showlegend=True, legend=dict(x=0.85, y=0.95, traceorder='normal', orientation='v'))
    
    return fig

def generate_response_surface(dataframe,element_x,element_y,element_z,title='Unnamed Response Surface'):
    
    # To simplify notation, specify axis
    x = dataframe[element_x]
    y = dataframe[element_y]
    z = dataframe[element_z]

    # Generate a grid that will be used to display the 3D data. The xi and y1 rank, must 
    # reach all data from element_x and element_y
    x_grid = np.linspace(min(x),max(x),500)
    y_grid = np.linspace(min(y),max(y),500)
    x_grid, y_grid = np.meshgrid(x_grid,y_grid)

    # Interpolate data in the grid
    z_grid = interpolate.griddata((x, y), z, (x_grid, y_grid), method='cubic')
    
    # Generate surface from the interpolated grid
    layout = go.Layout(title = title)
    fig = go.Figure(data=[go.Surface(z=z_grid, x=x_grid, y=y_grid)],layout=layout)
    
    # Add a topographic map to the figure
    fig.update_traces(contours_z=dict(
        show=True, 
        usecolormap=True,
        highlightcolor="limegreen",
        project_z=True))
    
    # Edit axis' names and aspect of the figure
    fig.update_layout(scene=dict(
        xaxis_title = element_x,
        yaxis_title = element_y,
        zaxis_title = element_z,
        aspectmode = 'cube'
    ))
    return fig

def generate_box_plot(dataframe:pd.DataFrame,elements,title='Unamed Box Plot'):
    # Generate a box plot given a dataframe and the elements to be plotted
    # INPUTS:
    #   - dataframe
    #   - elements
    #   - title
    # OUTPUT:
    #   - figure
    trace_vector = trace_box_plot(dataframe,elements)

    layout = go.Layout(title = title)
    fig = go.Figure(data=trace_vector,layout=layout)

    # Add legend and display it in the top-right corner of the graph
    fig.update_layout(showlegend=True, legend=dict(x=0.85, y=0.95, traceorder='normal', orientation='v'))

    return fig
