import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from interpret_serial import df, portList
from dash.dependencies import Input, Output, ClientsideFunction

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# =====================================================================
# Gráficos

# graph_temperature = px.line(df, x="tempo", y=['temp_obj', 'temp_amb'], color='variable', title='Temperatura CVT' )
graph_temperature = go.Figure(layout={"template": "plotly_dark"})
graph_temperature.add_trace(go.Scatter(x=df["tempo"], y=df["temp_obj"], name="temp_obj", mode="lines", line=dict(color="#F6511D")))
graph_temperature.add_trace(go.Scatter(x=df["tempo"], y=df["temp_amb"], name="temp_amb", mode="lines", line=dict(color="#FFB400")))
graph_temperature.update_layout(yaxis_title="Temperatura CVT", height=150, margin=dict(l=5, r=5, t=5, b=5))

graph_velocidade = go.Figure(layout={"template": "plotly_dark"})
graph_velocidade.add_trace(go.Scatter(x=df["tempo"], y=df["VEL_D"], name="Roda Direita", mode="lines", line=dict(color="#F72585")))
graph_velocidade.add_trace(go.Scatter(x=df["tempo"], y=df["VEL_E"], name="Roda Esquerda", mode="lines", line=dict(color="#7209B7")))
graph_velocidade.update_layout(yaxis_title="Velocidade", height=150, margin=dict(l=5, r=5, t=5, b=5))

graph_PRM = go.Figure(layout={"template": "plotly_dark"})
graph_PRM.add_trace(go.Scatter(x=df["tempo"], y=df["RPM_motor"], name="Motor", mode="lines", line=dict(color="#26C485")))
graph_PRM.add_trace(go.Scatter(x=df["tempo"], y=df["RPM_roda"], name="Roda", mode="lines", line=dict(color="#A3E7FC")))
graph_PRM.update_layout(yaxis_title="Rotação", height=150, margin=dict(l=5, r=5, t=5, b=5))

graph_ACC = go.Figure(layout={"template": "plotly_dark"})
graph_ACC.add_trace(go.Scatter(x=df["tempo"], y=df["ACC"], name="acc (km/h²)", mode="lines", line=dict(color="#FF6F59")))
graph_ACC.update_layout(yaxis_title="Aceleração", height=150, margin=dict(l=5, r=5, t=5, b=5))

# =====================================================================
# Layout
app.layout = dbc.Container(children=[
    dbc.Row([
        dbc.Col([
            html.Div(children=[
                html.H5(children='BAJA UEA'),
                html.H6(children="Visualização dos dados da telemetria"),
            ]),
        ]),
        dbc.Col([
            dcc.Dropdown(['2400', '4800', '9600', '115200'], id='baudrate-dropdown', value='9600',
                         placeholder='Baudrate', style={'width': '150px'}),
            dcc.Dropdown(portList, id='ports-dropdown', value='portList[0]', placeholder='COM Ports',
                         style={'width': '150px'}),
            dbc.Button('Connect', id='connect-button', style={'width': '150px'}),
        ], class_name='d-flex p-3 align-items-center justify-content-evenly'),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph_temperature',
                figure=graph_temperature
            ),
            dcc.Graph(
                id='graph_velocidade',
                figure=graph_velocidade
            ),
            dcc.Graph(
                id='graph_PRM',
                figure=graph_PRM
            ),
            dcc.Graph(
                id='graph_ACC',
                figure=graph_ACC
            )
        ]),
        dbc.Col([

        ])
    ])
], className="fluid")

# =====================================================================
# Interactivity

if __name__ == '__main__':
    app.run_server()
