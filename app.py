#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Import required libraries
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

# Load your dataset
file_path = 'World Energy Consumption.csv'  # Ensure this file is in the same directory
energy_data = pd.read_csv(file_path)

# Clean and preprocess the dataset
energy_data_clean = energy_data.dropna(subset=["country", "year", "gdp", "population"])
energy_data_clean["year"] = energy_data_clean["year"].astype(int)
energy_columns = [col for col in energy_data.columns if "consumption" in col]

# Initialize the Dash app
app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Global Energy Consumption Dashboard", style={"text-align": "center"}),

    # Select Year Range
    html.Div([
        html.Label("Select Year Range:", style={"color": "#FFFFFF"}),
        dcc.RangeSlider(
            id="year-slider",
            min=energy_data_clean["year"].min(),
            max=energy_data_clean["year"].max(),
            step=1,
            marks={str(year): str(year) for year in range(1900, 2025, 25)},
            value=[2000, 2020],
        )
    ], style={"margin-bottom": "20px"}),

    # Dropdowns for filtering
    html.Div([
        html.Div([
            html.Label("Select Country:", style={"color": "#FFFFFF"}),
            dcc.Dropdown(
                id="country-dropdown",
                options=[{"label": c, "value": c} for c in energy_data_clean["country"].unique()],
                value="United States",
                multi=False,
                style={"width": "100%", "color": "#000000"}
            ),
        ], style={"width": "30%", "display": "inline-block", "padding": "0 10px"}),

        html.Div([
            html.Label("Select Energy Type (Pie Chart):", style={"color": "#FFFFFF"}),
            dcc.Dropdown(
                id="energy-pie-dropdown",
                options=[{"label": col, "value": col} for col in energy_columns],
                value="biofuel_consumption",
                style={"width": "100%", "color": "#000000"}
            )
        ], style={"width": "30%", "display": "inline-block", "padding": "0 10px"}),

        html.Div([
            html.Label("Select Energy Type (Scatter Plot):", style={"color": "#FFFFFF"}),
            dcc.Dropdown(
                id="energy-scatter-dropdown",
                options=[{"label": col, "value": col} for col in energy_columns],
                value="biofuel_consumption",
                style={"width": "100%", "color": "#000000"}
            )
        ], style={"width": "30%", "display": "inline-block", "padding": "0 10px"}),
    ], style={"margin-bottom": "20px"}),

    # Graphs and interactions
    html.Div([
        dcc.Graph(id="energy-trend")
    ], style={"margin-bottom": "20px"}),

    html.Div([
        dcc.Graph(id="energy-share")
    ], style={"margin-bottom": "20px"}),

    html.Div([
        dcc.Graph(id="gdp-vs-energy")
    ])
], style={"backgroundColor": "#111111", "color": "#FFFFFF"})

# Callbacks for interactivity
@app.callback(
    [Output("energy-trend", "figure"),
     Output("energy-share", "figure"),
     Output("gdp-vs-energy", "figure")],
    [Input("country-dropdown", "value"),
     Input("year-slider", "value"),
     Input("energy-pie-dropdown", "value"),
     Input("energy-scatter-dropdown", "value")]
)
def update_graphs(selected_country, year_range, pie_energy, scatter_energy):
    # Filter data based on inputs
    filtered_data = energy_data_clean[
        (energy_data_clean["country"] == selected_country) &
        (energy_data_clean["year"] >= year_range[0]) &
        (energy_data_clean["year"] <= year_range[1])
    ]

    # Energy trends over time
    trend_fig = px.line(
        filtered_data,
        x="year",
        y=["biofuel_consumption", "solar_consumption", "wind_consumption"],
        title=f"Energy Trends in {selected_country} ({year_range[0]}-{year_range[1]})",
        labels={"value": "Energy Consumption (TWh)", "variable": "Energy Type"}
    )
    trend_fig.update_layout(
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font_color="#FFFFFF",
        xaxis=dict(gridcolor="#444444"),
        yaxis=dict(gridcolor="#444444")
    )

    # Energy share (Pie chart for selected energy type)
    share_fig = px.pie(
        filtered_data,
        values=pie_energy,
        names="year",
        title=f"Energy Share ({pie_energy}) in {selected_country}"
    )
    share_fig.update_layout(
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font_color="#FFFFFF"
    )

    # GDP vs. Selected Energy Type
    gdp_fig = px.scatter(
        filtered_data,
        x="gdp",
        y=scatter_energy,
        size="population",
        color="year",
        title=f"GDP vs. {scatter_energy}",
        labels={"gdp": "GDP", scatter_energy: f"{scatter_energy} (TWh)"}
    )
    gdp_fig.update_layout(
        plot_bgcolor="#111111",
        paper_bgcolor="#111111",
        font_color="#FFFFFF",
        xaxis=dict(gridcolor="#444444"),
        yaxis=dict(gridcolor="#444444")
    )

    return trend_fig, share_fig, gdp_fig

# Ensure the app is callable by gunicorn
server = app.server

