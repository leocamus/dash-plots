import os
import pandas as pd
import datetime as dt
from utils import constants


def query_database(freq):
    # The connection should be open all the time.
    # Data is retrieved with some frequency.
    # Pandas dataframe is built and manipulated to build the Dash app
    pass


def read_data(extraction_date):
    # Should be replaced for a connection to a ddbb
    travel_times_dir = constants.travel_times_dir
    travel_times = os.path.join(travel_times_dir, 'travel_times_' + extraction_date + '.csv')
    
    routes = os.path.join(travel_times_dir, 'routes_' + extraction_date + '.csv')

    df_tt = pd.read_csv(travel_times, sep=';', encoding='latin-1', parse_dates=['updatetime'],
                        date_parser=lambda x: pd.to_datetime(x.rpartition('-')[0]))

    df_r = pd.read_csv(routes, sep=';', encoding='latin-1', parse_dates=['start_date'])

    return df_tt, df_r


def process_data(df_tt, df_r):

    df_tt['updatetime_stgo'] = df_tt['updatetime'].apply(lambda x: x - pd.Timedelta('3 hours'))

    df_tt['date_ext'] = df_tt['updatetime_stgo'].dt.date
    df_tt['time_ext'] = df_tt['updatetime_stgo'].dt.time

    df_tt = df_tt.merge(df_r[['name', 'length']], on='name', how='left')
    df_tt = df_tt.loc[df_tt['length'].isnull() == False, :]
    df_tt['time/length'] = (df_tt['time'] / (df_tt['length']))*1000
    # Only saturday, sunday and monday
    #sat = dt.date(2018, 10, 20)
    #sun = dt.date(2018, 10, 21)
    #mon = dt.date(2018, 10, 22)

    #df_tt = df_tt.loc[(df_tt['date_ext'] == sat)|(df_tt['date_ext'] == sun)|(df_tt['date_ext'] == mon),:]

    grouped_df_tt = df_tt.groupby(["name", pd.Grouper(
        freq="15min", key="updatetime_stgo")])['time/length'].mean().to_frame()
    grouped_df_tt.reset_index(inplace=True)

    grouped_df_tt['date_ext'] = grouped_df_tt['updatetime_stgo'].dt.date
    grouped_df_tt['time_ext'] = grouped_df_tt['updatetime_stgo'].dt.time

    return df_tt, grouped_df_tt


def assemble_data(extraction_date):
    [df_tt, df_r] = read_data(extraction_date)
    [df_tt, grouped_df_tt] = process_data(df_tt, df_r)
    return df_tt, df_r, grouped_df_tt
