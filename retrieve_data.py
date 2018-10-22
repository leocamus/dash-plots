import os
import pandas as pd
from utils import constants

def query_database(freq):
    #The connection should be open all the time.
    #Data is retrieved with some frequency.
    #Pandas dataframe is built and manipulated to build the Dash app
    pass

def read_data():
    #Should be replaced for a connection to a ddbb'''
    travel_times_dir = constants.travel_times_dir
    travel_times = os.path.join(travel_times_dir, 'tiempoviaje-12-10-2018.csv')
    routes = os.path.join(travel_times_dir, 'ruta-12-10-2018.csv')

    df_travel_times = pd.read_csv(travel_times, sep=',', encoding='latin-1', parse_dates = ['tvjfechaextraccion'])
    df_travel_times['fecha_extraccion'] = df_travel_times['tvjfechaextraccion'].dt.date
    df_travel_times['tiempo_extraccion'] = df_travel_times['tvjfechaextraccion'].dt.time

    columns_datetime = ['rtahorariocomienzo','rtahorariofinal','rtafechacreacion']
    df_routes = pd.read_csv(routes,sep=';', encoding='latin-1', parse_dates = columns_datetime)
    df_routes['rtahorariocomienzo'] = df_routes['rtahorariocomienzo'].dt.time
    df_routes['rtahorariofinal'] = df_routes['rtahorariofinal'].dt.time

    df_travel_times = df_travel_times.merge(df_routes[['rtaid','length','rtanombre']], on='rtaid', how='left')
    df_travel_times['tvjtiempo/length'] = df_travel_times['tvjtiempo'] / df_travel_times['length']

    return df_travel_times, df_routes

