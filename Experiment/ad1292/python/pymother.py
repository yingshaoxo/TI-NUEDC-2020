"""
author: yingshaoxo
gmail: yingshaoxo@gmail.com
ls -l /dev/ttyUSB0
sudo usermod -a -G uucp yingshaoxo
sudo chmod a+rw /dev/ttyUSB0
"""
import plotly.graph_objects as go
import pandas as pd
import time
import serial
import binascii
from time import sleep
from struct import pack, unpack
import numpy as np


import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque

import threading

X = deque(maxlen=1000)
X.append(1)

Y = deque(maxlen=1000)
Y.append(1)

app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True),
        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals=0
        ),
    ]
)


@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(n):
    data = plotly.graph_objs.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers'
    )

    return {'data': [data],
            'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]), yaxis=dict(range=[min(Y), max(Y)]),)}


the_thread = threading.Thread(target=app.run_server, args=())
the_thread.start()


# ser = serial.Serial('/dev/ttyACM1', 115200)  # open serial port
ser = serial.Serial('COM4', 115200)  # open serial port
print(ser.name)         # check which port was really used

show = False
index = 0
while 1:
    index += 1
    if (index > 10000000):
        index = 0
    if ser.readable():
        heading1 = ser.read(1)
        if heading1.hex() == "0a":
            if ser.readable():
                heading2 = ser.read(1)
                if heading2.hex() == "fa":
                    if ser.readable():
                        data_length_bytes = ser.read(2)
                        data_length = unpack("H", data_length_bytes)[0]
                        # print(data_length)
                        if ser.readable():
                            type_bytes = ser.read(1)
                            type_ = unpack("B", type_bytes)[0]
                            if type_ == 2:
                                if ser.readable():
                                    data_bytes = ser.read(data_length)
                                    data = unpack("<iiB", data_bytes)
                                    ecg, resp, heart_rate = data

                                    X.append(index)
                                    Y.append(ecg)

                                    if heart_rate != 0:
                                        #print(data)
                                        pass