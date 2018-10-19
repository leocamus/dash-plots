import os
import dash
import pandas as pd
import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
from utils import constants
from dash.dependencies import Input, Output

def read_data():
    waze_dir = constants.waze_dir
    travel_times = os.path.join(waze_dir, 'tiempoviaje-12-10-2018.csv')
    routes = os.path.join(waze_dir, 'ruta-12-10-2018.csv')

    df_travel_times = pd.read_csv(travel_times, sep=',', encoding='latin-1', parse_dates = ['tvjfechaextraccion'])
    df_travel_times['fecha_extraccion'] = df_travel_times['tvjfechaextraccion'].dt.date
    df_travel_times['tiempo_extraccion'] = df_travel_times['tvjfechaextraccion'].dt.time

    columns_datetime = ['rtahorariocomienzo','rtahorariofinal','rtafechacreacion']
    df_routes = pd.read_csv(routes,sep=';', encoding='latin-1', parse_dates = columns_datetime)
    df_routes['rtahorariocomienzo'] = df_routes['rtahorariocomienzo'].dt.time
    df_routes['rtahorariofinal'] = df_routes['rtahorariofinal'].dt.time

    df_travel_times = df_travel_times.merge(df_routes[['rtaid','length']], on='rtaid', how='left')
    df_travel_times['tvjtiempo/length'] = df_travel_times['tvjtiempo'] / df_travel_times['length']

    return df_travel_times, df_routes


def create_dash_app(df):
    app = dash.Dash()
    app.layout = html.Div(children=[
        html.H1(children='Waze Travel Times'), #This component generates a <h1></h1> HTML element in your application
        dcc.Dropdown(
            id = 'query-dates',
            options=[{'label': i.strftime("%d-%m-%Y"), 'value': i} for i in df['fecha_extraccion'].unique()],
            value='MTL'
        ),
        #The dcc describe higher-level components that are interactive 
        dcc.Graph(
            id='waze-graph'
        )
    ])

    @app.callback(Output('waze-graph', 'figure'), [Input('query-dates', 'value')])
    def update_graph(selected_dropdown_value):
        #Be aware that the selected_dropdown_value is a string!
        selected_dropdown_value = dt.datetime.strptime(selected_dropdown_value, '%Y-%m-%d').date()
        x_70 = df.loc[(df['rtaid']==70)&(df['fecha_extraccion']==selected_dropdown_value),'tiempo_extraccion']

        y_70 = df.loc[(df['rtaid']==70)&(df['fecha_extraccion']==selected_dropdown_value),'tvjtiempo/length']
        y_72 = df.loc[(df['rtaid']==72)&(df['fecha_extraccion']==selected_dropdown_value),'tvjtiempo/length']
        
        return {
            'data': [{'x': x_70,'y': y_70}, {'x': x_70,'y': y_72}]
        }

    return app


if __name__ == '__main__':
    df_travel_times = read_data()[0]
    app = create_dash_app(df_travel_times)
    app.run_server()