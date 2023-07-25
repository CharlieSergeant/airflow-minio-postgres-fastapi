import datetime
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

from pandas.core.dtypes.common import is_numeric_dtype
#from timezonefinder import TimezoneFinder
#import geocoder
import re

## Webpage stuff
def get_webpage(url):
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    return None


def get_webpage_soup(html, html_attr=None, attr_key_val=None):
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        if html_attr:
            soup = soup.find(html_attr, attr_key_val)
        return soup
    return None


def get_webpage_df(soup, header=0, table_num=0):
    if soup:
        try:
            df = pd.read_html(str(soup), header=header)[table_num]
            return df
        except Exception as e:
            print(e)
            return pd.DataFrame()
    return pd.DataFrame()


def get_next_url(base_url, start_sub, next_sub, html_attr=None, attr_key_val=None):
    start_html = get_webpage(base_url + start_sub)
    start_soup = get_webpage_soup(start_html, html_attr=html_attr, attr_key_val=attr_key_val)
    for a in start_soup.find_all('a'):
        if a.get('href') and next_sub in a.get('href'):
            return base_url + a.get('href')[1:]
    return None

def get_suburl_names_from_table(soup, sub_url, html_tag='td', attrs={'data-stat': 'boxscore_word'}):
    try:
        tablename_rows = soup.find_all(html_tag, attrs=attrs)
    except Exception:
        return []
    internalLinks = []
    for i in tablename_rows:
        if i.find('a'):
            if i.find('a').get('href') and i.find('a').get('href').startswith(sub_url):
                internalLinks.append(i.find('a').get('href').replace(sub_url, '').replace('/', '').split('.')[0])
        else:
            internalLinks.append(i.text + '_NOLINK')

    return internalLinks

def get_multi_webpage(func, urls, processes=10):
    with Pool(processes) as p:
        records = p.map(func, urls)
    return records


def get_multi_webpage_star(func, params, processes=10):
    with Pool(processes) as p:
        records = p.starmap(func, params)
    return records


## Filters and dataframe stuff
def clean_string(s):
    if isinstance(s, str):
        return re.sub("[\W_]+",'',s)
    else:
        return s

def re_alphanumspace(s):
    if isinstance(s, str):
        return re.sub("^[a-zA-Z0-9 ]*$",'',s)
    else:
        return s

def re_braces(s):
    if isinstance(s, str):
        return re.sub("[\(\[].*?[\)\]]", "", s)
    else:
        return s


def re_numbers(s):
    if isinstance(s, str):
        n = ''.join(re.findall(r'\d+', s))
        return int(n) if n != '' else n
    else:
        return s

def re_html_comments(soup):
    #soup argument can be string or bs4.beautifulSoup instance it will auto convert to string, please prefer to input as (string) than (soup) if you want highest speed
    if not isinstance(soup,str):
        soup=str(soup)
    return re.sub("(<!--.*?-->)", "", soup, flags=re.DOTALL)

def name_filter(s):
    s = clean_string(s)
    s = re_braces(s)
    s = str(s)
    s = s.replace(' ', '').lower()
    return s

def parse_website_url(url):
    url = url.replace('http://', '').replace('https://', '').replace('.0', '').replace('www.', '')
    if url[-1] != '/':
        url = f"{url}/"
    return url

def fill_numeric_and_string_cols(df,number_val=0,string_val=''):
    c = df.select_dtypes(np.number).columns
    df[c] = df[c].fillna(number_val)
    df = df.fillna(string_val)
    return df

def df_filter(df: pd.DataFrame, unique_count=1):
    df = df.dropna(axis=1, how='all')
    df = df[[c for c in list(df) if len(df[c].unique()) > unique_count]]
    return df


def df_get_prefix_cols(df, col_prefix, inverse=False):
    t_cols = [i for i in df.columns if col_prefix in i]
    return list(set(t_cols).symmetric_difference(set(df.columns))) if inverse else t_cols


def df_replace_prefix_col(df, col_prefix, replace_prefix='',skip_cols=[]):
    t_cols = [i.replace(col_prefix, replace_prefix) for i in df.columns if col_prefix in i and i not in skip_cols]
    original_cols = [i for i in df.columns if col_prefix in i and i not in skip_cols]
    df_out = df.rename(columns=dict(zip(original_cols, t_cols)))
    return df_out

def df_add_prefix_col(df, replace_prefix='',skip_cols=[]):
    t_cols = [f"{replace_prefix}{i}" for i in df.columns if i not in skip_cols]
    original_cols = [i for i in df.columns if i not in skip_cols]
    df_out = df.rename(columns=dict(zip(original_cols, t_cols)))
    return df_out


def df_rename_pivot(df, all_cols, pivot_cols, t1_prefix, t2_prefix, sub_merge_df=None):
    '''
    The reverse of a df_rename_fold
    Pivot one generic type into two prefixed column types
    Ex: team_id -> away_team_id and home_team_id
    '''
    try:
        df = df[all_cols]
        t1_cols = [t1_prefix + i for i in all_cols if i not in pivot_cols]
        t2_cols = [t2_prefix + i for i in all_cols if i not in pivot_cols]
        original_cols = [i for i in all_cols if i not in pivot_cols]

        t1_renamed_pivot_df = df.rename(columns=dict(zip(original_cols, t1_cols)))
        t2_renamed_pivot_df = df.rename(columns=dict(zip(original_cols, t2_cols)))

        if sub_merge_df is None:
            df_out = pd.merge(t1_renamed_pivot_df, t2_renamed_pivot_df, on=pivot_cols).reset_index().drop(columns='index')
        else:
            sub_merge_cols = sub_merge_df.columns.values
            t1_sub_df = pd.merge(sub_merge_df, t1_renamed_pivot_df, how='inner', left_on=[t1_prefix + i for i in pivot_cols], right_on=pivot_cols).drop(columns=pivot_cols)
            t2_sub_df = pd.merge(sub_merge_df, t2_renamed_pivot_df, how='inner', left_on=[t2_prefix + i for i in pivot_cols], right_on=pivot_cols).drop(columns=pivot_cols)
            df_out = pd.merge(t1_sub_df, t2_sub_df, on=list(sub_merge_cols))
        return df_out
    except Exception as e:
        print("--df_rename_pivot-- " +str(e))
        print(f"columns in: {df.columns}")
        print(f"shape: {df.shape}")
        return df

def df_rename_fold(df, t1_prefix, t2_prefix):
    '''
    The reverse of a df_rename_pivot
    Fold two prefixed column types into one generic type
    Ex: away_team_id and home_team_id -> team_id
    '''
    try:
        t1_all_cols = [i for i in df.columns if t2_prefix not in i]
        t2_all_cols = [i for i in df.columns if t1_prefix not in i]

        t1_cols = [i for i in df.columns if t1_prefix in i]
        t2_cols = [i for i in df.columns if t2_prefix in i]
        t1_new_cols = [i.replace(t1_prefix, '') for i in df.columns if t1_prefix in i]
        t2_new_cols = [i.replace(t2_prefix, '') for i in df.columns if t2_prefix in i]

        t1_df = df[t1_all_cols].rename(columns=dict(zip(t1_cols, t1_new_cols)))
        t2_df = df[t2_all_cols].rename(columns=dict(zip(t2_cols, t2_new_cols)))

        df_out = pd.concat([t1_df, t2_df]).reset_index().drop(columns='index')
        return df_out
    except Exception as e:
        print("--df_rename_fold-- " +str(e))
        print(f"columns in: {df.columns}")
        print(f"shape: {df.shape}")
        return df

def df_rename_dif(df,t1_prefix,t2_prefix,sub_prefix=''):
    '''
    An extension of the df_rename_pivot
    Take the difference of two prefixed column types
    Ex: away_team_turnovers - home_team_turnovers -> team_turnovers_dif
    Note: This method applies the difference to the columns and removes the two prefixed column types
    '''
    t1_cols = [i for i in df.columns if t1_prefix in i]
    t2_cols = [i for i in df.columns if t2_prefix in i]
    for t1_col, t2_col in zip(t1_cols, t2_cols):
        if is_numeric_dtype(df[t1_col]) and is_numeric_dtype(df[t2_col]):
            df[f"{t1_col.replace(t1_prefix, sub_prefix) + '_dif'}"] = df[t1_col] - df[t2_col]
    df_out = df.drop(columns=t1_cols + t2_cols)
    return df_out

def df_col_dif(a: pd.DataFrame, b: pd.DataFrame):
    return set(a.columns).symmetric_difference(set(b.columns))

def is_pandas_none(val):
    return str(val) in ["nan", "None","", "none", " ", "<NA>","NaT","NaN"]

def dataset_column_selector(df, subset, to_drop):
    not_in_col_set = []
    if subset is not None:
        for i in subset:
            if i not in df.columns:
                not_in_col_set.append(i)
        if not_in_col_set != []:
            print(f"These Columns {not_in_col_set} are not in the dataset")
            return None
        else:
            df = df[subset]
    if to_drop:
        df = df.drop(columns=to_drop)
    return df

"""
def fuzz_match(associated_teams, team, cutoff=0.7):
    team = name_filter(team)
    idx = [i for i, x in enumerate(associated_teams) if x == team]
    if idx == [] or not idx:
        print(f"No match get_teams_stadium --------- defaulting to fuzz at {cutoff} for {team}")
        fuzzy_matched_teams = difflib.get_close_matches(team, associated_teams, cutoff=cutoff)[0:2]
        idx = []
        for m in fuzzy_matched_teams:
            # applies condition for multiple indexes in list with same value
            indices = [i for i, x in enumerate(associated_teams) if x == m]
            idx.extend(indices)
    else:
        print(f"Found exact match for {team} at {idx}")

    if idx:
        matched_team = [associated_teams[i] for i in idx][0]
        return matched_team
    else:
        return None


## Geocoding
def get_geocode(address):
    '''
    Recursive GeoCode search on a comma separated address
    EX: 1600 Pennsylvania Avenue NW, Washington, DC 20500
    - 2nd search would be Washington, DC 20500
    Returns: tuple(str)
    lat, lng, country_code, address, city, zip, state
    '''
    g = geocoder.osm(address)
    if address == '' or address is None:
        return None, None, None, None, None, None, None
    if g.status == 'OK':
        res = g.json
        if 'city' in res:
            city = res['city']
        elif 'town' in res:
            city = res['town']
        elif 'suburb' in res:
            city = res['suburb']
        else:
            city = None
        if 'postal' in res:
            zipcode = res['postal']
        else:
            zipcode = None
        if 'state' not in res:
            res['state'] = None
        return res['lat'], res['lng'], res['country_code'], res['address'], city, zipcode, res['state']
    else:
        return get_geocode(','.join(address.split(',')[1:]))

def get_elevations(lats, lons, n=50):
    if n > 50:
        raise ValueError("Batch size cannot be greater than 50.")

    try:
        datasets = ','.join([
            # 'aster30m',
            'etopo1',
            # 'eudem25m',
            # 'mapzen',
            'ned10m',
            'srtm30m',
            # 'gebco2020',
            'emod2018',
        ])

        elevations = []
        for i in range(0, len(lats), n):
            batch_lats = lats[i:i + n]
            batch_lons = lons[i:i + n]
            locations = '|'.join([f'{lat},{lon}' for lat, lon in zip(batch_lats, batch_lons)])
            time.sleep(1.0) # free api
            res = requests.get(f'https://api.opentopodata.org/v1/{datasets}?locations={locations}')
            if res.status_code != 200:
                raise Exception(res.json())
            data = json.loads(res.text)

            batch_elevations = [dataset_response['elevation'] * 3.28084 if dataset_response['elevation'] is not None else None for dataset_response in data['results']]
            elevations.extend(batch_elevations)

        return elevations
    except Exception as e:
        print(e)
        return None

def get_timezones(lats, lons):
    fix_shite = {
        'America/Indiana/Indianapolis': 'America/Chicago',
        'America/Kentucky/Louisville': 'America/Chicago',
        'America/Las_Angeles': 'America/Los_Angeles',
        'America/Boise': 'America/Denver',
        'America/Detroit': 'America/Chicago',
        'America/Nassau': 'America/New_York'
    }
    tf = TimezoneFinder()
    return [fix_shite.get(tf.timezone_at(lng=lon, lat=lat), tf.timezone_at(lng=lon, lat=lat)) for lat, lon in zip(lats, lons)]

"""


def handle_column_minmax_scaling(df, col_name,min_score,max_score):
    next_score = df[col_name].values
    X_std = (next_score - next_score.min(axis=0)) / (next_score.max(axis=0) - next_score.min(axis=0))
    X_scaled = X_std * (max_score - min_score) + min_score
    df[col_name] = X_scaled
    return df

def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # calculate haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # radius of earth in km
    distance_km = c * r
    distance_miles = distance_km * 0.621371  # convert km to miles

    return distance_miles

# This is gross but it does what I want
def split_on_cim(me_str):
    '''
    Split on capital in middle
    EX: New York GiantsNew York Jets ->
    ['New York Giants', 'New York Jets']
    '''
    if isinstance(me_str, str):

        words_ind = [0]
        for i in range(1, len(me_str) - 1):
            check = ((not me_str[i - 1].isspace()) & me_str[i].isupper() & (not me_str[i + 1].isspace()))
            if check:
                words_ind.append(i)
        words_ind.append(len(me_str))
        if len(words_ind) == 2:
            return me_str
        words = []
        for i in range(len(words_ind) - 1):
            words.append(me_str[words_ind[i]:words_ind[i + 1]])
        return words
    else:
        return None


SEASON_START_MONTH = {
    'mlb': {'start': 4, 'wrap': False},
    'nba': {'start': 10, 'wrap': True},
    'ncaab': {'start': 11, 'wrap': True},
    'ncaaf': {'start': 5, 'wrap': False},
    'ncaaml': {'start': 1, 'wrap': False},
    'nfl': {'start': 9, 'wrap': False},
    'nhl': {'start': 10, 'wrap': True}
}
def _find_year_for_season(league,date=None):
    """
    Return the necessary seaons's year based on the current date.

    Since all sports start and end at different times throughout the year,
    simply using the current year is not sufficient to describe a season. For
    example, the NCAA Men's Basketball season begins in November every year.
    However, for the November and December months, the following year is used
    to denote the season (ie. November 2017 marks the start of the '2018'
    season) on sports-reference.com. This rule does not apply to all sports.
    Baseball begins and ends in one single calendar year, so the year never
    needs to be incremented.

    Additionally, since information for future seasons is generally not
    finalized until a month before the season begins, the year will default to
    the most recent season until the month prior to the season start date. For
    example, the 2018 MLB season begins in April. In January 2018, however, not
    all of the season's information is present in the system, so the default
    year will be '2017'.

    Parameters
    ----------
    league : string
        A string pertaining to the league start information as listed in
        SEASON_START_MONTH (ie. 'mlb', 'nba', 'nfl', etc.). League must be
        present in SEASON_START_MONTH.

    Returns
    -------
    int
        The respective season's year.

    Raises
    ------
    ValueError
        If the passed 'league' is not a key in SEASON_START_MONTH.
    """
    if date is None:
        today = datetime.datetime.now()
    else:
        today = pd.Timestamp(date)
        today = today.to_pydatetime()
    if league not in SEASON_START_MONTH:
        raise ValueError('"%s" league cannot be found!')
    start = SEASON_START_MONTH[league]['start']
    wrap = SEASON_START_MONTH[league]['wrap']
    if wrap and start - 1 <= today.month <= 12:
        return today.year + 1
    elif not wrap and start == 1 and today.month == 12:
        return today.year + 1
    elif not wrap and not start - 1 <= today.month <= 12:
        return today.year - 1
    else:
        return today.year