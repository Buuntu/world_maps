import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.plotly as py
import pandas as pd
from flask import Flask, json
import requests
import requests_cache
from dotenv import load_dotenv
import os
import pdb

requests_cache.install_cache(expire_after=1000)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])

app_name = 'Dash Earthquakes'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
app = dash.Dash(__name__, server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

# Get USGS data
usgs = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.geojson'
req = requests.get(usgs)
data = json.loads(req.text)
# pdb.set_trace()

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/Nuclear%20Waste%20Sites%20on%20American%20Campuses.csv')
site_lat = df.lat
site_lon = df.lon
locations_name = df.text

app.config['suppress_callback_exceptions'] = True

app.layout = html.Div(children=[
    html.H1(children='World GDPs', style={'textAlign': 'center'}),
    dcc.Graph(
        id='world-map',
        figure=go.Figure({
            'data': [
                go.Scattermapbox(
                    lat=site_lat,
                    lon=site_lon,
                    mode='markers',
                    marker=dict(
                        size=17,
                        color='rgb(255, 0, 0)',
                        opacity=0.7
                    ),
                    hoverinfo='text',
                    text=locations_name
                )
            ],
            'layout': go.Layout(
                autosize=True,
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    style='light',
                    pitch=0,
                    zoom=3,
                ),
            )
        })
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
