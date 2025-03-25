import numpy as np
import plotly.express as px
from data_loaders import (
    load_gdp_data,
    load_gdp_per_capita_data,
    load_health_expenditure_data,
    load_life_expectancy_data,
    load_economic_sentiment,
    load_epidemic_data,
    load_employment_rate_data,
    load_tourism_data,
    load_tourism_nights_data,
    safe_float,
    iso_to_country_name
)

#secondary ranges for datasets (y-axis)
def get_secondary_range(dataset):
    ranges = {
        'health': (0, 10000, "Health Expenditure"),
        'lifeexp': (50, 90, "Life Expectancy"),
        'epidemic': (0, 300, "Epidemic Cases"),
        'econ': (50, 150, "Economic Sentiment"),
        'employment': (50, 100, "Employment Rate"),
        'tourism': (0, 100, "Personal Tourism (%)"),
        'tourism_nights': (0, 500000000, "Tourism Nights")
    }
    return ranges.get(dataset, (0, 1, "Secondary Value"))

# Bilinear Interpolation - GPT GENERATED!!!!
def bilinear_interpolate(x, y, c00, c10, c01, c11):
    r = (c00[0]*(1 - x)*(1 - y) + c10[0]*x*(1 - y) +
         c01[0]*(1 - x)*y + c11[0]*x*y)
    g = (c00[1]*(1 - x)*(1 - y) + c10[1]*x*(1 - y) +
         c01[1]*(1 - x)*y + c11[1]*x*y)
    b = (c00[2]*(1 - x)*(1 - y) + c10[2]*x*(1 - y) +
         c01[2]*(1 - x)*y + c11[2]*x*y)
    return (int(round(r)), int(round(g)), int(round(b)))

# Compute final color for a given data point
def compute_final_color(x_val, other, x_var='gdp_growth', secondary='health'):
    # Normalize x based on chosen x_var
    if x_var == 'gdp_growth':
        # Assume GDP Growth is in range -10 to 10
        x_norm = (x_val + 10) / 20.0
    elif x_var == 'gdp_per_capita':
        # Now assume GDP Per Capita is in range 0 to 90,000 (Euro per capita)
        x_norm = x_val / 90000.0
    else:
        x_norm = 0
    x_norm = min(max(x_norm, 0), 1)
    
    # Normalize y from secondary variable range
    other_min, other_max, _ = get_secondary_range(secondary)
    y_norm = (other - other_min) / (other_max - other_min)
    y_norm = min(max(y_norm, 0), 1)
    
    # Define corners:
    # Bottom-left = white, bottom-right = blue,
    # Top-left = red, top-right = magenta.
    c00 = (255, 255, 255)
    c10 = (0, 0, 255)
    c01 = (255, 0, 0)
    c11 = (255, 0, 255)
    
    (r, g, b) = bilinear_interpolate(x_norm, y_norm, c00, c10, c01, c11)
    r = min(max(r, 0), 255)
    g = min(max(g, 0), 255)
    b = min(max(b, 0), 255)
    return f'#{r:02x}{g:02x}{b:02x}'

# Create the 2D legend figure.
# Now accepts x_var to update the x-axis label and ticks.
def create_2d_legend_figure(x_var, user_var=''):
    # Define the same corner colors as above.
    c00 = (255, 255, 255)  # bottom-left: white
    c10 = (0, 0, 255)      # bottom-right: blue
    c01 = (255, 0, 0)      # top-left: red
    c11 = (255, 0, 255)    # top-right: magenta

    secondary_min, secondary_max, secondary_label = get_secondary_range(user_var)
    
    # Determine x-axis label and ticks based on x_var.
    if x_var == 'gdp_growth':
        x_label = "GDP Growth (%)"
        x_ticks_actual = [-10, -5, 0, 5, 10]
        x_ticks_norm = [(val + 10) / 20 for val in x_ticks_actual]
    elif x_var == 'gdp_per_capita':
        x_label = "GDP Per Capita (Euro)"
        # New range: 0 to 90,000; set 5 tick marks.
        x_ticks_actual = [0, 22500, 45000, 67500, 90000]
        x_ticks_norm = [val / 90000 for val in x_ticks_actual]
    else:
        x_label = "X Value"
        x_ticks_actual = [0, 0.25, 0.5, 0.75, 1]
        x_ticks_norm = x_ticks_actual

    grid_size = 100
    x_vals = np.linspace(0, 1, grid_size)
    y_vals = np.linspace(0, 1, grid_size)
    img = np.zeros((grid_size, grid_size, 3), dtype=np.uint8)
    for i, x_norm in enumerate(x_vals):
        for j, y_norm in enumerate(y_vals):
            row_index = j  # so y=0 => bottom row when origin='lower'
            img[row_index, i, :] = bilinear_interpolate(x_norm, y_norm, c00, c10, c01, c11)

    fig = px.imshow(
        img,
        origin='lower',
        x=x_vals,
        y=y_vals,
        labels=dict(x=x_label, y=secondary_label)
    )
    fig.update_xaxes(tickmode='array', tickvals=x_ticks_norm, ticktext=[str(val) for val in x_ticks_actual])
    
    y_ticks_actual = np.linspace(secondary_min, secondary_max, 5)
    y_ticks_norm = [(val - secondary_min) / (secondary_max - secondary_min) for val in y_ticks_actual]
    fig.update_yaxes(tickmode='array', tickvals=y_ticks_norm, ticktext=[f'{val:.0f}' for val in y_ticks_actual])
    
    fig.update_layout(
        title="Continuous 2D Legend (Blended Axes)",
        showlegend=False,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    return fig

# Create the bivariate map figure.
def create_bivariate_map(x_var, secondary_var, year):
    # Load baseline data based on x_var.
    if x_var == 'gdp_growth':
        baseline_data = load_gdp_data()
        base_col = "gdp_value"
        base_label = "GDP Growth (%)"
    elif x_var == 'gdp_per_capita':
        baseline_data = load_gdp_per_capita_data()
        base_col = "gdp_per_capita"
        base_label = "GDP Per Capita (Euro)"
    else:
        return px.choropleth(title="No data available.")
    
    # Load secondary data for the y-axis.
    if secondary_var == 'health':
        secondary_data = load_health_expenditure_data()
        sec_col = "health_exp"
        sec_label = "Health Expenditure"
    elif secondary_var == 'lifeexp':
        secondary_data = load_life_expectancy_data()
        sec_col = "life_exp"
        sec_label = "Life Expectancy"
    elif secondary_var == 'epidemic':
        secondary_data = load_epidemic_data()
        sec_col = "epidemic"
        sec_label = "Epidemic Cases"
    elif secondary_var == 'econ':
        secondary_data = load_economic_sentiment()
        sec_col = "econ_sentiment"
        sec_label = "Economic Sentiment"
    elif secondary_var == 'employment':
        secondary_data = load_employment_rate_data()
        sec_col = "employment_rate"
        sec_label = "Employment Rate"
    elif secondary_var == 'tourism':
        secondary_data = load_tourism_data()
        sec_col = "tourism_rate"
        sec_label = "Personal Tourism (%)"
    elif secondary_var == 'tourism_nights':
        secondary_data = load_tourism_nights_data()
        sec_col = "tourism_nights"
        sec_label = "Tourism Nights"
    else:
        return px.choropleth(title="No data available.")
    
    # Filter by year and merge.
    baseline_year = baseline_data[baseline_data['year'] == year].copy()
    baseline_year = baseline_year.rename(columns={"Country": "Country_baseline"})
    secondary_year = secondary_data[secondary_data['year'] == year].copy()
    secondary_year = secondary_year.rename(columns={"Country": "Country_secondary"})
    df_merged = baseline_year.merge(secondary_year, on=['iso_alpha', 'year'], how='inner')
    
    if df_merged.empty:
        df_base = baseline_year.copy()
        df_base["color"] = "lightgrey"
        df_base[base_col] = df_base[base_col].apply(safe_float)
        df_base[sec_col] = None
        df_base["Country"] = df_base["Country_baseline"]
        fig = px.choropleth(
            df_base,
            locations='iso_alpha',
            color='color',
            hover_name='Country',
            custom_data=[base_col, sec_col],
            color_discrete_map={"lightgrey": "lightgrey"},
            scope='europe',
            title=f"Bivariate Map: {base_label} vs. {sec_label} ({year})"
        )
        fig.update_traces(hovertemplate=f'<b>%{{hovertext}}</b><br>{base_label}: %{{customdata[0]}}<br>{sec_label}: N/A<extra></extra>')
        fig.update_layout(showlegend=False)
        return fig

    # Process merged data.
    df_merged["Country"] = df_merged["Country_baseline"]
    df_merged[base_col] = df_merged[base_col].apply(safe_float)
    df_merged[sec_col] = df_merged[sec_col].apply(safe_float)
    
    # Compute the color for each row.
    df_merged["color"] = df_merged.apply(
        lambda row: compute_final_color(row[base_col], row[sec_col], x_var=x_var, secondary=secondary_var),
        axis=1
    )
    
    fig = px.choropleth(
        df_merged,
        locations='iso_alpha',
        color='color',
        hover_name='Country',
        custom_data=[base_col, sec_col],
        color_discrete_map={c: c for c in df_merged["color"].unique()},
        scope='europe',
        title=f"Bivariate Map: {base_label} vs. {sec_label} ({year})"
    )
    fig.update_traces(hovertemplate=f'<b>%{{hovertext}}</b><br>{base_label}: %{{customdata[0]}}<br>{sec_label}: %{{customdata[1]}}<extra></extra>')
    fig.update_layout(showlegend=False)
    return fig
