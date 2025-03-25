import os
import pandas as pd
from cache import cache

# base directory for data files
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# map the country iso codes
CSV_COUNTRY_ISO = {
    'Albania': 'ALB',
    'Armenia': 'ARM',
    'Austria': 'AUT',
    'Belgium': 'BEL',
    'Bulgaria': 'BGR',
    'Croatia': 'HRV',
    'Cyprus': 'CYP',
    'Czech Republic': 'CZE',
    'Czechia': 'CZE',
    'Denmark': 'DNK',
    'Estonia': 'EST',
    'Finland': 'FIN',
    'France': 'FRA',
    'Germany': 'DEU',
    'Greece': 'GRC',
    'EL': 'GRC',
    'Hungary': 'HUN',
    'Ireland': 'IRL',
    'Italy': 'ITA',
    'Latvia': 'LVA',
    'Lithuania': 'LTU',
    'Luxembourg': 'LUX',
    'Malta': 'MLT',
    'Netherlands': 'NLD',
    'Poland': 'POL',
    'Portugal': 'PRT',
    'Romania': 'ROU',
    'Slovakia': 'SVK',
    'Slovenia': 'SVN',
    'Spain': 'ESP',
    'Sweden': 'SWE',
    'UK': 'GBR',
    'United Kingdom': 'GBR'
}

def country_name_to_iso(country):
    return CSV_COUNTRY_ISO.get(country)

def iso_to_country_name(iso):
    reverse_map = {x: y for y, x in CSV_COUNTRY_ISO.items()}
    return reverse_map.get(iso, iso)

def safe_float(x): # returns 0.0 if input isn't numeric 
    try:
        val = float(x)
        return 0.0 if pd.isna(val) else val
    except Exception:
        return 0.0

# Load GDP Growth data
@cache.memoize(timeout=3600) #save data for 1 hour
def load_gdp_data():
    path = os.path.join(BASE_DIR, 'GDPGrowthData.csv') # make the file path
    df = pd.read_csv(path) # read the csv data

    # convert the columns to numeric values
    # if conversion fails, errors='coerce' will set those entries to NaN.
    df['year'] = pd.to_numeric(df['TIME_PERIOD'], errors='coerce')
    df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
    
    # create new column 'iso_alpha' by mapping the 'geo' column values to their ISO codes
    df['iso_alpha'] = df['geo'].apply(country_name_to_iso)

    # duplicate the 'geo' column into a new column called 'Country'
    df['Country'] = df['geo']
    
    df = df[['Country', 'year', 'OBS_VALUE', 'iso_alpha']] # only keep important columns in data frame
    df = df.rename(columns={'OBS_VALUE': 'gdp_value'}) # rename to increase readability

    return df

# Load GDP Per Capita data
@cache.memoize(timeout=3600)
def load_gdp_per_capita_data():
    path = os.path.join(BASE_DIR, 'GDPPerCapitaData.csv')
    df = pd.read_csv(path)
    df['year'] = pd.to_numeric(df['TIME_PERIOD'], errors='coerce')
    df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
    df['iso_alpha'] = df['geo'].apply(country_name_to_iso)
    df['Country'] = df['geo']
    df = df[['Country', 'year', 'OBS_VALUE', 'iso_alpha']]
    df = df.rename(columns={'OBS_VALUE': 'gdp_per_capita'})
    return df

# Load Health Expenditure data
@cache.memoize(timeout=3600)
def load_health_expenditure_data():
    path = os.path.join(BASE_DIR, 'HealthcareExpenditureData.csv')
    df = pd.read_csv(path)
    df['year'] = pd.to_numeric(df['TIME_PERIOD'], errors='coerce')
    df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
    df['iso_alpha'] = df['geo'].apply(country_name_to_iso)
    df = df[df['iso_alpha'].notnull()].copy()
    df = df.rename(columns={'OBS_VALUE': 'health_exp'})
    df_grouped = df.groupby(['iso_alpha', 'year'], as_index=False)['health_exp'].mean()
    df_grouped["Country"] = df_grouped["iso_alpha"].apply(iso_to_country_name)
    return df_grouped

# Load Life Expectancy data
@cache.memoize(timeout=3600)
def load_life_expectancy_data():
    path = os.path.join(BASE_DIR, 'LifeExpectancyData(1YO).csv')
    df = pd.read_csv(path)
    df['year'] = pd.to_numeric(df['TIME_PERIOD'], errors='coerce')
    df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
    df['iso_alpha'] = df['geo'].apply(country_name_to_iso)
    df = df[df['iso_alpha'].notnull()].copy()
    df = df.rename(columns={'OBS_VALUE': 'life_exp'})
    df_grouped = df.groupby(['iso_alpha', 'year'], as_index=False)['life_exp'].mean()
    df_grouped["Country"] = df_grouped["iso_alpha"].apply(iso_to_country_name)
    return df_grouped

# Load Economic Sentiment data
@cache.memoize(timeout=3600)
def load_economic_sentiment():
    path = os.path.join(BASE_DIR, 'EconomicSentimentData.csv')
    df = pd.read_csv(path)
    df['year'] = df['TIME_PERIOD'].astype(str).str[:4].astype(int)
    df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
    df['iso_alpha'] = df['geo'].apply(country_name_to_iso)
    df = df[df['iso_alpha'].notnull()].copy()
    df = df.rename(columns={'OBS_VALUE': 'econ_sentiment'})
    df_grouped = df.groupby(['iso_alpha', 'year'], as_index=False)['econ_sentiment'].mean()
    df_grouped["Country"] = df_grouped["iso_alpha"].apply(iso_to_country_name)
    return df_grouped

# Load Epidemic data
@cache.memoize(timeout=3600)
def load_epidemic_data():
    path = os.path.join(BASE_DIR, 'EpidemicData.csv')
    df_demo = pd.read_csv(path)

    def clean_country(country):
        if pd.isna(country):
            return country
        if "(" in country and ")" in country:
            start = country.find("(")
            end = country.find(")")
            return country[start+1:end].strip()
        return country.strip()

    df_demo['clean_country'] = df_demo['country_extracted'].apply(clean_country)
    european_countries = [
        'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic',
        'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary',
        'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
        'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia',
        'Spain', 'Sweden', 'United Kingdom', 'Norway', 'Switzerland'
    ]
    df_europe = df_demo[df_demo['clean_country'].isin(european_countries)].copy()
    df_europe['cases_extracted'] = pd.to_numeric(df_europe['cases_extracted'], errors='coerce')
    df_europe['date_extracted'] = pd.to_datetime(df_europe['date_extracted'], errors='coerce')
    df_europe['year'] = df_europe['date_extracted'].dt.year

    df_grouped = df_europe.groupby(['clean_country', 'year'], as_index=False)['cases_extracted'].sum()
    df_grouped['iso_alpha'] = df_grouped['clean_country'].apply(country_name_to_iso)
    df_grouped = df_grouped[df_grouped['iso_alpha'].notnull()].copy()
    df_grouped = df_grouped.rename(columns={'cases_extracted': 'epidemic'})
    return df_grouped[['iso_alpha', 'year', 'epidemic']]

# Load Employment Rate data
@cache.memoize(timeout=3600)
def load_employment_rate_data():
    path = os.path.join(BASE_DIR, 'EmploymentRateData.csv')
    df = pd.read_csv(path)
    df['year'] = pd.to_numeric(df['TIME_PERIOD'], errors='coerce')
    df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')
    df['iso_alpha'] = df['geo'].apply(country_name_to_iso)
    df['Country'] = df['geo']
    df = df[['Country', 'year', 'OBS_VALUE', 'iso_alpha']]
    df = df.rename(columns={'OBS_VALUE': 'employment_rate'})
    df_grouped = df.groupby(['iso_alpha', 'year'], as_index=False)['employment_rate'].mean()
    df_grouped["Country"] = df_grouped["iso_alpha"].apply(iso_to_country_name)
    return df_grouped

# Load Tourism data
@cache.memoize(timeout=3600)
def load_tourism_data():
    path = os.path.join(BASE_DIR, 'PercentTourismContributing.csv')
    df = pd.read_csv(path)
    df_long = df.melt(id_vars=['Country'], var_name='year', value_name='tourism_rate')
    df_long['year'] = pd.to_numeric(df_long['year'], errors='coerce')
    df_long['tourism_rate'] = pd.to_numeric(df_long['tourism_rate'], errors='coerce')
    df_long['iso_alpha'] = df_long['Country'].apply(country_name_to_iso)
    df_long = df_long[df_long['iso_alpha'].notnull()].copy()
    return df_long[['iso_alpha', 'year', 'tourism_rate', 'Country']]

# Load Tourism Nights data
@cache.memoize(timeout=3600)
def load_tourism_nights_data():
    path = os.path.join(BASE_DIR, 'TourismNights.csv')
    df = pd.read_csv(path)
    df['year'] = pd.to_numeric(df['YEAR'], errors='coerce')
    df['OBS_VALUE'] = pd.to_numeric(df['VALUE'], errors='coerce')
    df['iso_alpha'] = df['NAME'].apply(country_name_to_iso)
    df['Country'] = df['NAME']
    df = df[['Country', 'year', 'OBS_VALUE', 'iso_alpha']]
    df = df.rename(columns={'OBS_VALUE': 'tourism_nights'})
    df_grouped = df.groupby(['iso_alpha', 'year'], as_index=False)['tourism_nights'].mean()
    df_grouped["Country"] = df_grouped["iso_alpha"].apply(iso_to_country_name)
    return df_grouped
