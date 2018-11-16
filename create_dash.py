import dash
import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from retrieve_data import assemble_data
import plotly.graph_objs as go
from plotly import tools
import pandas as pd
import numpy as np
import urllib
from utils import constants, tokens
import os


def create_dash_app(df_w, df_g, df_r):
    app = dash.Dash('Travel Times')

    travel_times_dir = constants.travel_times_dir
    test_dir = os.path.join(travel_times_dir, 'maps/test.html')

    mapbox_access_token = tokens.mapbox_token

    app.layout = html.Div([
        # This component generates a <h1></h1> HTML element in your application
        html.H1('Tiempos de viaje'),
        # The dcc describe higher-level components that are interactive
        html.Label('Selecciona la ruta'),
        dcc.Dropdown(
            id='query-routes',
            options=[{'label': i, 'value': i}
                     for i in df_w['name'].unique()],
            # This is the default value
            value= df_w.iloc[0,0] #This is a string, ok!
        ),
        html.Label('Selecciona la fecha'),
        dcc.Dropdown(
            id='query-dates',
            options=[{'label': i.strftime("%d-%m-%Y"), 'value': i}
                     for i in df_w['date'].unique()],
            value = df_w.loc[:,'date'].min()
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

    def filter_data(df, query_route, query_date):
        sd2_d = dt.datetime.strptime(query_date, '%Y-%m-%d').date()
        dff = df.loc[(df['name'] == query_route)&(df['date'] == sd2_d),['updatetime','time/length']]
        return dff
        

    @app.callback(Output('travel-times-graph', 'figure'), [Input('query-routes', 'value'), Input('query-dates', 'value')])
    def update_graph(query_route, query_date):
        # Be aware that the query_route and query_date are (always) strings!

        fig = tools.make_subplots(rows=1, cols=1, shared_xaxes = True, shared_yaxes = True)

        def temporal_transform(x):
            #This is weird
            x = x - pd.Timedelta('3 hours')
            return x

        def create_traces(df, source):
            dff = filter_data(df,query_route,query_date)
            trace = go.Scatter(
                x = dff.loc[:,'updatetime'].apply(temporal_transform),
                y = dff.loc[:,'time/length'],
                mode='lines+markers',
                name = query_date + " " + source)
            return trace
       
        trace_w = create_traces(df_w, "waze")        
        trace_g = create_traces(df_g, "gps")

        fig.append_trace(trace_w,1,1)        
        fig.append_trace(trace_g,1,1)
        
        max_w = 0
        if trace_w.y.size>0:
            max_w = max(trace_w.y)
        
        max_g = 0
        if trace_g.y.size > 0:
            max_g = max(trace_g.y)
        
        max_y_value = max(max_w,max_g) + 25

        #Don't like this. Consider to refactor it.
        fig['data'][1]['marker']['symbol'] = 'triangle-down'
        fig.layout.yaxis.update({'title': 'Tiempo de viaje [s/km]','dtick':50, 'range': [0,max_y_value]})

        return fig

    @app.callback(Output('download-link', 'href'),[Input('query-routes', 'value'), Input('query-dates', 'value')])
    def update_download_link(query_route, query_date):
        dff_w = filter_data(df_w, query_route, query_date)
        dff_g = filter_data(df_g, query_route, query_date)
        dff = dff_w.merge(dff_g, on='updatetime', how='left', suffixes=('_waze','_gps'))
        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
        return csv_string

    @app.callback(Output('map-routes', 'figure'),[Input('query-routes', 'value')])
    def update_map(query_route):

        def changing_line(x):
            x = x.replace("[","")
            x = x.replace("]","")
            x = x.replace("(","")
            x = x.replace(")","")
            return pd.Series(x.split(","))
                    
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

    return app

if __name__ == '__main__':
    [grouped_df_tt_w, grouped_df_tt_g, df_r_w] = assemble_data('13.11.2018', '24.10.2018', '25.10.2018')
    app = create_dash_app(grouped_df_tt_w, grouped_df_tt_g, df_r_w)
    app.run_server(host = '0.0.0.0', port = 8080)
