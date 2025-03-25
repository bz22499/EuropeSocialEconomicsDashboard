from dash import dcc, html

# reference: https://dash.plotly.com/dash-core-components

YEARS = list(range(2015, 2025))

def get_layout():
    return html.Div([
        html.H1([ #title
            "Bivariate Map: ",
            dcc.Dropdown( # dropdowns to select variables
                id='x-variable-dropdown',
                options=[
                    {'label': 'GDP Growth', 'value': 'gdp_growth'},
                    {'label': 'GDP Per Capita', 'value': 'gdp_per_capita'}
                ],
                value='gdp_growth',
                clearable=False,
                style={
                    'width': '200px',
                    'display': 'inline-block',
                    'marginRight': '10px',
                    'fontSize': '14px'
                }
            ),
            " vs ",
            dcc.Dropdown(
                id='variable-dropdown',
                options=[
                    {'label': 'Health Expenditure', 'value': 'health'},
                    {'label': 'Life Expectancy', 'value': 'lifeexp'},
                    {'label': 'Epidemic Cases', 'value': 'epidemic'},
                    {'label': 'Economic Sentiment', 'value': 'econ'},
                    {'label': 'Employment Rate', 'value': 'employment'},
                    {'label': 'Personal Tourism (%)', 'value': 'tourism'},
                    {'label': 'Tourism Nights', 'value': 'tourism_nights'}
                ],
                value='health',
                clearable=False,
                style={
                    'width': '200px',
                    'display': 'inline-block',
                    'marginLeft': '10px',
                    'fontSize': '14px'
                }
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'flexWrap': 'wrap'}),

        # Year slider
        html.Div([
            html.Label("Select Year:", style={'marginRight': '10px'}),
            dcc.Slider(
                id='year-slider',
                min=min(YEARS),
                max=max(YEARS),
                step=1,
                marks={y: str(y) for y in YEARS},
                value=2018
            )
        ], style={'width': '60vw', 'maxWidth': '800px', 'margin': '20px 0', 'textAlign': 'left'}),

        # map + Legend side by side
        html.Div([
            dcc.Graph(id='choropleth-graph', style={'width': '45vw', 'minWidth': '300px', 'margin': '10px'}),
            dcc.Graph(id='legend-graph', style={'width': '45vw', 'minWidth': '300px', 'margin': '10px'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center', 'alignItems': 'center'})
    ])
