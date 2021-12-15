import dash_core_components as dcc
import dash
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from gas import Gas

# Gas
test_gas_file = "files/gas/test.gas"

gas = Gas()
gas.load_gas_file(test_gas_file)
#

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Tab(label='Gas', children=[
        dcc.Graph(
            id='gas-graph',
        ),
    ])
])

if __name__ == '__main__':
    print(gas)
    app.run_server(debug=True)
