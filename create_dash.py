import dash
import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from retrieve_data import *
import plotly.graph_objs as go
from plotly import tools


def create_dash_app(df):
    app = dash.Dash()
    app.layout = html.Div(children=[
        # This component generates a <h1></h1> HTML element in your application
        html.H1(children='Travel Times'),
        # The dcc describe higher-level components that are interactive
        dcc.Dropdown(
            id='query-dates',
            options=[{'label': i.strftime("%d-%m-%Y"), 'value': i}
                     for i in df['fecha_extraccion'].unique()],
            # This is the default value
            value='2018-09-28'
        ),
        dcc.Dropdown(
            id='query-routes',
            options=[{'label': i, 'value': i}
                     for i in df['rtanombre'].unique()],
            multi=True,
            value='None'
        ),
        dcc.Graph(
            id='travel-times-graph'
        )
    ])

    @app.callback(Output('travel-times-graph', 'figure'), [Input('query-dates', 'value'), Input('query-routes', 'value')])
    def update_graph(sd1, sd2s):
        # Be aware that the sd1 is a string!
        # Be aware that the sd2 is a list because of the multi=True!
        sd1 = dt.datetime.strptime(sd1, '%Y-%m-%d').date()

        dff = df[df['fecha_extraccion'] == sd1]
        fig = tools.make_subplots(rows=1, cols=1, shared_xaxes=True,
                                  shared_yaxes=True, vertical_spacing=0.001)
#        data = []
        for sd2 in sd2s:
            trace = go.Scatter(
                x=dff.loc[dff['rtanombre'] == sd2, 'tiempo_extraccion'],
                y=dff.loc[dff['rtanombre'] == sd2, 'tvjtiempo/length'],
                mode='lines')
    #            data.append(trace)
            fig.append_trace(trace,1,1)

        return fig

 #       return {
            #'data': data
 #           'figure' : fig
 #       }

    return app


if __name__ == '__main__':
    df_travel_times = read_data()[0]
    app = create_dash_app(df_travel_times)
    app.run_server()
