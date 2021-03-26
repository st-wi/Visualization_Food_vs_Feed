import pandas as pd
import matplotlib.pyplot as plt
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__)
#load data
data = pd.read_csv("fao.csv")

# extract data and drop unused data
data = data.drop(columns = ['Area Abbreviation', 'Area Code', 'Item Code','Element Code','latitude', 'longitude'])
data = data.drop(data.loc[:,'Y1961':'Y1992'], axis=1)
data['Total'] = data.iloc[:,4:].sum(axis=1) 

data_group = data.groupby(['Area','Element']).sum()
# rename columns
data_group.rename(columns=lambda x:x[1:] if x != 'Total' else x, inplace = True)
data_group = data_group.reset_index()
# years
years = list(range(1993,2014))
years.reverse()

#countries
countries = list(set(data_group['Area']))
countries.sort()

#app layout
app.layout = html.Div([
    html.H1("Food vs Feed (1993-2013) Dashboard", style={'text-align': 'center'}),
    html.H3("Data from fao.org", style={'text-align':'center'}),

    dcc.Dropdown(
        id='select_year',
        value='2013',
        options = [{'label': i, 'value':i} for i in years],
        placeholder = 'Select a year', 
        style={'width':'40%'}, 
        multi=False
        ),
    dcc.Dropdown(
        id='select_country',
        value='United States of America',
        options = [{'label':j, 'value':j} for j in countries],
        placeholder = 'Select a countries', 
        style={'width':'50%'}, 
        multi=False
        ),
        
    dcc.Graph(id='pie-chart'),
])

# connect graph with component
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('select_year', 'value'), Input('select_country','value')]
)
def generate_chart(select_year, select_country):
    labels = ['Feed', 'Food']
    # get index of the country
    i, j = data_group[data_group['Area'] ==select_country].index.values
    # get year of that country
    feed = data_group.get(select_year)[i]
    food = data_group.get(select_year)[j]
    size =  [feed, food]
    df = pd.DataFrame({'Labels':labels, 'Size':size})
    fig = px.pie(df, values=size, names=labels,title="Percentage of Food and Feed in {} in {}".format(select_country, select_year))
    return fig 


if __name__ == '__main__':
    app.run_server(debug=True)
