import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.plotly as py
import pandas as pd
from flask import Flask, json
import requests
import requests_cache
from dotenv import load_dotenv
from datetime import datetime as dt
import datetime
import os

requests_cache.install_cache(expire_after=500)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

mapbox_access_token = os.environ.get('MAPBOX_ACCESS_TOKEN')
py.sign_in(os.environ['PLOTLY_USERNAME'], os.environ['PLOTLY_API_KEY'])

app_name = 'Dash Earthquakes'
server = Flask(app_name)
server.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')
app = dash.Dash(__name__, server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(style={'textAlign': 'center'}, children=[
    html.H1(children='World Earthquakes', style={'textAlign': 'center'}),
    dcc.DatePickerRange(
        id='date-range-picker',
        min_date_allowed=dt(1995, 8, 5),
        max_date_allowed=dt.now().replace(hour=0, minute=0, second=0, microsecond=0),
        initial_visible_month=dt.now(),
    ),
    dcc.Graph(
        id='world-map',
        figure=go.Figure({
            'data': [
                go.Scattermapbox(
                )
            ],
            'layout': go.Layout(
                autosize=True,
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    style='light',
                    pitch=0,
                    zoom=1,
                ),
            )
        })
    ),
    dbc.CardDeck(style={'width': '30%', 'margin': 'auto'}, id='earthquake-info')
])


@app.callback(
    dash.dependencies.Output('world-map', 'figure'),
    [dash.dependencies.Input('date-range-picker', 'start_date'),
     dash.dependencies.Input('date-range-picker', 'end_date')]
)
def _update_map(start_date, end_date):
    if (start_date is None) or (end_date is None):
        return

    base_url = 'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&'
    url = base_url + 'starttime=' + start_date + '&endtime=' + end_date
    req = requests.get(url)
    data = json.loads(req.text)
    df = pd.DataFrame(columns=['lat', 'lon'])
    for row in data['features']:
        df = df.append({'lon': row['geometry']['coordinates'][0],
                        'lat': row['geometry']['coordinates'][1],
                        'mag': row['properties']['mag'],
                        'place': row['properties']['place'],
                        'url': row['properties']['url'],
                        'properties': row['properties']}, ignore_index=True)

    site_lat = df['lat']
    site_lon = df['lon']
    mag = df['mag']
    place = df['place']
    url = df['url']
    mag = mag.clip(lower=0)
    mag = mag.fillna(0)
    properties = df['properties']

    return {
        'data': [
            go.Scattermapbox(
                lat=site_lat,
                lon=site_lon,
                mode='markers',
                customdata=properties,
                marker=dict(
                    size=mag ** 2,
                    color='rgb(255, 0, 0)',
                    opacity=0.3
                ),
                hoverinfo='text',
                text=place
            )
        ],
        'layout': go.Layout(
            autosize=True,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                bearing=0,
                style='light',
                pitch=0,
                zoom=1,
            ),
        )
    }


@app.callback(
    Output('earthquake-info', 'children'),
    [Input('world-map', 'clickData')])
def display_click_data(clickData):
    if clickData is None:
        return ''

    data = clickData['points'][0]['customdata']
    print(json.dumps(data, indent=2))
    s = data['time'] / 1000.0
    time = dt.fromtimestamp(s)

    return dbc.Card(style={'textAlign': 'left'}, children=[
        dbc.CardHeader(data['title']),
        dbc.CardBody('URL: ' + str(data['detail'])),
        dbc.CardBody('Magnitutde: ' + str(data['mag'])),
        dbc.CardBody('Place: ' + str(data['place'])),
        dbc.CardBody('Time: ' + time.strftime('%Y-%m-%d %H:%M:%S'))
    ])


if __name__ == '__main__':
    app.run_server(debug=True)
