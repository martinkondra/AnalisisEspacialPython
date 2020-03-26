import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import pandas as pd
from geo import *
from textMetrics import *
import subprocess
import os
import signal

interval = 5 # cada cuantos segundos actualiza
process = False
# limpio el df
df = pd.DataFrame(columns=['text', 'raw_location', 'location', 'lat', 'long', 'code', 'language'])
df.to_csv('myLocations.csv', index=False)
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1('Análisis de tweets en tiempo real', style={'textAlign': 'center'}),
    
    html.Div([
    dcc.Input(id='input-box', 
              type='text',
              placeholder='Ingresá los términos a buscar, separados por comas',
              style={'width':'105vh'}),
    html.Button('Search', id='button'),
    ], className="eight columns"),

    html.Div(id='output-container-button',
             className="eight columns",
             style={'color': 'white'}),
    
    dcc.Interval(
            id='interval-component',
            interval=interval*1000, # in milliseconds
            n_intervals=0
    ),

    html.Div([
        html.H6('Seleccioná el tipo de gráfico a generar:'),
        dcc.Dropdown(
            id='map-type',
            options=[
                {'label': 'Scatter plot', 'value': 'scatterGeo'},
                {'label': 'ChoroPleth plot', 'value': 'choroPleth'},],
            value='scatterGeo',
            searchable=False,
            clearable=False
        ),
        dcc.Graph(id='live-update-map', ),
    ], className="eight columns",
       style={'width':'125vh'}),

    html.Div([
        html.H6('Frecuencias:'),
        dcc.Dropdown(
            id='frec-type',
            options=[
                {'label': 'Hashtags', 'value': 'hashtags'},
                {'label': 'Menciones', 'value': 'menciones'},
                {'label': 'Idiomas', 'value': 'languages'}],
            value='menciones',
            searchable=False,
            clearable=False
        ),
        dcc.Graph(id='live-update-barplot')
    ], className="three columns",
       style={'width':'45vh'}),   
])

# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-map', 'figure'),
             [Input('interval-component', 'n_intervals'), 
              Input('map-type', 'value')])
def update_map(n, mapType):
    df = pd.read_csv('myLocations.csv')
    df = df[-df['location'].isnull()]
    df['wrapped'] = df['text'].str.wrap(36).str.replace('\\n','<br>')
    layout = go.Layout(
            #width=656,
            #height=1500,
            margin=dict(
                l=10,
                r=10,
                b=00,
                t=0,
                pad=4)
            )
    if mapType=='scatterGeo':
        fig = go.Figure(data=go.Scattergeo(
            lon = df['long'],
            lat = df['lat'],
            #text = df['wrapped'],
            hovertemplate =
                '<b>Lugar: </b>' + df['location'] +
                '<br><b>Texto: </b>' + df['wrapped'],
            mode = 'markers',
            marker = dict(
                size = 10,
                opacity = 0.5,
                color='Red',),
            #marker_color = df['cnt'],
            ),
            layout=layout)

    else:
        groupDf = df.groupby('code').size().to_frame('size').reset_index()
        fig = go.Figure(data=go.Choropleth(
            locations=groupDf['code'],
            z = groupDf['size'], # Data to be color-coded
            colorscale = 'Reds',
            colorbar_title = "Cantidad de menciones",
            ),
            layout=layout)
    return fig

@app.callback(Output('live-update-barplot', 'figure'),
             [Input('interval-component', 'n_intervals'), 
              Input('frec-type', 'value')])
def update_barplot(n, frecType):
    df = pd.read_csv('myLocations.csv')
    df = df[-df['location'].isnull()]
    hashtags, mentions, languages = groupCounts(df)
    if frecType=='hashtags':
        df = hashtags[::-1]
    elif frecType=='languages':
        df = languages[::-1]
    else:
        df = mentions[::-1]
    data = go.Bar(x=df.cantidad,
                  y=df.item,
                  orientation='h',
                  )
    layout = go.Layout(
                #width=300,
                #height=500,
                margin=dict(
                    l=100,
                    r=10,
                    b=10,
                    t=10,
                    pad=4)
                )
    fig = go.Figure(data=data, layout=layout)
    return fig


@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('input-box', 'value')])
def update_output(n_clicks, value):
    if value == None:
        return '_'
    else:
        runSubprocess(value)
        return 'Descargando tweets con los siguientes términos: ' + value


def runSubprocess(query):
    global process
    if process:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    origWD = os.getcwd()
    cli = 'python3 ' + origWD + '/streamLocations.py ' + query
    print(cli)
    process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    df = pd.DataFrame(columns=['text', 'raw_location', 'location', 'lat', 'long', 'code', 'language'])
    df.to_csv('myLocations.csv', index=False)

    

if __name__ == '__main__':
    app.run_server(debug=True)
