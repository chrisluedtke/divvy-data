"""
Pulls data from:
https://www.divvybikes.com/system-data
https://s3.amazonaws.com/divvy-data/tripdata
"""
from io import BytesIO
import os
import re
import requests
from zipfile import ZipFile
from typing import List

from lxml import html
import pandas as pd

from .stations_feed import StationsFeed


STN_DT_FORM = {
    '2013': "%m/%d/%Y",  # Not labeled for quarters
    '2014_Q1Q2': None,  # xlsx file
    '2014_Q3Q4': "%m/%d/%Y %H:%M",
    '2015': None,  # no date column and not labeled for quarters
    '2016_Q1Q2': "%m/%d/%Y",
    '2016_Q3': "%m/%d/%Y",
    '2016_Q4': "%m/%d/%Y",
    '2017_Q1Q2': "%m/%d/%Y %H:%M:%S",
    '2017_Q3Q4': "%m/%d/%Y %H:%M",
}

STN_COL_MAP = {
    'latitude': 'lat',
    'longitude': 'lon',
    'dateCreated': 'online_date',
    'online date': 'online_date',
}

RD_DT_FORM = {
    '2013': "%Y-%m-%d %H:%M",  # Not labeled for quarters
    '2014_Q1Q2': "%m/%d/%Y %H:%M",
    '2014_Q3': "%m/%d/%Y %H:%M",
    '2014_Q4': "%m/%d/%Y %H:%M",
    '2015_Q1': "%m/%d/%Y %H:%M",
    '2015_Q2': "%m/%d/%Y %H:%M",
    '2015': "%m/%d/%Y %H:%M",  # Q3 labeled as month integer
    '2015_Q4': "%m/%d/%Y %H:%M",
    '2016_Q1': "%m/%d/%Y %H:%M",
    '2016': "%m/%d/%Y %H:%M",  # Q2 labeled as month integer
    '2016_Q3': "%m/%d/%Y %H:%M:%S",
    '2016_Q4': "%m/%d/%Y %H:%M:%S",
    '2017_Q1': "%m/%d/%Y %H:%M:%S",
    '2017_Q2': "%m/%d/%Y %H:%M:%S",
    '2017_Q3': "%m/%d/%Y %H:%M:%S",
    '2017_Q4': "%m/%d/%Y %H:%M",
    '2018_Q1': "%Y-%m-%d %H:%M:%S",
    '2018_Q2': "%Y-%m-%d %H:%M:%S",
    '2018_Q3': "%Y-%m-%d %H:%M:%S",
    '2018_Q4': "%Y-%m-%d %H:%M:%S",
}

RD_COL_MAP = {
    '01 - Rental Details Rental ID': 'trip_id',
    '01 - Rental Details Local Start Time': 'start_time',
    '01 - Rental Details Local End Time': 'end_time',
    '01 - Rental Details Bike ID': 'bikeid',
    '01 - Rental Details Duration In Seconds Uncapped': 'tripduration',
    '03 - Rental Start Station ID': 'from_station_id',
    '03 - Rental Start Station Name': 'from_station_name',
    '02 - Rental End Station ID': 'to_station_id',
    '02 - Rental End Station Name': 'to_station_name',
    'User Type': 'usertype',
    'Member Gender': 'gender',
    '05 - Member Details Member Birthday Year': 'birthyear',
    'stoptime': 'end_time',
    'starttime': 'start_time',
    'birthday': 'birthyear',
}


def parse_zip_urls_from_url(url):
    r = requests.get(url)
    webpage = html.fromstring(r.content)

    base_source = 'https://s3.amazonaws.com/divvy-data/tripdata/'
    urls = [url for url in set(webpage.xpath('//a/@href'))
            if (base_source in url and url.endswith('.zip'))]

    return urls


def year_lookup_to_date(yr_lookup: str) -> str:
    q_map = {
        'Q1': '03-31',
        'Q2': '06-30',
        'Q3': '09-30',
        'Q4': '12-31',
    }

    yr_l_splt = yr_lookup.split('_')
    q = yr_l_splt[-1][-2:]
    date = q_map.get(q, '12-31')
    date = f'{yr_l_splt[0]}-{date}'

    return date


def get_current_stations():
    """Pulls most recent data from Divvy JSON feed.

    Necessar because Divvy did not provide 2018 station data.
    """
    df = StationsFeed().get_current_data()
    cols = ['id', 'stationName', 'latitude', 'longitude',
            'totalDocks', 'lastCommunicationTime']
    df = df[cols].rename(columns={
        'stationName': 'name',
        'lastCommunicationTime': 'as_of_date',
        'totalDocks': 'dpcapacity'
    })
    df = df.rename(columns=STN_COL_MAP)

    return df


def process_ride_df(z, fpath, year_lookup):
    df = (pd.read_csv(z.open(fpath))
            .rename(columns=RD_COL_MAP))

    df['start_time'] = pd.to_datetime(
        df['start_time'],
        format=RD_DT_FORM.get(year_lookup, None),
        errors='coerce'
    )
    df['end_time'] = pd.to_datetime(
        df['end_time'],
        format=RD_DT_FORM.get(year_lookup, None),
        errors='coerce'
    )

    return df


def process_station_df(z, fpath, year_lookup):
    if fpath.endswith('.csv'):
        df = pd.read_csv(z.open(fpath))
    else:  # must be '.xlsx'
        df = pd.read_excel(z.open(fpath))

    df = df.rename(columns=STN_COL_MAP)
    df['as_of_date'] = year_lookup_to_date(year_lookup)
    df['as_of_date'] = pd.to_datetime(df['as_of_date'])

    if 'online_date' in df:
        df['online_date'] = pd.to_datetime(
            df['online_date'],
            format=STN_DT_FORM.get(year_lookup, None),
            errors='coerce'
        )

    return df


def combine_ride_dfs(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    dfs = (pd.concat(dfs, ignore_index=True, sort=True)
             .sort_values('start_time')
             .reset_index(drop=True))
    dfs['tripduration'] = (
        dfs.tripduration.astype(str).str.replace(',', '').astype(float)
    )

    cols = ['trip_id', 'bikeid', 'start_time', 'end_time', 'tripduration',
            'from_station_id', 'from_station_name', 'to_station_id',
            'to_station_name', 'usertype', 'gender', 'birthyear']
    dfs = dfs[[col for col in cols if col in dfs]]

    return dfs


def combine_station_dfs(dfs: List[pd.DataFrame]) -> pd.DataFrame:
    dfs = (pd.concat(dfs, ignore_index=True, sort=True)
             .sort_values(['id', 'as_of_date'])
             .reset_index(drop=True))

    # excludes ['city', 'Unnamed: 7']
    cols = ['id', 'name', 'as_of_date', 'lat', 'lon', 'dpcapacity',
            'online_date', 'landmark']
    dfs = dfs[[col for col in cols if col in dfs]]

    return dfs


def get_historical_data(years: List[str], write_to: str = '', rides=True,
                        stations=True):
    """Gathers and cleans historical Divvy data

    write_to: optional local folder path to extract zip files to
    returns: (pandas.DataFrame of rides, pandas.DataFrame of stations)
    """

    if isinstance(years, str):
        years = [years]

    ride_dfs = []
    station_dfs = []

    if not (rides or stations):
        return ride_dfs, station_dfs

    urls = parse_zip_urls_from_url('https://www.divvybikes.com/system-data')

    for url in sorted(urls):
        z_fn = url.split('/')[-1]
        z_year = re.findall(r'20\d{2}', z_fn)[0]
        if z_year not in years:
            continue

        print(url)

        r = requests.get(url)
        with ZipFile(BytesIO(r.content)) as z:
            if write_to:
                write_path = os.path.join(write_to, z_fn.replace('.zip', ''))
                z.extractall(write_path)

            for fpath in z.namelist():
                fn = fpath.split('/')[-1]
                if fn.endswith(('.csv', '.xlsx')) and not fn.startswith('.'):
                    quarter = re.findall('Q[1-4]', fn)
                    if quarter:
                        year_lookup = f"{z_year}_{''.join(quarter)}"
                    else:
                        year_lookup = z_year
                else:
                    continue

                if rides and '_trips_' in fn.lower():
                    print(fn, year_lookup)
                    df = process_ride_df(z, fpath, year_lookup)
                    ride_dfs.append(df)

                elif stations and '_stations_' in fn.lower():
                    print(fn, year_lookup)
                    df = process_station_df(z, fpath, year_lookup)
                    station_dfs.append(df)

    if rides:
        ride_dfs = combine_ride_dfs(ride_dfs)

    if stations:
        if '2018' in years:
            df = get_current_stations()
            station_dfs.append(df)

        station_dfs = combine_station_dfs(station_dfs)

    return ride_dfs, station_dfs
