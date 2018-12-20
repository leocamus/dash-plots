import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import datetime as dt
import urllib

from plotly import tools
from dash.dependencies import Input, Output
from utils import constants, tokens
from retrieve_data import assemble_data

[df_tt_w, df_tt_g, df_r_w] = assemble_data('17.12.2018', '24.10.2018', '25.10.2018')

def temporal_transform(x):
    #This is weird
    x = x - pd.Timedelta('3 hours')
    return x

def changing_line(x):
    x = x.replace("[","")
    x = x.replace("]","")
    x = x.replace("(","")
    x = x.replace(")","")
    return pd.Series(x.split(","))

def filter_data(df, query_route, query_date):
    query_date_d = dt.datetime.strptime(query_date, '%Y-%m-%d').date()
    dff = df.loc[(df['name'] == query_route)&(df['date'] == query_date_d),['updatetime','time/length[s/km]','length/time[km/h]']]
    return dff

def create_traces(df, query_route, query_date, source):
    dff = filter_data(df,query_route,query_date)
    x = dff.loc[:,'updatetime'].apply(temporal_transform)
    trace_y1 = go.Scatter(
        x = x,
        y = dff.loc[:,'time/length[s/km]'],
        mode='lines+markers',
        name = query_date + " " + source + " - [s/km]")

    trace_y2 = go.Scatter(
        x = x,
        y = dff.loc[:,'length/time[km/h]'],
        mode='lines+markers',
        name = query_date + " " + source + " - [km/h]",
        xaxis = "x1", 
        yaxis = "y2")

    return trace_y1, trace_y2

app = dash.Dash('Travel Times')
mapbox_access_token = tokens.get_mapbox_token()

app.layout = html.Div([
    # This component generates a <h1></h1> HTML element in your application
    html.H1('Tiempos de viaje'),
    # The dcc describe higher-level components that are interactive
    html.Label('Selecciona la ruta'),
    dcc.Dropdown(
        id='query-routes',
        options=[{'label': i, 'value': i}
                    for i in df_tt_w['name'].unique()],
        # This is the default value
        value= df_tt_w.iloc[0,0] #This is a string, ok!
    ),
    html.Label('Selecciona la fecha'),
    dcc.Dropdown(
        id='query-dates',
        options=[{'label': i.strftime("%d-%m-%Y"), 'value': i}
                    for i in df_tt_w['date'].unique()],
        value = df_tt_w.loc[:,'date'].min()
    ),
    html.A(
        'Descargar Datos',
        id='download-link',
        download="rawdata.csv",
        href="",
        target="_blank"
    ),
    dcc.Graph(
        id='map-routes'
    ),
    dcc.Graph(
        id='travel-times-graph'
    )
])

@app.callback(Output('travel-times-graph', 'figure'), [Input('query-routes', 'value'), Input('query-dates', 'value')])
def update_graph(query_route, query_date):
    fig = tools.make_subplots(rows=1, cols=1, shared_xaxes = True, shared_yaxes = True)
    [trace_w_y1,trace_w_y2] = create_traces(df_tt_w,query_route, query_date, "waze")  
    [trace_g_y1,trace_g_y2] = create_traces(df_tt_g,query_route, query_date, "gps")

    fig.append_trace(trace_w_y1,1,1)#0 - WAZE Y1
    fig.append_trace(trace_w_y2,1,1)#1 - WAZE Y2
    fig.append_trace(trace_g_y1,1,1)#2 - GPS Y1
    fig.append_trace(trace_g_y2,1,1)#3 - GPS Y2
    
    max_w_y1 = 0
    if trace_w_y1.y.size>0:
        max_w_y1 = max(trace_w_y1.y)
    
    max_g_y1 = 0
    if trace_g_y1.y.size > 0:
        max_g_y1 = max(trace_g_y1.y)
    
    max_y1_value = max(max_w_y1,max_g_y1) + 25

    #Don't like this. Consider to refactor it.
    fig.data[2]['marker']['symbol'] = 'triangle-down'
    fig.data[3]['marker']['symbol'] = 'triangle-down'

    fig.data[1].update(yaxis = 'y2')
    fig.data[3].update(yaxis = 'y2')

    fig.layout.update({'yaxis{}'.format(1): {'anchor':'x', 'side':'left', 'title': 'Tiempo de viaje [s/km]','dtick':50, 'range': [0,max_y1_value]}})
    fig.layout.update({'yaxis{}'.format(2): {'anchor':'x', 'side':'right', 'title': 'Velocidad [km/h]', 'overlaying': 'y'}})

    return fig

@app.callback(Output('download-link', 'href'),[Input('query-routes', 'value'), Input('query-dates', 'value')])
def update_download_link(query_route, query_date):
    dff_w = filter_data(df_tt_w, query_route, query_date)
    dff_g = filter_data(df_tt_g, query_route, query_date)
    dff = dff_w.merge(dff_g, on='updatetime', how='left', suffixes=('_waze','_gps'))
    csv_string = dff.to_csv(index=False, encoding='utf-8')
    csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
    return csv_string

@app.callback(Output('map-routes', 'figure'),[Input('query-routes', 'value')])
def update_map(query_route):
    line = df_r_w.loc[df_r_w['name']==query_route, 'line'].apply(changing_line)

    line.columns = [np.arange(len(line.columns)) % 2, np.arange(len(line.columns)) // 2]
    line = line.stack().reset_index(drop=True)
    line.columns = ['lon','lat']

    lat = line.loc[:,'lat'].tolist()
    lon = line.loc[:,'lon'].tolist()

    data=[
        go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='markers',
            marker=dict(size=13)
            )
        ]

    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(lat=float(lat[0]),lon=float(lon[0])),
        pitch=0,
        zoom=11
        )
    )
    
    fig = dict(data = data, layout=layout)
    return fig

if __name__ == '__main__':
    app.run_server(port = 80)
