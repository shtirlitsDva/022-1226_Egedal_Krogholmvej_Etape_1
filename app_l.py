import geopandas as gpd
import os
import dash_leaflet as dl
from dash_leaflet import Marker, DivMarker
import numpy as np
from dash import Dash, html, Output, Input
from dash_extensions.javascript import Namespace
import dash_bootstrap_components as dbc
import plotly.express as px
from itertools import cycle
from typing import List, Dict

def get_rotation_angle(feature: Dict) -> float:
    coordinates = feature['geometry']['coordinates'][:-1]  # Ignore the last point as it's a repeat of the first point

    # Find the two points with the largest distance between them
    p1, p2 = None, None
    max_distance = 0
    for i in range(len(coordinates)):
        distance = np.linalg.norm(np.array(coordinates[i]) - np.array(coordinates[i - 1]))
        if distance > max_distance:
            max_distance = distance
            p1, p2 = coordinates[i], coordinates[i - 1]

    # Calculate the angle based on the two points
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    angle_rad = np.arctan2(dy, dx)
    angle_deg = np.degrees(angle_rad)

    # Ensure the text is never upside down by limiting the rotation angle between -90 and 90 degrees
    # if angle_deg < -90:
    #     angle_deg += 180
    # elif angle_deg > 90:
    #     angle_deg -= 180

    return angle_deg

def get_centroid(gdf: gpd.GeoDataFrame, feature: Dict, properties: List[str]) -> List[float]:
    query_string = " and ".join([f"{prop} == '{feature['properties'][prop]}'" for prop in properties])
    filtered_gdf = gdf.query(query_string)
    
    if not filtered_gdf.empty:
        centroid = filtered_gdf.iloc[0].geometry.centroid
        return [centroid.y, centroid.x]
    else:
        return None

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
    ),
    *[dl.DivMarker(position=[get_centroid(gdf, feature, ['DwgNumber'])[0],
                             get_centroid(gdf, feature, ['DwgNumber'])[1]],
                   children=html.Div(
    f"{feature['properties']['DwgNumber']}",
    style={'color': f"{feature['properties']['color']}",
           'transform': f"rotate({get_rotation_angle(feature)}deg)"
           }))
          for feature in geojson_data["features"]]
    ], style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block"}, id="map"),
    html.Div(id="click-output")
])

@dash_app.callback(Output("click-output", "children"), Input("viewframes", "click_feature"))
def on_viewframe_click(feature):
    if feature is not None:
        return f"You clicked on viewframe {feature['properties']['id']}"

if __name__ == '__main__':
    dash_app.run_server(debug=True)