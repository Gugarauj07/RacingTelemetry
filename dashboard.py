import dash
from dash import html, dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import plotly.io as io
import pandas as pd
from interpret_serial import df, portList, read_serial
from dash.dependencies import Input, Output, ClientsideFunction
from dash.exceptions import PreventUpdate
from win32api import GetSystemMetrics

screen_height = GetSystemMetrics(1)
print(screen_height)

io.templates.default = 'plotly_dark'
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

df_map = pd.read_csv("map.csv")

# =====================================================================
# Gráficos

# graph_laps = go.Figure(layout={"template": "plotly_dark"})
# graph_laps.add_trace(go.Bar(x=df["tempo"], y=df["ACC"]))
# graph_laps.update_layout(yaxis_title="Lap Times", margin=dict(l=5, r=5, t=5, b=5), autosize=True, height=170)

graph_map = go.Figure(layout={"template": "plotly_dark"})
graph_map.add_trace(
    go.Scatter(x=df_map["latitude"], y=df_map["longitude"], name="location"))
graph_map.update_layout(yaxis_title="Map", margin=dict(l=5, r=5, t=5, b=5), autosize=False, height=388, width=600)

# =====================================================================
# Layout
app.layout = dbc.Container(children=[
    dcc.Interval(
        id='interval-component',
        interval=400,
        n_intervals=0
    ),
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
        ], class_name='d-flex p-3 align-items-center justify-content-evenly', id='connect-div'),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='graph_temperature',
                responsive='auto',
            ),
            dcc.Graph(
                id='graph_velocidade',
                responsive='auto',

            ),
            dcc.Graph(
                id='graph_RPM',
                responsive='auto',

            ),
            dcc.Graph(
                id='graph_ACC',
                responsive='auto',

            ),
            dcc.Graph(
                id='graph_laps',
                responsive='auto',

            ),

        ], className="m-0 p-0 mh-100"),
        dbc.Col([
            dbc.Row([
                dbc.Col([dbc.Card([
                    dbc.CardBody([
                        html.H6("Velocidade", className="card-text text-center"),
                        html.H5("0", style={"color": "#EFE322", "text-align": "center"}, id="velocidade-text"),
                    ], className="m-0 p-0")
                ])], style={'padding-right': '0px'}, md=2),
                dbc.Col([dbc.Card([
                    dbc.CardBody([
                        html.H6("Rotação", className="card-text text-center"),
                        html.H5("0", style={"color": "#EFE322", "text-align": "center"}, id="rpm-text"),
                    ], className="m-0 p-0")
                ])], style={'padding-right': '0px'}, md=2),
                dbc.Col([dbc.Card([
                    dbc.CardBody([
                        html.H6("Aceleração", className="card-text text-center"),
                        html.H5("0", style={"color": "#EFE322", "text-align": "center"}, id="aceleracao-text"),
                    ], className="m-0 p-0")
                ])], style={'padding-right': '0px'}, md=2),
                dbc.Col([dbc.Card([
                    dbc.CardBody([
                        html.H6("Distância", className="card-text text-center"),
                        html.H5("0", style={"color": "#EFE322", "text-align": "center"}, id="distancia-text"),
                    ], className="m-0 p-0")
                ])], style={'padding-right': '0px'}, md=2),
                dbc.Col([dbc.Card([
                    dbc.CardBody([
                        html.H6("Tanque", className="card-text text-center"),
                        html.H5("0", style={"color": "#EFE322", "text-align": "center"}, id="tanque-text"),
                    ], className="m-0 p-0")
                ])], style={'padding-right': '0px'}, md=2),
                dbc.Col([dbc.Card([
                    dbc.CardBody([
                        html.H6("Temperatura", className="card-text text-center"),
                        html.H5("0", style={"color": "#EFE322", "text-align": "center"}, id="temp-text"),
                    ], className="m-0 p-0")
                ])], style={'padding-right': '0px'}, md=2)
            ], className="m-0 p-0 mh-100"),
            dbc.Row([
                dbc.Col([
                    dbc.Row([
                        dbc.Col([
                            daq.Gauge(
                                color={"gradient": True,
                                       "ranges": {"#F6BDC0": [0, 25], "#F07470": [25, 50], "#DC1C13": [50, 80]}},
                                label='Velocidade',
                                id='gauge_velocidade',
                                value=6,
                                size=210,
                                max=80,
                                min=0,
                                style={'margin-top': '10px', 'padding-right': '0px'},
                                theme={
                                    'dark': True,
                                }
                            ),
                        ], md=6, class_name='m-auto'),
                        dbc.Col([
                            daq.Gauge(
                                color={"gradient": True, "ranges": {"#F6BDC0": [0, 2000], "#F07470": [2000, 4000],
                                                                    "#DC1C13": [4000, 6000]}},
                                label='Rotação',
                                size=210,
                                id='gauge_rpm',
                                value=3400,
                                max=6000,
                                min=0,
                                style={'margin-top': '10px'},
                                theme={
                                    'dark': True,
                                }
                            ),
                        ], md=6, class_name='m-auto'),

                    ], class_name='d-flex', style={'height': '250px'}),
                    dbc.Row([
                        daq.GraduatedBar(
                            color={"gradient": True, "ranges": {"red": [0, 2], "yellow": [2, 5], "green": [5, 10]}},
                            showCurrentValue=True,
                            value=10,
                            label='Bateria',
                            labelPosition='top',
                            theme={
                                'dark': True,
                            }
                        )
                    ], class_name='justify-content-center')
                ], md=8),

                dbc.Col([
                    daq.Thermometer(
                        value=35,
                        label='Temperatura CVT',
                        labelPosition='top',
                        min=0,
                        max=100,
                        height=230,
                        width=10,
                        style={'margin-top': '10px'},
                        color='#FF6C00',
                    )
                ], md=2, class_name='p-0'),

                dbc.Col([
                    daq.Tank(
                        id='tank',
                        value=5,
                        showCurrentValue=True,
                        units='litros',
                        min=0,
                        max=10,
                        height=250,
                        style={'margin-top': '10px'},
                        label='Nível do tanque',
                        labelPosition='top',
                        color='#00FFFF'
                    ),
                ], md=2)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.ListGroup([
                        dbc.ListGroupItem([
                            daq.LEDDisplay(
                                label="Tempo de volta",
                                value="1:34.421",
                                size=18,
                                labelPosition='top',
                                backgroundColor="#060606"
                            ),
                        ]),
                        dbc.ListGroupItem([
                            daq.LEDDisplay(
                                label="Velocidade Média",
                                value="55.42",
                                size=18,
                                labelPosition='top',
                                backgroundColor="#060606"
                            ),
                        ]),
                        dbc.ListGroupItem([
                            daq.LEDDisplay(
                                label="Aceleração Média",
                                value="23.92",
                                size=18,
                                labelPosition='top',
                                backgroundColor="#060606",
                            ),
                        ]),
                        dbc.ListGroupItem([
                            daq.LEDDisplay(
                                label="Distância Percorrida",
                                value="232.92",
                                size=18,
                                labelPosition='top',
                                backgroundColor="#060606",
                            ),
                        ]),

                    ], style={'margin': '8px', 'margin-bottom': '0px'}),
                ], md=3, class_name='ms-0 me-0'),
                dbc.Col([
                    dcc.Graph(
                        id='graph_map',
                        figure=graph_map,
                    ),

                ], class_name='mt-2')
            ])
        ], className="m-0 p-0 h-100")
    ], className="m-0 p-0")
], fluid=True, class_name="mh-100")


# =====================================================================
# Callbacks

# Connect button callback
@app.callback(
    Output('connect-div', 'children'),
    Input('connect-button', 'n_clicks'),
    prevent_initial_call=True
)
def callback_function(n_clicks):
    if n_clicks > 0:
        return [
            dbc.Button('Marcar volta!', id='lap-button', style={'width': '200px'}, color='warning'),
            dbc.Button('Disconnect', id='disconnect-button', style={'width': '200px'}, color='danger'),
        ]


# Update Graphs callback
@app.callback(
    Output('graph_temperature', 'figure'),
    Output('graph_velocidade', 'figure'),
    Output('graph_RPM', 'figure'),
    Output('graph_ACC', 'figure'),
    Output('graph_laps', 'figure'),
    Output('velocidade-text', 'children'),
    Output('rpm-text', 'children'),
    Output('aceleracao-text', 'children'),
    Output('distancia-text', 'children'),
    Output('tanque-text', 'children'),
    Output('temp-text', 'children'),
    Output('gauge_velocidade', 'value'),
    Output('gauge_rpm', 'value'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)
def update_graphs(n):
    if n is None:
        raise PreventUpdate
    else:
        read_serial(n)

        graph_temperature = {
            'data': [
                {
                    'line': {'color': '#F6511D'},
                    'mode': 'lines',
                    'type': 'scatter',
                    'name': 'temp_obj',
                    'y': df['temp_obj'].tail(50)
                },
                {
                    'line': {'color': '#FFB400'},
                    'mode': 'lines',
                    'name': 'temp_amb',
                    'type': 'scatter',
                    'y': df['temp_amb'].tail(50)
                }
            ],
            "layout": {
                "xaxis": dict(showline=False, showgrid=True, zeroline=False, autorange=True),
                "yaxis": dict(showgrid=True, showline=False, zeroline=False, autorange=True, title="Temperatura CVT"),
                "autosize": True,
                "height": screen_height / 7,
                "margin": dict(l=40, r=5, t=5, b=20),
                "template": 'plotly_dark',
                "font": {"color": "white"},
                "paper_bgcolor": "rgb(10,10,10)",
                "plot_bgcolor": "rgb(10,10,10)"
            }
        }
        graph_velocidade = {
            'data': [
                {
                    'line': {'color': '#F72585'},
                    'mode': 'lines',
                    'type': 'scatter',
                    'name': 'Roda Esquerda',
                    'y': df['VEL_E'].tail(50)
                },
                {
                    'line': {'color': '#7209B7'},
                    'mode': 'lines',
                    'name': 'Roda Direita',
                    'type': 'scatter',
                    'y': df['VEL_D'].tail(50)
                }
            ],
            "layout": {
                "xaxis": dict(showline=False, showgrid=True, zeroline=False, autorange=True),
                "yaxis": dict(showgrid=True, showline=False, zeroline=False, autorange=True, title="Velocidade"),
                "autosize": True,
                "height": screen_height / 7,
                "margin": dict(l=40, r=5, t=5, b=20),
                "template": 'plotly_dark',
                "font": {"color": "white"},
                "paper_bgcolor": "rgb(10,10,10)",
                "plot_bgcolor": "rgb(10,10,10)"
            }
        }
        graph_RPM = {
            'data': [
                {
                    'line': {'color': '#26C485'},
                    'mode': 'lines',
                    'type': 'scatter',
                    'name': 'Roda',
                    'y': df['RPM_roda'].tail(50)
                },
                {
                    'line': {'color': '#A3E7FC'},
                    'mode': 'lines',
                    'name': 'Motor',
                    'type': 'scatter',
                    'y': df['RPM_motor'].tail(50)
                }
            ],
            "layout": {
                "xaxis": dict(showline=False, showgrid=True, zeroline=False, autorange=True),
                "yaxis": dict(showgrid=True, showline=False, zeroline=False, autorange=True, title="Rotação"),
                "autosize": True,
                "height": screen_height / 7,
                "margin": dict(l=40, r=5, t=5, b=20),
                "template": 'plotly_dark',
                "font": {"color": "white"},
                "paper_bgcolor": "rgb(10,10,10)",
                "plot_bgcolor": "rgb(10,10,10)"
            }
        }
        graph_ACC = {
            'data': [
                {
                    'line': {'color': '#26C485'},
                    'mode': 'lines',
                    'type': 'scatter',
                    'name': 'ACC',
                    'y': df['ACC'].tail(50)
                }
            ],
            "layout": {
                "xaxis": dict(showline=False, showgrid=True, zeroline=False, autorange=True),
                "yaxis": dict(showgrid=True, showline=False, zeroline=False, autorange=True, title="Aceleração"),
                "autosize": True,
                "height": screen_height / 7,
                "margin": dict(l=40, r=5, t=5, b=20),
                "template": 'plotly_dark',
                "font": {"color": "white"},
                "paper_bgcolor": "rgb(10,10,10)",
                "plot_bgcolor": "rgb(10,10,10)"
            }
        }
        graph_laps = {
            'data': [
                {
                    'line': {'color': '#26C485'},
                    'mode': 'lines',
                    'type': 'bar',
                    'name': 'laps',
                    'y': df['ACC'].tail(50)
                }
            ],
            "layout": {
                "xaxis": dict(showline=False, showgrid=True, zeroline=False, autorange=True),
                "yaxis": dict(showgrid=True, showline=False, zeroline=False, autorange=True, title="Tempo de voltas"),
                "autosize": True,
                "height": screen_height * 2 / 9,
                "margin": dict(l=40, r=5, t=5, b=20),
                "template": 'plotly_dark',
                "font": {"color": "white"},
                "paper_bgcolor": "rgb(10,10,10)",
                "plot_bgcolor": "rgb(10,10,10)"
            }
        }
        velocidade_text = df["VEL_E"].tail(1)
        rpm_text = df["RPM_motor"].tail(1)
        aceleracao_text = df["ACC"].tail(1)
        distancia_text = df["Distancia"].tail(1)
        capacitivo = df["capacitivo"].tail(1)

        if int(capacitivo) == 0:
            tanque_text = 'Baixo'
        elif int(capacitivo) == 1:
            tanque_text = 'Médio'
        else:
            tanque_text = 'Alto'

        temp_text = df["temp_obj"].tail(1)

        vel_gauge = float(velocidade_text)
        rpm_gauge = float(rpm_text)

    return graph_temperature, graph_velocidade, graph_RPM, graph_ACC, graph_laps, velocidade_text, rpm_text, \
           aceleracao_text, distancia_text, tanque_text, temp_text, vel_gauge, rpm_gauge


# =====================================================================
# Interactivity
if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port="8050")
