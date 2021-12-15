import pandas as pd
import numpy as np

import dash

from dash import dcc, html
from dash.dependencies import Input, Output

import plotly.graph_objects as go
import plotly.express as px

from gas import Gas, get_gas_files

# Gas
gas_files = get_gas_files()
print(f"found {len(gas_files)} gas files")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(title="Gas Dashboard", external_stylesheets=external_stylesheets)
app._favicon = "assets/favicon.png"

app.layout = html.Div([
    dcc.Store(id='selected-gases'),
    html.Div([
        html.Center(html.H3("Gas Selection")),
        dcc.Dropdown(
            options=[{"label": gas_file.split("/")[-1], "value": gas_file} for gas_file in gas_files],
            value=[],
            multi=True,
            id="gas-selection-dropdown-multi"
        ),
    ]),
    dcc.Tab(label="Gas", children=[
        dcc.RangeSlider(
            id="electric-field-slider",
            min=1E1,
            max=1E4,
            step=1,
            value=[1E1, 1E3]
        ),
        dcc.RangeSlider(
            id="pressure-slider",
            min=1E-3,
            max=1E1,
            step=1E-3,
            value=[1E-3, 1E1]
        ),
        dcc.RangeSlider(
            id="temperature-slider",
            min=100,
            max=300,
            step=0.1,
            value=[100, 300]
        ),
        dcc.RadioItems(
            options=[
                {"label": "Electric Field", "value": "electric-field"},
                {"label": "Pressure", "value": "pressure"},
                {"label": "Temperature", "value": "temperature"}
            ],
            value="electric-field",
            id="gas-plot-x-axis-radio"
        ),
        dcc.Tabs([
            dcc.Tab(label="Drift Velocity", children=[
                html.Div([
                    html.Center(html.H3("Drift Velocity")),
                    dcc.Graph(
                        id="drift-velocity-graph",
                    )]
                )
            ]),
            dcc.Tab(label="Diffusion Coefficient", children=[
                html.Div([
                    html.Center(html.H3("Diffusion Coefficient"))
                ])
            ])
        ])
    ])
])


@app.callback(
    Output("selected-gases", "data"),
    Input("gas-selection-dropdown-multi", "value"))
def update_gases(gas_selection):
    data = {gas_name: Gas(gas_name) for gas_name in gas_selection}
    print(f"updated stored gases to: {data}")
    return data


@app.callback(
    Output("drift-velocity-graph", "figure"),
    Input("selected-gases", "data"),
    Input("electric-field-slider", "value"),
    Input("pressure-slider", "value"),
    Input("temperature-slider", "value"),
    Input("gas-plot-x-axis-radio", "value"))
def update_drift_velocity(available_gases, electric_field_range, pressure_range, temperature_range, x_axis_selection):
    if len(available_gases) == 0:
        return
    return
    gas = available_gases[list(available_gases.keys())[0]]

    if x_axis_selection == "electric-field":
        electric_field = np.logspace(np.log10(np.min(electric_field_range)), np.log10(np.max(electric_field_range)),
                                     1000)
        drift_velocity = gas.get_drift_velocity_electric_field(electric_field) * 1E3

        df = pd.DataFrame({"Electric Field (V/cm)": electric_field,
                           "Drift Velocity (cm/us)": drift_velocity})
        fig = px.line(df, x="Electric Field (V/cm)", y="Drift Velocity (cm/us)", log_x=True, template="simple_white")
        fig.update_traces(line_color="red")
        fig.update_layout(
            xaxis=dict(
                showline=True, showgrid=True, ticks="outside", linewidth=2
            ))
    elif x_axis_selection == "pressure":
        pressure = np.linspace(np.min(pressure_range), np.max(pressure_range), 1000)
        drift_velocity = gas.get_drift_velocity_pressure(electric_field=100, pressure=pressure)

        df = pd.DataFrame({"Pressure (Bar)": pressure,
                           "Drift Velocity (cm/us)": drift_velocity})
        fig = px.line(df, x="Pressure (Bar)", y="Drift Velocity (cm/us)", log_x=False, template="simple_white")
        fig.update_traces(line_color="blue")
        fig.update_layout(
            xaxis=dict(
                showline=True, showgrid=True, ticks="outside", linewidth=2
            ))
    elif x_axis_selection == "temperature":
        temperature = np.linspace(np.min(temperature_range), np.max(temperature_range), 1000)
        drift_velocity = gas.get_drift_velocity_temperature(electric_field=100, temperature=temperature)

        df = pd.DataFrame({"Temperature (K)": temperature,
                           "Drift Velocity (cm/us)": drift_velocity})
        fig = px.line(df, x="Temperature (K)", y="Drift Velocity (cm/us)", log_x=False, template="simple_white",
                      color=None)
        fig.update_traces(line_color="green")
        fig.update_layout(
            xaxis=dict(
                showline=True, showgrid=True, ticks="outside", linewidth=2
            ))
    return fig


if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=8888)
