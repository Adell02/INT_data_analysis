# INT_data_analysis
Data analysis for INT project
<h1>Function Descriptions</h1>
<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Multi Histogram Function</b></summary>


## Description

The `multi_histogram` function takes a DataFrame and a list of column names as input to create a multiple histogram plot. Each column of the DataFrame is represented as a histogram on the plot, allowing for a visual comparison of different datasets in a single visualization.

## Parameters

- `dataframe`: The DataFrame containing the data to be represented in the histograms.
- `elements`: A list of column names from the DataFrame. Each column will be represented as a histogram on the plot.
- `units`: Optional string representing the units of the variable on the x-axis.
- `start`, `end`, `step`: Optional parameters controlling the configuration of the x-axis and histogram bins.
- `title`: Title of the plot.

## Output

The function returns a `go.Figure` object that can be displayed or saved as needed.

## Example Usage

```python
import pandas as pd
import plotly.graph_objects as go

def multi_histogram(dataframe, elements, units='', start=-200, end=200, step=10, title='Unnamed distribution'):
    # ... (Paste the function code here)

# Create an example DataFrame
data = {'A': [1, 2, 2, 3, 3, 3, 4, 4, 4, 4],
        'B': [2, 2, 3, 3, 3, 4, 4, 4, 4, 5],
        'C': [3, 3, 3, 4, 4, 4, 4, 5, 5, 5]}
df = pd.DataFrame(data)

# Use the multi_histogram function to visualize column distributions
fig = multi_histogram(df, elements=['A', 'B', 'C'], units='Value', title='Distribution Comparison')
fig.show()
```


This example demonstrates the use of the `multi_histogram` function, which creates multi-histogram plots with Plotly. The function takes a DataFrame and a list of column names, allowing users to visualize the distributions of specified columns. The example uses a Pandas DataFrame with sample data in columns 'A', 'B', and 'C' and calls the function to generate a Plotly figure. Users can customize parameters such as units, axis range, and title for tailored visualizations.

</details>


<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Pie Chart Function</b></summary>


## Description

The `pie_chart` function is an effective tool for creating pie chart graphics. This function can generate subplots containing multiple pie charts if it is necessary to segregate certain information into different categories but visualize it together.

## Parameters

- `dataframe`: The DataFrame containing the data for the pie chart.
- `elements`: An array of arrays (each position contains the names of a single pie chart).
- `title`: Title of the chart.

## Output

The function returns a pie chart figure object.

## Example Usage

```python
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def pie_chart(dataframe, elements, title='Unnamed pie chart'):

    num_elements = len(elements)

    fig = make_subplots(
        rows=1,
        cols=num_elements,
        specs=[[{'type':'domain'}, {'type':'domain'}]]
    )

    for i in range(num_elements):
        fig.add_trace(generate_go_pie(dataframe, elements[i], ''), 1, i+1)

    fig.update_traces(hole=.4, hoverinfo="label+percent+name")

    fig.update_layout(title_text=title)

    return fig
```
This example code uses the pie_chart function to create a pie chart from a DataFrame and a list of elements. You can customize the parameters according to your specific needs.
</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Trace Trendline Function</b></summary>

## Description

The `trace_trendline` function efficiently generates trendlines using Ordinary Least Squares (OLS) regression. This utility is particularly useful when visualizing trends in data by providing regression lines for a selected x-axis element and multiple y-axis elements. The function is designed to accommodate diverse datasets and supports customization of trendline aesthetics.

## Parameters
- `dataframe`: The DataFrame containing the data for regression analysis.
- `element_x`: The element to be displayed on the x-axis.
- `elements_y`: A list of elements for which trendlines will be displayed on the y-axis.
- `title`: Title of the trendlines (default is 'Trendline').

## Output
The function returns a vector of Plotly traces representing the trendlines generated for each element specified in `elements_y`. Each trace corresponds to a trendline, allowing for easy integration into a Plotly figure.

## Example Usage
```python
import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go

# Define DataFrame and elements
data = {'X': [1, 2, 3, 4, 5],
        'Y1': [2, 3, 4, 3, 5],
        'Y2': [1, 2, 2, 3, 4]}
df = pd.DataFrame(data)

# Use the trace_trendline function to generate trendlines for Y1 and Y2 with X as the x-axis
trendlines = trace_trendline(df, element_x='X', elements_y=['Y1', 'Y2'], title='Regression Trends')

# Incorporate trendlines into a Plotly figure
fig = go.Figure(trendlines)
fig.show()
```
This code snippet demonstrates the application of the `trace_trendline` function to visualize regression trends for `Y1` and `Y2` against `X`. Users can modify the function parameters for different datasets and customization requirements.

</details>

<details>
<summary style="color: #ADD8E6;"><b style="font-size: 18px;">Generate Scatter Plot User Function</b></summary>

## Description

The `generate_scatter_plot_user` function generates a scatter plot given a DataFrame, a specified user ID (`key_user`), an x-axis element (`element_x`), and a vector of y-axis elements (`elements_y`). The function allows for customization with an optional title and the ability to integrate regression lines. If a specific user's data is requested (`user_reg_line=True`), an individualized trendline is added to the plot.

## Parameters
- `dataframe`: The DataFrame containing all the data.
- `key_user`: ID of the user for whom data is needed.
- `element_x`: The x-axis data.
- `elements_y`: A vector containing all the different data sources to be plotted.
- `title`: Title of the graph (default is "Unnamed Scatter Plot").
- `user_reg_line`: Boolean indicating if an individualized regression line for the user is desired (default is False).
- `reg_line`: Boolean indicating if a general regression line for the entire dataset is desired (default is False).

## Output
If successful, the function returns a Plotly figure. If an error occurs or the user is not found in the DataFrame, the function returns None. The returned Plotly figure comprises a set of traces representing the trendlines generated for each element specified in `elements_y`. Each trace corresponds to a trendline, facilitating seamless integration into a Plotly figure.

## Example Usage
```python
import pandas as pd
import plotly.graph_objects as go

# Define DataFrame and elements
data = {'User_ID': [1, 1, 2, 2, 3, 3],
        'Age': [25, 30, 22, 28, 35, 40],
        'Income': [50000, 60000, 45000, 55000, 70000, 80000],
        'Spending': [100, 120, 80, 110, 150, 160]}
df = pd.DataFrame(data)

# Generate a scatter plot for User ID 2, plotting 'Age' on the x-axis and 'Income' and 'Spending' on the y-axis
fig = generate_scatter_plot_user(df, key_user=2, element_x='Age', elements_y=['Income', 'Spending'], title='User Spending Habits')
fig.show()
```
This example demonstrates how to use the `generate_scatter_plot_user` function to create a scatter plot for a specific user ( **User ID 2** ) and visualize their spending habits. Users can customize the parameters based on their specific dataset and analysis requirements.
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
