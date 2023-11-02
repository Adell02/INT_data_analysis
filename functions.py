import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import statsmodels.api as sm
import os
import json
from scipy import interpolate
import pyarrow as pa
import pyarrow.parquet as pq
import datetime



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

"""
def test_scatter_plot_user(dataframe,key_user,elements,title='Unnamed scatter plot',reg_line = False):
    
    if len(elements) != 2:
        return None

    # De dataframe, cogemos sólo la información disponible del usuario que nos han pasado
    # From dataframe, we store in an auxiliary dataframe only the information corresponding to
    # the key_user. It will search for it in key_columns
    if key_user in dataframe.index:
        user_df = dataframe.loc[dataframe.index == key_user]
    else:
        return None
    
    # Check if we want a regression line
    if reg_line == True:
        trend='ols'
    else:
        trend = False
    
    # Plot generation
    fig = px.scatter(
        user_df,
        x=elements[0],
        y=elements[1],
        opacity=0.65,
        trendline=trend,
        trendline_color_override='darkblue'
    )


    return fig
"""

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
    # act as intended if elements_y contains one single element
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
    

    # Get user dataframe
    if key_user in dataframe.index:
        user_df = dataframe.loc[dataframe.index == key_user]
    else:
        return None

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
    
    return fig

def generate_bar_chart(dataframe,element_x,elements_y,title='Unnamed Bar Chart'):
    
    trace_vector = trace_bar_chart(dataframe,element_x,elements_y)

    fig = go.Figure(data=trace_vector)

    fig.update_layout(
        title = title,
        xaxis_title = element_x,
        barmode = 'group'               #Options available: group, stack, relative
    )
    
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
    fig = go.Figure(data=[go.Surface(z=z_grid, x=x_grid, y=y_grid)])
    
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

"""********************     Dataframe functions    ********************"""

def df_from_elements(file_route,index,rows,key_cols,elements):
    # Returns a dataframe containing all data passed as 'elements' structured following
    # 'key_cols'. Additionally, an index and number of rows has to be added.
    # Note that the dataframe is generated from an excel
    # 
    # INPUTS
    #   - file_route:   relative route to the excel file
    #   - index:        name of the column used as index
    #   - rows:         number of rows wanted for the dataframe 
    #   - key_cols:     name of the columns used to identify each vehicle in the dataframe
    #   - elements:     name of the data columns that we need to include in the dataframe
    # 
    # OUTPUT  
    #   -   dataframe generated

    # Read and save the xlsx file in 'excel' variable
    excel = pd.ExcelFile(file_route)

    # Generate an empty dataframe to which 'key_cols' will be added and index will be
    # determined
    custom_df = pd.DataFrame()
    num_key_cols = len(key_cols)
    key_cols_found = 0

    # This loop finds whether there are all 'key_cols' in one sheet, if so, copy them
    # onto the custom dataframe 'custom_df' and sets the index
    for sheet in excel.sheet_names:
        df = pd.read_excel(file_route, sheet_name=sheet, nrows=rows)

        for column_name in df.columns:
            for key_column in key_cols:
                if column_name == key_column:
                    key_cols_found += 1

        if key_cols_found == num_key_cols:
            custom_df = df[key_cols].copy()
            custom_df.set_index(index,inplace=True)
            break
        
        key_cols_found=0
    
    # Once the custom dataframe has all the key columns, add the elements to be included
    # in the custom dataframe

    num_elements = len(elements) # used to stop the for loop when all elements have been added
    elements_found = 0

    # Create auxiliary list used to merge both the custom_df with the data selected
    columns_to_merge=[]
    for element in key_cols:
        if element != index:
            columns_to_merge.append(element)

    # Iterate through the excel sheets
    for sheet in excel.sheet_names:
        df = pd.read_excel(file_route, sheet_name=sheet, index_col=index, nrows=rows)

        for column_name in df.columns:
            for element in elements:
                if column_name == element:
                    columns_to_merge.append(element)                                #add to the auxiliary list the element to merge
                    custom_df.drop_duplicates(subset=custom_df, inplace=True)       # Drop duplicates is used to prevent duplicated rows
                    df.drop_duplicates(subset=df, inplace=True)
                    custom_df = pd.merge(custom_df,df[columns_to_merge],on=key_cols,how='inner')
                    columns_to_merge.pop()                                          #retrieve it for the next iteration
                    elements_found += 1
        
        if(elements_found == num_elements):
            break
    custom_df = custom_df.dropna(axis=1) # erase any column with NaN

    # Reorganise data (not strictly necessary, helpfull to debug)
    custom_df = custom_df.sort_values(by=key_cols)

    return custom_df

def df_from_vehicle(file_route, search_object, index='VIN', check_columns=['Id', 'Timestamp']):
    # Read and save the xlsx file in 'excel' variable
    excel = pd.ExcelFile(file_route)

    # Generate an empty dataframe to which all information will be stored
    custom_df = pd.DataFrame()
    custom_df[index] = None
    for element in check_columns:
        custom_df[element] = None
    custom_df.set_index(index, inplace=True)

    num_check_columns = len(check_columns)

    for sheet in excel.sheet_names:
        #if sheet!="Resumen":
        df = pd.read_excel(file_route, sheet_name=sheet, index_col=index)

        # Check if sheet has all key columns
        if all(col in df.columns for col in check_columns):
            if search_object in df.index:
                fila = df.loc[search_object]
                custom_df = pd.merge(custom_df, fila, on=check_columns, how='right')
                custom_df = custom_df.dropna(axis=1)

    return custom_df


def df_get_elements_tag(dataframe):
    # This vector returns a vector containing all names of all columns and the name
    # of the index in case there is one given a dataframe dataframe
    # 
    # INPUTS
    #   - dataframe:    dataframe to read
    # 
    # OUTPUTS
    #   - index:        name of the index, None if index is default
    #   - tags_vector:  vector containing all names of the dataframe

    # Get all columns (this will not include the index if there is one)
    tags_vector=[]

    for element in dataframe.columns:
        tags_vector.append(element)
    
    # Check if the index is the default: 0, 1, 2, 3, .... len(dataframe)-1
    if dataframe.index.equals(pd.RangeIndex(start=0, stop=len(dataframe), step=1)):
        index = None
    
    else:
        index = dataframe.index.name

    return index, tags_vector

def df_check_user_values(usr_dataframe):
    # Load the JSON file
    #INPUT
    #usr_dataframe: Un DataFrame de pandas que contiene los datos que se van a verificar. Los nombres de las columnas del DataFrame representan los elementos cuyos valores se verificarán.
    #   
    #OUTPUTS
    #   - result:Devuelve True si todos los valores están dentro de los rangos, y False si al menos un valor está fuera de los rangos o si hay elementos no encontrados en el archivo JSON.
    #elements_check: Un diccionario que contiene información detallada sobre la verificación de cada elemento. Para cada elemento, se almacenan los resultados de la verificación mínima (Check_min), la verificación máxima (Check_max).Este diccionario proporciona detalles sobre qué valores no cumplen con los criterios de verificación.
    
    

    with open('param_batery.json', 'r') as archivo:
        dict_param = json.load(archivo)

    result = True
    elements_check = {}

    for element in usr_dataframe.columns:
        min_value = dict_param[element]['minimum']
        max_value = dict_param[element]['maximum']
        
        check_min = True  # Initialize the verification variables
        check_max = True

        for value in usr_dataframe[element]:
            if value < min_value or value > max_value:
                check_min = False
                check_max = False

        elements_check[element] = {
            'Check_min': check_min,
            'Check_max': check_max,
            'Check': check_min or check_max
        }

        if not elements_check[element]['Check']:
            result = False

    return result, elements_check


"""********************     Parquet Files funcitons    ********************"""
    

def df_generate_month(file_path:str,type_name:str,year:int,month:int) -> pd.DataFrame:
    # Given a month and year, generates a dataframe containing all "data_to_save" information
    # which will be further (in another function) appended to the parquet file that contains
    # all months.
    # 
    # From the month and year, it will search the corresponding document in the folder df
    # 
    # IMPORTANT: The function saves the mean value of the columns to be saved
    # 
    # INPUT  
    #   - data_to_save:     columns to be "meaned" and saved in the new df
    #   - month, year:      integers to indicate the month and year of the dataframe
    # 
    # OUTPUT
    #   - -1 if no file matches the date
    #   - df_month

    """ Se suposa que els noms de les columnes son correctes i no s'ha de fer cap check """
    MONTHLY_DATA_TRIP = ['Mins','Max speed','Total (km)','Total energy (Wh)','Inv  min T (°C)']
    MONTHLY_DATA_CHARGE = ['Min temp I','Max temp I']

    df = pq.read_parquet(file_path)

    if type_name == 'trip':
        # Generate a new dataframe containing the necessary columns from both vectors    
        df_month = pd.DataFrame(columns = MONTHLY_DATA_TRIP)
        for column_tag in MONTHLY_DATA_TRIP:
            df_month[column_tag] = None   
        
        # Add to the dataframe all columns to be stored. Note that the value saved is
        # the average 
        mean_trip = df[MONTHLY_DATA_TRIP].mean()
        df_month[MONTHLY_DATA_TRIP] = mean_trip

    elif type_name == 'charge':
        # Generate a new dataframe containing the necessary columns from both vectors    
        df_month = pd.DataFrame(columns = MONTHLY_DATA_CHARGE)
        for column_tag in MONTHLY_DATA_CHARGE:
            df_month[column_tag] = None   
        
        # Add to the dataframe all columns to be stored. Note that the value saved is
        # the average 
        mean_trip = df[MONTHLY_DATA_CHARGE].mean()
        df_month[MONTHLY_DATA_CHARGE] = mean_trip
    
    else:
        return -1

    # Generate the date string and update df_month
    date_string = f'{year}-{month:02}'
    date = np.datetime64(date_string)
    df_month['Date'] = [date]

    return df_month

def df_generate_from_months(num_months:int) -> pd.DataFrame:
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
    MONTHS_FILE_PATH = 'df/critical_data.parquet'
    if not os.path.exists(MONTHS_FILE_PATH):
        return -1
    
    aux_df = pd.read_parquet(MONTHS_FILE_PATH)

    # Get the last "num_months" columns from the critical data file
    last_months_df = aux_df.tail(num_months)

    return last_months_df

def df_add_month_df(df_new,df_vector=None):
    # This function will add a new month's dataframe to a previously existing dataframe vector,
    # if none df_vector is passed, it is assumed that it is the first month dataframe to be created
    # and thus, a new dataframe vector is created
    # 
    # INPUT:
    #   - df_new: new month's dataframe
    #   - df_vector: preexsisting vector of month_df, if None, a new vector will be created
    # 
    # OUTPUT:
    #   - df_vector with df_new concatenated

    if df_vector == None:
        df_vector=[]
    df_vector.append(df_new)
    return df_vector

def df_append_data(df_new:pd.DataFrame, type_name:str) -> pd.DataFrame:

    timestamp_max=df_new['Timestamp'].max()
    date_max=datetime.datetime.utcfromtimestamp(timestamp_max)
    year_max=date_max.year
    month_max=date_max.month
    timestamp_min=df_new['Timestamp'].min()
    date_min=datetime.datetime.utcfromtimestamp(timestamp_min)
    year_min=date_min.year
    month_min=date_min.month

    
    #All the data are from the same month
    if month_min == month_max:
        filename=f'df/{year_min}_{month_min:02}_{type_name}.parquet'
        df_add_df_file(filename,df_new)
        return df_new
    
    #Data are from the different month
    if month_min != month_max:
        for index, row_data in df_new.iterrows():
            if row_data['Timestamp']> np.datetime64(f'{year_max}-{month_max:02}-01T00:00:00'):
                df_new_month=df_new_month.append(df_new.loc[index])
                df_new=df_new.drop(index)
        
        filename_new_month=f'df/{year_max}_{month_max:02}_{type_name}.parquet'
        df_add_df_file(filename_new_month,df_new_month)

        filename_last_month=f'df/{year_min}_{month_min:02}_{type_name}.parquet'
        df_add_df_file(filename_last_month,df_new)

        return df_new_month
    
def df_add_to_month(month_df) -> pd.DataFrame:
    # This function will either create critical_data.parquet and add this 
    # month's critical data or just add the critical data to an existing file
    # 
    # INPUT:
    #   - month_df: new month's dataframe
    # 
    # OUTPUT:
    #   - new_month_df: dataframe that has been stored into a .parquet file
    
    # Check if there's any months.parquet file, if not, return -1
    MONTHS_FILE_PATH = 'df/critical_data.parquet'
    if not os.path.exists(MONTHS_FILE_PATH):
        new_month_df = df_generate_month()
    
    new_month_df = pd.read_parquet(MONTHS_FILE_PATH)
    
    return new_month_df

def df_add_df_file(file_path:str,df_new:pd.DataFrame) -> pd.DataFrame:
    # This function will generate and modify a new .parquet given a filename
    # and dataframe to ba added.
    # 
    # This function has to be used to modify data related to 'run' and 'charge'
    # files. To do so with the monthly critical data, use df_add_to_month_df()
    # 
    # INPUT:
    #   - file_path
    #   - df_new: dataframe containing new data to be stored
    # 
    # OUTPUT:
    #   - Resulting dataframe
    
    # If file exists
    if os.path.exist(file_path):
        # Read and add new data
        df_exist = pd.read_parquet(file_path)
        df_final = pd.concat([df_exist,df_new])
        # Overwrite file
        table = pa.Table.from_pandas(df_final)
        pq.write_table(table,file_path)
       
        return df_final

    # If file does not exist, generate a new one from df_new
    table = pa.Table.from_pandas(df_new)
    pq.write_table(table,file_path)
    
    return df_new


def df_get_columns_tag(dataframe):

    tag_vector = []
    for columna in dataframe.columns:
        tag_vector.append(columna)

    return tag_vector