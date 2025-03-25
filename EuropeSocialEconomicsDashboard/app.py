import dash
from dash import Input, Output
from layout import get_layout
from color_logic import create_bivariate_map, create_2d_legend_figure
from cache import cache  # import the shared cache

from flask import Flask

# create a Flask server and a Dash app that uses it
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

# initialise the cache with the Flask server and configuration
cache.init_app(server, config={'CACHE_TYPE': 'simple'})

app.layout = get_layout()

@app.callback(
    Output('choropleth-graph', 'figure'),
    [Input('variable-dropdown', 'value'),
     Input('x-variable-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_bivariate_map_callback(secondary_var, x_var, year):
    return create_bivariate_map(x_var, secondary_var, year)

@app.callback(
    Output('legend-graph', 'figure'),
    [Input('x-variable-dropdown', 'value'),
     Input('variable-dropdown', 'value')]
)
def update_legend_callback(x_var, secondary_var):
    return create_2d_legend_figure(x_var, secondary_var)

if __name__ == "__main__":
    app.run_server(debug=True)
