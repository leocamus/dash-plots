import dash
import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from retrieve_data import assemble_data
import plotly.graph_objs as go
from plotly import tools
import pandas as pd
import urllib


def create_dash_app(df_w, df_g):
    app = dash.Dash()

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
#           multi = True,
            multi = False,
            value = df_w.loc[:,'date'].min()
        ),
        html.A(
            'Download Data',
            id='download-link',
            download="rawdata.csv",
            href="",
            target="_blank"
        ),
        dcc.Graph(
            id='travel-times-graph'
        )
    ])

    def filter_data(sd1,sd2s):
        

    @app.callback(Output('travel-times-graph', 'figure'), [Input('query-routes', 'value'), Input('query-dates', 'value')])
    def update_graph(sd1, sd2s):
        # Be aware that the sd1 is (always) a string!
        # Be aware that the sd2 is a list (of strings) because of the multi=True!

        dff_w = df_w[df_w['name'] == sd1]
        dff_g = df_g[df_g['name'] == sd1]

#        fig = tools.make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.00001)
        fig = tools.make_subplots(rows=1, cols=1, shared_xaxes = True, shared_yaxes = True)


        def temporal_transform(x):
            #this should not be necessary.
#            x = x.replace(day = 22)
            #This is weird
            x = x - pd.Timedelta('3 hours')
            return x

        def create_traces(df, query_date, source):
            trace = go.Scatter(
                x = df.loc[df['date'] == sd2_d, 'updatetime'].apply(temporal_transform),
                y = df.loc[df['date'] == sd2_d, 'time/length'],
                mode='lines+markers',
                name = query_date + " " + source)
            return trace         
        
        if type(sd2s) == str:
            sd2_d = dt.datetime.strptime(sd2s, '%Y-%m-%d').date()
            trace_w = create_traces(dff_w, sd2s, "waze")
            trace_g = create_traces(dff_g, sd2s, "gps")
            fig.append_trace(trace_w,1,1)
#            fig.append_trace(trace_g,2,1)
            fig.append_trace(trace_g,1,1)
            fig['data'][1]['marker']['symbol'] = 'triangle-down'

        else:
            for sd2 in sd2s:
                sd2_d = dt.datetime.strptime(sd2, '%Y-%m-%d').date()
                trace_w = create_traces(dff_w, sd2, "waze")
                trace_g = create_traces(dff_g, sd2, "gps")
                fig.append_trace(trace_w,1,1)
#                fig.append_trace(trace_g,2,1)
                fig.append_trace(trace_g,1,1)        

        return fig

    @app.callback(Output('download-link', 'href'),[Input('query-routes', 'value'), Input('query-dates', 'value')])
    def update_download_link(sd1, sd2s):
        dff = filter_data(filter_value)
        csv_string = dff.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + urllib.quote(csv_string)
        return csv_string

    return app




if __name__ == '__main__':
    [grouped_df_tt_w, grouped_df_tt_g] = assemble_data('29.10.2018', '24.10.2018', '25.10.2018')
    app = create_dash_app(grouped_df_tt_w, grouped_df_tt_g)
    app.run_server()
