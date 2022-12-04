from dash import html, dcc, ctx
import dash_daq as daq
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
from dash_extensions.enrich import DashProxy, MultiplexerTransform, Input, Output, State
from dash.exceptions import PreventUpdate
from win32api import GetSystemMetrics
import serial
import serial.tools.list_ports
from time import strftime, time
from pathlib import Path
import csv
import gc
from random import randrange

# =====================================================================
# Configurações iniciais
screen_height = GetSystemMetrics(1)

app = DashProxy(
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.CYBORG],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    transforms=[MultiplexerTransform()]
)

df_map = pd.read_csv("map.csv")

serialPort = serial.Serial()
serialPort.timeout = 0.5

arquivo = strftime("%d.%m.%Y_%Hh%M")
path = Path("Arquivos_CSV")
path.mkdir(parents=True, exist_ok=True)
with open(f"Arquivos_CSV/{arquivo}.csv", 'w', newline='') as f:
    thewriter = csv.writer(f)
    thewriter.writerow(
        ['tempo', 'temp_obj', 'temp_amb', 'RPM_motor', 'VEL_E', 'capacitivo', 'ACC', 'RPM_roda', 'Distancia', 'VEL_D'])
portList = [port.device for port in serial.tools.list_ports.comports()]

# TESTING
N = 100
sensors = {
    'tempo': [0],
    'temp_obj': [0],
    'temp_amb': [0],
    'RPM_motor': [0],
    'VEL_E': [0],
    'capacitivo': [0],
    'ACC': [0],
    'RPM_roda': [0],
    'Distancia': [0],
    'VEL_D': [0],
}
df = pd.DataFrame(sensors)
df_laps = pd.DataFrame(columns=["tempo_formatado", "tempo_lap", "acc_avg", "vel_avg", "distancia_lap"])

# =====================================================================
# Gráficos

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
    dcc.Store(id="current-data", storage_type='memory'),
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
                        id='thermoter'
                    )
                ], md=2, class_name='p-0'),

                dbc.Col([
                    daq.Tank(
                        id='tank',
                        value=5,
                        showCurrentValue=True,
                        units='litros',
                        min=0,
                        max=3.8,
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
                                backgroundColor="#060606",
                                id='display_tempo'
                            ),
                        ]),
                        dbc.ListGroupItem([
                            daq.LEDDisplay(
                                label="Velocidade Média",
                                value="55.42",
                                size=18,
                                labelPosition='top',
                                backgroundColor="#060606",
                                id='display_vel'

                            ),
                        ]),
                        dbc.ListGroupItem([
                            daq.LEDDisplay(
                                label="Aceleração Média",
                                value="23.92",
                                size=18,
                                labelPosition='top',
                                backgroundColor="#060606",
                                id='display_acc'
                            ),
                        ]),
                        dbc.ListGroupItem([
                            daq.LEDDisplay(
                                label="Distância Percorrida",
                                value="232.92",
                                size=18,
                                labelPosition='top',
                                backgroundColor="#060606",
                                id='display_distancia'
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
    Input('baudrate-dropdown', 'value'),
    Input('ports-dropdown', 'value'),
    prevent_initial_call=True
)
def callback_function(n_clicks, baud, port):
    if n_clicks is None:
        raise PreventUpdate
    if n_clicks > 0:
        serialPort.port = port
        serialPort.baudrate = int(baud)

        try:
            serialPort.open()  # Tenta abrir a porta serial
        except:
            print("ERROR SERIAL")

        return [
            dbc.Button('Iniciar volta!', id='inicio-button', style={'width': '200px'}, color='success'),
            dbc.Button('Finalizar volta!', id='final-button', style={'width': '200px'}, color='warning'),
            dbc.Button('Disconnect', id='disconnect-button', style={'width': '200px'}, color='danger', href='/'),
        ]


# app.clientside_callback(
#     """
#     function(ibtn, fbtn, data) {
#         button_clicked = ctx.triggered_id
#         data = data || {'tempo': 0, 'tempo_inicio': 0, 'tempo_final': 0}
#
#         if (button_clicked == 'inicio-button'){
#             data["tempo_inicio"] = data["tempo"]
#             return data
#         }
#         elif (button_clicked == 'final-button'){
#             data["tempo_final"] = data["tempo"]
#             return data
#         }
#     }
#     """,
#     Output('current-data', 'data'),
#     Input('inicio-button', 'n_clicks'),
#     Input('final-button', 'n_clicks'),
#     State('current-data', 'data'),
# )

initial_time = int(round(time() * 1000))


def convert_time(millisseconds):
    mili = millisseconds % 1000
    seconds = (millisseconds // 1000) % 60
    minutes = (millisseconds // 1000) // 60
    return "%d:%02d.%02d" % (minutes, seconds, mili)


tempo_inicio, tempo_final = 0, 0


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
    Output('thermoter', 'value'),
    Output('tank', 'value'),
    Output('display_tempo', 'value'),
    Output('display_vel', 'value'),
    Output('display_acc', 'value'),
    Output('display_distancia', 'value'),
    Input('interval-component', 'n_intervals'),
    Input('inicio-button', 'n_clicks'),
    Input('final-button', 'n_clicks'),
    prevent_initial_call=True
)
def update_graphs(n, ibtn, fbtn):
    if n is None:
        raise PreventUpdate
    else:
        button_clicked = ctx.triggered_id
        global tempo_final, tempo_inicio

        tempo = int(round(time() * 1000)) - initial_time
        temp_obj, temp_amb, RPM, VEL, capacitivo = 0, 0, 0, 0, 0

        if serialPort.is_open:
            try:
                temp_obj, temp_amb, RPM, VEL, capacitivo = [int(x) for x in
                                                            serialPort.readline().decode("utf-8").rstrip("\r\n").split(
                                                                ',')]
            except ValueError:
                print("ValueError")

        Distancia = round(VEL / 3.6 + float(df["Distancia"].tail(1)), 2)  # Metros
        ACC = round(VEL - float(df["VEL_E"].tail(1)), 2)
        ACC = ACC if ACC > 0 else 0

        RPMroda = VEL / ((18 / 60) * 0.04625 * 1.72161199 * 3.6)
        line = [tempo, temp_obj, temp_amb, RPM, VEL, capacitivo, ACC, RPMroda, Distancia, 0]
        df.loc[len(df)] = line

        tempo_formatado = "0:00.000"
        tempo_percorrido, acc_avg, vel_avg, distancia_lap = 0, 0, 0, 0
        if tempo_inicio != 0:
            df_tempo = df[df["tempo"].between(tempo_inicio, df["tempo"].iloc[-1])]
            acc_avg = round(df_tempo["ACC"].mean(), 2)
            vel_avg = round(df_tempo["VEL_E"].mean(), 2)
            distancia_lap = round(df_tempo["Distancia"].iloc[-1] - df_tempo["Distancia"].iloc[0], 2)
            tempo_percorrido = df_tempo["tempo"].iloc[-1] - df_tempo["tempo"].iloc[0]
            tempo_formatado = convert_time(tempo_percorrido)

            if tempo_final != 0:
                tempo_final = 0
                tempo_inicio = 0
                df_laps.loc[len(df_laps)] = [tempo_formatado, tempo_percorrido, acc_avg, vel_avg, distancia_lap]

        if button_clicked == 'inicio-button':
            tempo_inicio = df["tempo"].iloc[-1]
            print('oi')

        elif button_clicked == 'final-button':
            tempo_final = df["tempo"].iloc[-1]
            print('oi')

        with open(f"Arquivos_CSV/{arquivo}.csv", 'a+', newline='') as f:
            thewriter = csv.writer(f)
            thewriter.writerow(line)

        # gc.collect()

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
                "plot_bgcolor": "rgb(10,10,10)",
                "hovermode": 'x unified'
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
                "plot_bgcolor": "rgb(10,10,10)",
                "hovermode": 'x unified'
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
                "plot_bgcolor": "rgb(10,10,10)",
                "hovermode": 'x unified'
            }
        }
        graph_ACC = {
            'data': [
                {
                    'line': {'color': '#E24C33'},
                    'mode': 'lines',
                    'type': 'scatter',
                    'name': 'ACC',
                    'y': df['ACC'].tail(50),
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
                "plot_bgcolor": "rgb(10,10,10)",
                "hovermode": 'x unified'
            }
        }
        graph_laps = {
            'data': [
                {
                    'type': 'bar',
                    'name': 'Tempo Percorrido',
                    'y': [x / 1000 for x in df_laps['tempo_lap'].tail(50)]
                },
                {
                    'type': 'bar',
                    'name': 'Velocidade Média',
                    'y': df_laps['vel_avg'].tail(50)
                },
                {
                    'type': 'bar',
                    'name': 'Aceleração Média',
                    'y': df_laps['acc_avg'].tail(50)
                },
                {
                    'type': 'bar',
                    'name': "Distancia Percorrida",
                    'y': [x / 10 for x in df_laps['distancia_lap'].tail(50)]
                },

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
        temp_text = df["temp_obj"].tail(1)

        if int(capacitivo) == 0:
            tanque_text = 'Baixo'
            tank_daq = 1
        elif int(capacitivo) == 1:
            tanque_text = 'Médio'
            tank_daq = 2
        else:
            tanque_text = 'Alto'
            tank_daq = 3.5

        vel_gauge = float(velocidade_text)
        rpm_gauge = float(rpm_text)
        temp = float(temp_text)

    return graph_temperature, graph_velocidade, graph_RPM, graph_ACC, graph_laps, velocidade_text, rpm_text, \
           aceleracao_text, distancia_text, tanque_text, temp_text, vel_gauge, rpm_gauge, temp, tank_daq, \
           tempo_formatado, vel_avg, acc_avg, distancia_lap


# =====================================================================
# Interactivity
if __name__ == '__main__':
    app.run_server(threaded=True, debug=True)
