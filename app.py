import geopandas as gpd
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objs as go
import os
from itertools import cycle

cwd = os.getcwd()

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

# Instantiate dash app
dash_app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server        

# Read the GeoJSON file
viewFramesFileName = 'ViewFrames.geojson'
gdf = gpd.read_file(find(viewFramesFileName, cwd), crs='EPSG:25832')
gdf = gdf.to_crs(epsg=4326)

# Populate the dict with number and link
rectangle_sharepoint_urls = dict(zip(gdf['DwgNumber'], gdf['PdfLink']))  # Update with PDF links

# function to get colors
colors = cycle(px.colors.qualitative.Plotly)

def generate_traces(gdf):
    traces = []
    for index, row in gdf.iterrows():
        
        color = next(colors)

        coordinates = np.array(row.geometry.coords)
        lon, lat = coordinates[:, 0], coordinates[:, 1]
        trace_lines = go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode="lines",
            line=dict(width=2, color=color),
            customdata=[index],
            hoverinfo='none',
            showlegend=True,
            name=row['DwgNumber']
        )
        traces.append(trace_lines)
        
        # Add a trace for the viewframe number
        number_coords = row.geometry.centroid.coords[0]
        trace_numbers = go.Scattermapbox(
            lat=[number_coords[1]],
            lon=[number_coords[0]],
            mode="text",
            text=[row['DwgNumber']],
            customdata=[index],
            hovertemplate='<b>Viewframe:</b> %{customdata}<br>',
            textposition="middle center",
            textfont=dict(size=14, color=color),
            showlegend=False
        )
        traces.append(trace_numbers)
        
    return traces

map_json = gdf.__geo_interface__

graph = dbc.Card([dcc.Graph(id='map')])
dash_app.layout = dbc.Container(
    [
        html.H1('Interactive Plotly Dash Map'),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(graph, width=12),
            ]
        )
    ], fluid=True
)

@dash_app.callback(
    Output('map', 'figure'),
    Input('map', 'clickData'))
def display_map(clickData):
    fig = go.Figure(data=generate_traces(gdf))
    
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=go.layout.Mapbox(
            style="carto-positron",
            zoom=15,
            center_lat=gdf.geometry.centroid.y.mean(),
            center_lon=gdf.geometry.centroid.x.mean(),
        )
    )
    
    if clickData:
        clicked_id = clickData["points"][0]["customdata"]
        pdf_url = rectangle_sharepoint_urls.get(clicked_id)
        if pdf_url:
            fig.add_annotation(
                x=clickData["points"][0]["lon"],
                y=clickData["points"][0]["lat"],
                text=f'<a href="{pdf_url}" target="_blank">Open PDF</a>',
                showarrow=True,
                font=dict(size=12, color="black"),
                bgcolor="white",
                bordercolor="black",
                borderwidth=1,
                opacity=0.8
            )
    return fig

# alternative table from dbc
def generate_dbc_table(dataframe):
    return dbc.Table.from_dataframe(dataframe, striped=True, bordered=True, hover=True, responsive=True)

if __name__ == '__main__':
    dash_app.run_server(debug=True)