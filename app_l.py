import geopandas as gpd
import os
import dash_leaflet as dl
from dash_leaflet import Marker
import numpy as np
from dash import Dash, html, Output, Input
from dash_extensions.javascript import Namespace
import dash_bootstrap_components as dbc
import plotly.express as px
from itertools import cycle

cwd = os.getcwd()

def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)

colors = cycle(px.colors.qualitative.Plotly)

# Instantiate dash app
dash_app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash_app.server

# Read the GeoJSON file
viewFramesFileName = 'ViewFrames.geojson'
# Next line is an example ViewFrames.geojson feature
# {"type":"FeatureCollection","name":"ViewFrames","features":[{"type":"Feature","properties":{"DwgNumber":"001","PdfLink":"https://damgaardri.sharepoint.com/:b:/s/022-1226Egedal-KrogholmvejEtape1/EWqAQXO0zMxAjEQMbuu7oeYB_jAvgBvUlLHfRp8Om0dGlA"},"geometry":{"coordinates":[[699583.9,6185399],[699535.3,6185198.5],[699466.9,6185215],[699515.4,6185415.5],[699583.9,6185399]],"type":"LineString"}}]}
gdf = gpd.read_file(find(viewFramesFileName, cwd), crs='EPSG:25832')
gdf = gdf.to_crs(epsg=4326)
geojson_data = gdf.__geo_interface__
# add color property to each feature in the GeoJSON
for feature in geojson_data["features"]:
    feature["properties"]["color"] = next(colors)

# Create the namespace and the layout
ns = Namespace("myNamespace", "mySubNamespace")

dash_app.layout = html.Div([
    dl.Map(center=[np.mean(gdf.geometry.centroid.y), np.mean(gdf.geometry.centroid.x)], 
           zoom=13, children=[
        dl.TileLayer( # this styles base map
    url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png',
    attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
        ),
        dl.GeoJSON(
    data=geojson_data, id="viewframes", options=dict(style=ns("style"))
    )
    ], style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}, id="map"),
    html.Div(id="click-output")
])

@dash_app.callback(Output("click-output", "children"), Input("viewframes", "click_feature"))
def on_viewframe_click(feature):
    if feature is not None:
        return f"You clicked on viewframe {feature['properties']['id']}"

if __name__ == '__main__':
    dash_app.run_server(debug=True)