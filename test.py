import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc
from dash import html
from dash import Dash
from dash.dependencies import Input, Output
import dash

# code and plot setup
# settings
pd.options.plotting.backend = "plotly"
countdown = 20
# global df

# sample dataframe of a wide format
np.random.seed(4)
cols = list('abc')
X = np.random.randn(50, len(cols))
df = pd.DataFrame(X, columns=cols)
df.iloc[0] = 0

# plotly figure
fig = df.plot(template='plotly_dark')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div([
    html.H1("Streaming of random data"),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Graph(id='graph'),
])


# Define callback to update graph
@app.callback(
    Output('graph', 'figure'),
    [Input('interval-component', "n_intervals")]
)
def streamFig(value):
    global df

    Y = np.random.randn(1, len(cols))
    df2 = pd.DataFrame(Y, columns=cols)
    df = df.append(df2, ignore_index=True)  # .reset_index()
    # df.tail()
    df3 = df.copy()
    df3 = df3.cumsum()  # .tail(1000)
    fig = df3.plot(template='plotly_dark')
    # fig.show()

    colors = px.colors.qualitative.Plotly
    for i, col in enumerate(df3.columns):
        fig.add_annotation(x=df3.index[-1], y=df3[col].iloc[-1],
                           text=str(df3[col].iloc[-1])[:4],
                           align="right",
                           arrowcolor='rgba(0,0,0,0)',
                           ax=25,
                           ay=0,
                           yanchor='middle',
                           font=dict(color=colors[i]))

    return (fig)


app.run_server()