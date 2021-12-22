# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)
def getDropdownLabels():
    sites = spacex_df["Launch Site"].unique().tolist()
    labels = [{'label': 'All Sites', 'value': 'All'}]
    for s in sites:
        labels.append({'label': s, 'value':s})
    return labels
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=getDropdownLabels(), value='All', placeholder='Select a launch site',
                                searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0, max=10000, step=1000,
                                marks={0: '0', 2500: '2500', '5000':5000, '7500':7500,'10000':10000},
                                value=[0,10000]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site=='All':
        fig = px.pie(spacex_df, values='class', names='Launch Site', title='Total successful launches by site')
        return fig
    else:
        filtered = spacex_df[spacex_df['Launch Site'] == entered_site]
        summaryDf = filtered.groupby('class', as_index=False).count()
        fig = px.pie(summaryDf, values='Launch Site', names='class', title='Fraction successful launches for site %s'%entered_site)
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
[Input(component_id='site-dropdown', component_property='value'),Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(entered_site, payload_range):
    mask1 = spacex_df['Payload Mass (kg)'] >= payload_range[0]
    mask2 = spacex_df['Payload Mass (kg)'] <= payload_range[1]
    filteredDf = spacex_df[mask1 & mask2]
    if entered_site == 'All':
        fig = px.scatter(data_frame=filteredDf, x='Payload Mass (kg)', y='class', color='Booster Version Category', 
        title='Correlation between payload and success for all sites')
    else:
        data = filteredDf[filteredDf['Launch Site'] == entered_site]
        fig = px.scatter(data_frame=data, x='Payload Mass (kg)', y='class', color='Booster Version Category', 
        title='Correlation between payload and success for site %s'%entered_site)
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
