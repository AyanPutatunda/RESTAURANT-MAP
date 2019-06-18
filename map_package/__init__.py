from flask import Flask
import dash_bootstrap_components as dbc
import dash

server = Flask(__name__)
# add configurations and database
server.config['DEBUG'] = True

app = dash.Dash(__name__,
                server=server,
                url_base_pathname='/map/',
                external_stylesheets=[dbc.themes.LUX])
app.title = "map"
app.config['suppress_callback_exceptions'] = True

from map_package import routes
