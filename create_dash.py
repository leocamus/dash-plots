import dash
import datetime as dt
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from retrieve_data import assemble_data
import plotly.graph_objs as go
from plotly import tools
import pandas as pd


def create_dash_app(df):
    app = dash.Dash()

    app.layout = html.Div(children=[
        # This component generates a <h1></h1> HTML element in your application
        html.H1(children='Travel Times'),
        # The dcc describe higher-level components that are interactive
        dcc.Dropdown(
            id='query-routes',
            options=[{'label': i, 'value': i}
                     for i in df['name'].unique()],
            # This is the default value
            value='TramoTresAntoniosSN1'
        ),
        dcc.Dropdown(
            id='query-dates',
            options=[{'label': i.strftime("%d-%m-%Y"), 'value': i}
                     for i in df['date_ext'].unique()],
            multi = True,
            value = dt.date(2018, 10, 20)
        ),
        dcc.Graph(
            id='travel-times-graph'
        )
    ])

    @app.callback(Output('travel-times-graph', 'figure'), [Input('query-routes', 'value'), Input('query-dates', 'value')])
    def update_graph(sd1, sd2s):
        # Be aware that the sd1 is (always?) a string!
        # Be aware that the sd2 is a list (of strings) because of the multi=True!

        dff = df[df['name'] == sd1]
        fig = tools.make_subplots(rows=1, cols=1, shared_xaxes=False,
                                  shared_yaxes=True, vertical_spacing=0.001)


        def temporal_transform(x):
            #this is an ugly function.
            x = x.replace(day = 22)
            #This should not be done when data comes with tz in the proper way.
            x = x - pd.Timedelta('3 hours')
            return x

        for sd2 in sd2s:
            print('Selected dropdown value for the second dropdown menu is: ' + sd2 + '. The type of the' + 
            ' selected dropdown value for the second dropdown menu is: ' + str(type(sd2)))

            sd2_d = dt.datetime.strptime(sd2, '%Y-%m-%d').date()
            trace = go.Scatter(
                x = dff.loc[dff['date_ext'] == sd2_d, 'updatetime_stgo'].apply(temporal_transform),
                y = dff.loc[dff['date_ext'] == sd2_d, 'time/length'],
                mode='lines+markers',
                name = sd2)
    #            data.append(trace)
            fig.append_trace(trace,1,1)

        return fig

 #       return {
            #'data': data
 #           'figure' : fig
 #       }

    return app


if __name__ == '__main__':
    df_tt = assemble_data()[0]
    app = create_dash_app(df_tt)
    app.run_server()
