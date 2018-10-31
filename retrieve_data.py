import os
import pandas as pd
import datetime as dt
from utils import constants


def query_database(freq):
    # The connection should be open all the time.
    # Data is retrieved with some frequency.
    # Pandas dataframe is built and manipulated to build the Dash app
    pass


def read_waze_data(extraction_date):
    # Should be replaced for a connection to a ddbb
    waze_dir = constants.waze_travel_times_dir

    travel_times = os.path.join(waze_dir, 'travel_times_' + extraction_date + '.csv')    
    routes = os.path.join(waze_dir, 'routes_' + extraction_date + '.csv')

    df_tt = pd.read_csv(travel_times, sep=';', encoding='latin-1', parse_dates=['updatetime'],
                        date_parser=lambda x: pd.to_datetime(x.rpartition('-')[0]))

    df_r = pd.read_csv(routes, sep=';', encoding='latin-1', parse_dates=['start_date'])

    return df_tt, df_r

def read_gps_data(*args):
    # arg are dates as strings with a dd.mm.yyyy format.
    gps_dir = constants.gps_travel_times_dir
    frames = []

    for arg in args:
        travel_times = os.path.join(gps_dir, 'velocidadesIrPO' + arg.split(".")[0] + '.xlsx')
        df_tt = pd.read_excel(travel_times, encoding='latin-1') #"periodo" is parsed as datetime.time object.
        frames.append(df_tt)

    df_tt = pd.concat(frames)
    df_tt.reset_index(inplace=True)
    df_tt = df_tt.rename(columns={'tiempo (s/km)': 'time/length'})

    def names_compatibility(x):
        if x==8:
            return 'TramoIraPO2'
        elif x==9:
            return 'TramoIraPO3'
        elif x==10:
            return 'TramoIraPO4'

    def dates_compatibility(x, month=10, year=2018):
        date = dt.date(year,month,int(x[-2:]))
        return date
    
    def produce_datetime(date,time):
        datetime = dt.datetime(date.year,date.month,date.day,time.hour,time.minute,time.second)
        return datetime


    df_tt['name'] = df_tt['itramo'].apply(names_compatibility)
    df_tt['date'] = df_tt.apply(lambda x: dates_compatibility(x['servicio']), axis=1)
    df_tt['updatetime'] = df_tt.apply(lambda x: produce_datetime(x['date'], x['periodo']), axis=1)
    
    return df_tt


def process_waze_data(df_tt, df_r):

    df_tt['date'] = df_tt['updatetime'].dt.date
    df_tt['time_ext'] = df_tt['updatetime'].dt.time

    df_tt = df_tt.merge(df_r[['name', 'length']], on='name', how='left')
    df_tt = df_tt.loc[df_tt['length'].isnull() == False, :]
    df_tt['time/length'] = (df_tt['time'] / (df_tt['length']))*1000

    grouped_df_tt = df_tt.groupby(["name", pd.Grouper(
        freq="15min", key="updatetime")])['time/length'].mean().to_frame()
    grouped_df_tt.reset_index(inplace=True)

    grouped_df_tt['date'] = grouped_df_tt['updatetime'].dt.date
    grouped_df_tt['time'] = grouped_df_tt['updatetime'].dt.time

    return grouped_df_tt


def assemble_data(extraction_date, *args):
    [df_tt_w, df_r_w] = read_waze_data(extraction_date)
    grouped_df_tt_w = process_waze_data(df_tt_w, df_r_w)
    grouped_df_tt_g = read_gps_data(*args)
    return grouped_df_tt_w, grouped_df_tt_g
