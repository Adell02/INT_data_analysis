# INT_data_analysis


This repository conatins all files used to store, filter, analyse and display Ray's data. To do so, functions have been divided into different files: `plots_generation.py`, `dataframe_treatment.py`, `dataframe_generation.py` and `data_analysis.py`.

<h2>Plots Generation</h2>

The file `plots_generation.py` contains all functions regarding plot generation, next there are the basic plots that can be used. 

All functions return a `plotly` figure. Otherwise, it will be noted beneath.

Note that all functions that are usually accessed start with `generate_` to easily find them when programming.

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Multi Histogram</b></summary>

## Description

The `multi_histogram` function takes a DataFrame and a list of column names as input to create a multiple histogram plot. Each column of the DataFrame is represented as a histogram on the plot, allowing for a visual comparison of different datasets in a single visualization.

## Header & Parameters
`generate_multi_histogram(dataframe,elements,units='',start=-200,end=200,step=10, title='Unnamed distribution')`
- `dataframe`: The DataFrame containing the data to be represented in the histograms.
- `elements`: A list of column names from the DataFrame. Each column will be represented as a histogram on the plot.
- `units`: Optional string representing the units of the variable on the x-axis.
- `start`, `end`, `step`: Optional parameters controlling the configuration of the x-axis and histogram bins. All have preset values and don't need to be taken into account.
- `title`: Title of the plot. "Unnamed distribution" by default.

</details>


<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Pie Chart</b></summary>


## Description

The `pie_chart` function is an effective tool for creating pie chart graphics. This function can generate subplots containing multiple pie charts if it is necessary to segregate certain information into different categories but visualize it together.

## Header & Parameters
`generate_pie_chart(dataframe,elements,title='Unnamed pie chart)`
- `dataframe`: The DataFrame containing the data for the pie chart.
- `elements`: An array of arrays (each position contains the names of a single pie chart).
- `title`: Title of the chart.

</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Scatter Plot</b></summary>

## Description
The scatter plot is a most used function in data analysis. The user can introduce different elements to be plotted and can decide whether to display a regression line using Ordinary Least Squares (OLS) regression. This utility is particularly useful when visualizing trends in data.

## Header & Parameters
`generate_scatter_plot(dataframe,element_x,elements_y,title:"Unnamed scatter plot,reg_line=True)`
- `dataframe`: The DataFrame containing the data.
- `element_x`: The element to be displayed on the x-axis.
- `elements_y`: A list of elements for which traces will be displayed on the y-axis.
- `title`: Title of the plot. 
- `reg_line`: "True" by default.


</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Scatter Plot User</b></summary>

## Description

The `generate_scatter_plot_user` function generates a scatter plot given a DataFrame, a specified user ID (`key_user`), an x-axis element (`element_x`), and a vector of y-axis elements (`elements_y`). The function allows for customization with an optional title and the ability to integrate regression lines. If a specific user's data is requested (`user_reg_line=True`), an individualized trendline is added to the plot.

Also, if no user is specified or it is not found in the dataframe given, the function will call a "regular" scatter plot to be generated.

## Header & Parameters
`generate_scatter_plot_user(dataframe,key_user,element_x,elements_y,title="Unnamed Scatter Plot",user_reg_line=False,reg_line=False)`
- `dataframe`: The DataFrame containing all the data.
- `key_user`: ID of the user for whom data is needed.
- `element_x`: The x-axis data.
- `elements_y`: A vector containing all the different data sources to be plotted.
- `title`: Title of the graph (default is "Unnamed Scatter Plot").
- `user_reg_line`: Boolean indicating if an individualized regression line for the user is desired (default is False).
- `reg_line`: Boolean indicating if a general regression line for the entire dataset is desired (default is False).
</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Line Chart</b></summary>

## Description

Although not used in further analysis, a line chart can be generated given a `dataframe` and specifying which data must be plotted (`elements_y` and `element_x`).

## Header & Parameters
`generate_line_chart(dataframe,element_x,elements_y,title='Unnamed Line Chart')`
- `dataframe`: The DataFrame containing all the data.
- `element_x`: The x-axis data.
- `elements_y`: A vector containing all the different data sources to be plotted.
- `title`: Title of the graph (default is "Unnamed Line Chart").

</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Bar Chart</b></summary>

## Description
Bar charts can be plotted if needed using `generate_bar_chart`. These graphs are useful when displaying a quantity over a quantised variable, such as time or a numeric sets.

## Header & Parameters
`generate_bar_chart(dataframe,element_x,elements_y,title='Unnamed Bar Chart')`
- `dataframe`: The DataFrame containing all the data.
- `element_x`: The x-axis data.
- `elements_y`: A vector containing all the different data sources to be plotted.
- `title`: Title of the graph (default is "Unnamed Bar Chart").
</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Response Surface</b></summary>

## Description
A 3D graph can be generated using this function. Typically, these graphics are useful when trying to dig further into the correlation between several variables when it is known that a parameter can have dependence over more than one variable. It can help to deepen the analysis of certain parameters.

## Header & Parameters
`generate_response_surface(dataframe,element_x,element_y,element_z,title='Unnamed Response Surface')`
- `dataframe`: The DataFrame containing all the data.
- `element_x`: The x-axis data.
- `element_y`: The y-axis data.
-`element_z`: The z-axis data.
- `title`: Title of the graph (default is "Unnamed Response Surface").

## Caution
Bear in mind that, in order to generate a response surface, it generates a interpolated grid from the parameters passed to the functions. It is crucial that no aberrant measures are contained in either of the elements passed. User be advised.
</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Box Plot</b></summary>

## Description
Box plots are used when showing the distribution of data points across a selected measure. These charts display ranges within variables measured. This includes the outliers, the median, the mode, and where the majority of the data points lie in the “box”.

## Header & Parameters
`generate_box_plot(dataframe,elements,title='Unamed Box Plot')`
- `dataframe`: The DataFrame containing all the data.
- `element_x`: The x-axis data.
- `title`: Title of the graph (default is "Unnamed Response Surface").

</details>
<br>
<h2>Datframe Treatment</h2>

This file contains all functions necessary to assure that the data stored in a dataframe is correct,
contains all information and it is normalised so that future analyses can be done.

The main function is `df_filter_data`, which will return a filtered and depurated dataframe, the rest of
functions are auxiliary and do not need to be particularily used for external purposes.

`df_get_colum_tags_dictionary` returns a vector containing all the names of the columns given the type_name
(`trip` or `charge`). It is useful if it is needed to list all the variables contained in the dataframe or to check whether one particular variable is within the dataframe.

Note that all functions related to managing dataframes start with `df_` to find them easily when programming.

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Data filtering</b></summary>

## Description
This funciton: `df_filter_data`, given a raw dataframe, will do as follows:
1)  Update the column names (in case the dataframe comes from an xlsx file withdifferent column_tags).
2)  Add secondary columns, which are product of primary columns.
3)  Sort columns, so that the order is the same as in the param_battery.json file.
4)  Verify values, in case there are any data out of acceptable bounds.
5)  Apply the resolution of each column.

Note: It is of upmost importance that this function has to be executed before appending a dataframe to a definitive .parquet to ensure that all data stored has been checked.

## Header & Parameters
`df_filter_data(df:pd.DataFrame, type_name:str)`
- `dataframe`: The DataFrame containing the data to be represented in the histograms.
- `type_name`: To indicate if the dataframe introduced contains `trip`-related or `charge`-related data.
</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Generate df from elements Function</b></summary>

## Description:
The `generate_df_from_elements` function processes an Excel file (`file_route`), using an index column (`index`), a specified number of rows for the resulting dataframe (`rows`), designated key columns for vehicle identification (`key_cols`), and a list of elements (`elements`). This function reads the Excel file, searches for the specified key columns in its sheets, and constructs a custom dataframe (`custom_df`) containing the requested elements.

## Input Parameters:
- `file_route`: Relative path to the Excel file.
- `index`: Name of the column to serve as an index.
- `rows`: Desired number of rows for the resulting dataframe.
- `key_cols`: Names of the columns used to identifying each vehicle in the dataframe.
- `elements`: List of elements to be included in the custom dataframe.

## Output:
The generated dataframe (`custom_df`) with the designated key columns.

## Example Usage:
```python
file_route = "file_path.xlsx"
index = "ID"
rows = 100
key_cols = ["ID", "Make", "Model"]
elements = ["Price", "Mileage", "Year"]

result_df = generate_df_from_elements(file_route, index, rows, key_cols, elements)
print(result_df)
```
This code is essentially a utilization example of the `generate_df_from_elements` function. It sets up parameters such as the file path, index column, desired number of rows, key columns, and elements to be included. Then, it calls the function with these parameters and prints the resulting dataframe (`result_df`). The purpose is to showcase how users can customize the function's inputs based on their specific dataset and requirements.

</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Generate df from elements Function</b></summary>

## Description:
The `generate_df_from_vehicle` function is designed to extract and store specific information about a vehicle (identified by the search object) from an Excel file. It utilizes key columns to check and organize the data into a custom dataframe.

## Parameters:
- `file_route`: Relative path to the Excel file.
- `search_object`: Specific identifier of the vehicle to be searched for in the sheets of the Excel file.
- `index`: Column used as the index in the resulting dataframe ("VIN" by default).
- `check_columns`: List of columns used as keys to merge data into the custom dataframe (['Id', 'Timestamp'] by default).

## Output:
- `custom_df`: Resulting dataframe containing information related to the specific vehicle.

## Example Usage:
```python
file_route = "file_path.xlsx"
search_object = "ABC123"
index = "VIN"
check_columns = ["Id", "Timestamp"]

result_df = generate_df_from_vehicle(file_route, search_object, index, check_columns)
print(result_df)
```

</details>
