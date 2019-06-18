import json
import csv
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from map_package import app

from dash.dependencies import Input, Output, State

import surprise
from surprise import dump

preds, model = dump.load('finalmodel')

colors = {
    'background': '#FFFFFF',
    'text': '#0074D9'
}

with open('map_package/dashdata.json') as f:
    dash_data_dict = json.load(f)

# full, restaurant, model
# rating_count, reviewsperbusiness, reviewsperuser

categories = list(dash_data_dict.keys())

with open('finalbusinessesindexed.json') as f:
    businesses = json.load(f)

with open('finaldata.csv', 'r') as f:
    reader = csv.reader(f)
    reviews = list(reader)

def find(f, seq):
    for item in seq:
        if f(item):
            return item

def get_info(iid):
    return find(lambda b: iid == b['id'], businesses)

def get_reviewed_restaurants(uid, desc=True):
    userreviews = list(filter(lambda r: r[0] == str(uid), reviews))
    ratings = [r[2] for r in userreviews]
    restaurants = list(map(lambda r: get_info(int(r[1])), userreviews))
    names = [r['name'] for r in restaurants]
    if desc==True:
        return sorted(list(zip(names, ratings)), reverse=True, key=lambda x: x[1])
    return sorted(list(zip(names, ratings)), key=lambda x: x[1])

def get_n_preds(uid, n):
    ratings = []
    for i in range(1, 73101):
        pred = model.predict(str(uid), str(i))
        ratings.append((int(pred.iid), pred.est))
    ratingsdesc = sorted(ratings, reverse=True, key=lambda x: x[1])[:n]
    namedratings = [(get_info(r[0])['name'], r[1], get_info(r[0])['latitude'], get_info(r[0])['longitude']) for r in ratingsdesc]
    return namedratings



header = rowHeading = html.Div(
    [   
        dbc.Row(dbc.Col(html.H3("TOP RESTAURANT MAP", style={'textAlign': 'center','padding-bottom':20,'padding-top':20,'font-style': 'italic','font-size': 40,'color': '#4400B2'})))
        ]
)

image = html.Div(html.P(),className="container-fluid",style={'textAlign':'center'}
)
rowHeading = html.Div(
    [   
        dbc.Row( html.P(),id = 'userid-selected',style={'padding-top':20}),
        dbc.Row(dbc.Col(html.H3("Users' Reviews and Recommendations", style={'textAlign': 'center', 'color': '#0074D9','padding-top':60,'font-style': 'italic','color': '#4400B2'}))),
        dbc.Row(dbc.Col(dcc.Slider(
					id='userid-slider',
					min=1,
					max=81415,
					value=1,
                    step=100,
                    marks={1: '1', 10000: '10000', 20000: '20000', 30000: '30000',
                    40000: '40000', 50000: '50000', 60000: '60000', 70000: '70000',
                    81415: '81415'}
				), width={"size": 6, "offset": 3}
            )
        ),
        dbc.Row( html.Img(src='http://ichuli.africa/wp-content/uploads/2018/01/UIUC_Logo_University_of_Illinois_at_Urbana-Champaign.jpg'),style={'padding-top':60},className="justify-content-md-center"),
        
        
    ],className="container",style={'textAlign':'center'}
)





app.layout = html.Div(style={'backgroundColor': colors['background'], 'font-family': 'verdana'}, children=[
    header,
    image,
    rowHeading,


    html.H1('Exploratory Data Analysis', style={'textAlign': 'center', 'padding':20}),

    
    html.H3('Looking into the Raw Data', style={
        'textAlign': 'center',
        'padding-bottom':30
    }),

    
    dbc.Row(
            [
                dbc.Col(html.Div([
                    html.H5('1. Division of Star Ratings', style={'textAlign': 'center'}),
                    dcc.Dropdown(
                        id='star-ratings-distribution',
                        options=list(map(lambda c: {'label': c.capitalize(), 'value': c}, categories)),
                        value="full"
                    ),
                    html.Div(id='output-stars')
                ]),),
                dbc.Col( html.Div([
                    html.H5('2. Division of Number of Reviews per Business', style={'textAlign': 'center'},className="heading"),
                    dcc.Dropdown(
                        id='business-reviews-distribution',
                        options=list(map(lambda c: {'label': c.capitalize(), 'value': c}, categories)),
                        value="full"
                    ),

                    html.Div(id='output-rpb')
                ]),),
                dbc.Col(html.Div([
                    html.H5('3. Division of Number of Reviews per User', style={'textAlign': 'center'},className="heading"),
                    dcc.Dropdown(
                        id='user-reviews-distribution',
                        options=list(map(lambda c: {'label': c.capitalize(), 'value': c}, categories)),
                        value="full"
                    ),

                    html.Div(id='output-rpu')
                ])),
            ]
        ),
    ],className="main-content")

@app.callback(
	Output('userid-selected', 'children'),
	[Input('userid-slider','value')])
def update_userid(value):
    reviews = get_reviewed_restaurants(value)
    n = len(reviews)
    recs = get_n_preds(value, n)
    htmls = [dbc.ListGroupItem(reviews[i][0]+': '+reviews[i][1]) for i in range(n)]
    urls = ['http://www.google.com/maps/place/'+str(recs[i][2])+','+str(recs[i][3]) for i in range(n)]
    preds = [dbc.ListGroupItem([recs[i][0]+': '+str(round(recs[i][1],2))+' ', html.A('(map)', href=urls[i])]) for i in range(n)]
    return [
        html.Div(children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("{0} User Reviews".format(value)),
                        dbc.ListGroup(htmls)
                    ]
                ),
            )
            ] 
        ,className="col-md-6"),

        html.Div(children=[
             dbc.Card(
                dbc.CardBody(
                    [
                        html.H4('Recommendations {0} User'.format(value)),
                        dbc.ListGroup(preds)
                    ]
                ),
            )
            ] , className="col-md-6")
    ]

@app.callback(Output('output-stars', 'children'),
              [Input('star-ratings-distribution', 'value')])
def show_stars(value):
    stuff = dict(sorted(dash_data_dict[value]['rating_count'].items()))
    x = [float(k) for k in stuff.keys()]
    y = list(stuff.values())
    return html.Div([dcc.Graph(
        id='stars',
        figure={
            'data': [{'x': x, 'y': y, 'type': 'bar', 'marker': {'color': '#01FF70'}}],
            'layout': {
                #'title': 'Distribution of Star Ratings: ' + str(value).capitalize(),
                'margin': {'l': 30,'r': 30,'b': 30,'t': 30},
                'legend': {'x': 1, 'y': 1}
            }})])

@app.callback(Output('output-rpb', 'children'),
              [Input('business-reviews-distribution', 'value')])
def show_reviews_businesses(value):
    stuff = dash_data_dict[value]['reviewsperbusiness']
    return html.Div([dcc.Graph(
        id='businesses',
        figure={
            'data': [{'x': stuff, 'type': 'histogram', 'marker': {'color': '#FF851B'}}],
            'layout': {
                #'title': 'Distribution of Reviews Per Business: ' + str(value).capitalize(),
                'margin': {'l': 30,'r': 30,'b': 30,'t': 30},
                'legend': {'x': 1, 'y': 1}
            }})])

@app.callback(Output('output-rpu', 'children'),
              [Input('user-reviews-distribution', 'value')])
def show_reviews_businesses(value):
    stuff = dash_data_dict[value]['reviewsperuser']
    return html.Div([dcc.Graph(
        id='users',
        figure={
            'data': [{'x': stuff, 'type': 'histogram', 'marker': {'color': '#001f3f'}}],
            'layout': {
                #'title': 'Distribution of Reviews Per User: ' + str(value).capitalize(),
                'margin': {'l': 30,'r': 30,'b': 30,'t': 30},
                'legend': {'x': 1, 'y': 1}
            }})])



