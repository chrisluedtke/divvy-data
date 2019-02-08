import io, os, re, requests, zipfile
from typing import List

from lxml import html
import pandas as pd

from . import stations_feed

__all__ = [
    'get_data',
]

STN_DT_FORM = {
    '2013': "%m/%d/%Y", # Not labeled for quarters
    # '2014_Q1Q2': '', # xlsx file
    '2014_Q3Q4': "%m/%d/%Y %H:%M",
    # '2015': '', # no date column and not labeled for quarters
    '2016_Q1Q2':"%m/%d/%Y",
    '2016_Q3':"%m/%d/%Y",
    '2016_Q4':"%m/%d/%Y",
    '2017_Q1Q2':"%m/%d/%Y %H:%M:%S",
    '2017_Q3Q4':"%m/%d/%Y %H:%M",
}

RD_DT_FORM = {
    '2013':"%Y-%m-%d %H:%M", # Not labeled for quarters
    '2014_Q1Q2':"%m/%d/%Y %H:%M",
    '2014_Q3':"%m/%d/%Y %H:%M",
    '2014_Q4':"%m/%d/%Y %H:%M",
    '2015_Q1':"%m/%d/%Y %H:%M",
    '2015_Q2':"%m/%d/%Y %H:%M",
    '2015':"%m/%d/%Y %H:%M", # Q3 labeled as month integer
    '2015_Q4':"%m/%d/%Y %H:%M",
    '2016_Q1':"%m/%d/%Y %H:%M",
    '2016':"%m/%d/%Y %H:%M", # Q2 labeled as month integer
    '2016_Q3':"%m/%d/%Y %H:%M:%S",
    '2016_Q4':"%m/%d/%Y %H:%M:%S",
    '2017_Q1':"%m/%d/%Y %H:%M:%S",
    '2017_Q2':"%m/%d/%Y %H:%M:%S",
    '2017_Q3':"%m/%d/%Y %H:%M:%S",
    '2017_Q4':"%m/%d/%Y %H:%M",
    '2018_Q1':"%Y-%m-%d %H:%M:%S",
    '2018_Q2':"%Y-%m-%d %H:%M:%S",
    '2018_Q3':"%Y-%m-%d %H:%M:%S",
    '2018_Q4':"%Y-%m-%d %H:%M:%S",
}

RD_COL_MAP = {
    '01 - Rental Details Rental ID':'trip_id',
    '01 - Rental Details Local Start Time':'start_time',
    '01 - Rental Details Local End Time':'end_time',
    '01 - Rental Details Bike ID':'bikeid',
    '01 - Rental Details Duration In Seconds Uncapped':'tripduration',
    '03 - Rental Start Station ID':'from_station_id',
    '03 - Rental Start Station Name':'from_station_name',
    '02 - Rental End Station ID':'to_station_id',
    '02 - Rental End Station Name':'to_station_name',
    'User Type':'usertype' ,
    'Member Gender':'gender',
    '05 - Member Details Member Birthday Year':'birthyear',
    'stoptime':'end_time',
    'starttime':'start_time',
    'birthday':'birthyear'
}


def get_data(year, write_to:str = None, rides=True, stations=True):
    """
    Returns (pd.DataFrame of rides, pd.DataFrame of stations)

    write_to: optional full folder path to extract zip files
    """
#     cols = ['trip_id', 'start_time', 'end_time', 'bikeid', 'tripduration',
#             'from_station_id', 'from_station_name', 'to_station_id',
#             'to_station_name', 'usertype', 'gender', 'birthyear']
    if isinstance(year, str):
        year = [year]

    ride_dfs = []
    station_dfs = []

    if not (rides or stations):
        return (ride_dfs, station_dfs)

    r = requests.get('https://www.divvybikes.com/system-data')
    webpage = html.fromstring(r.content)

    base_source = 'https://s3.amazonaws.com/divvy-data/tripdata/'
    urls = [url for url in set(webpage.xpath('//a/@href'))
            if (base_source in url and url.endswith('.zip'))]

    for url in sorted(urls):
        z_fn = url.split('/')[-1]
        z_year = re.findall(r'\d{4}', z_fn)[0]
        if z_year not in year:
            continue

        print(url)

        r = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
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
                    df = (pd.read_csv(z.open(fpath))
                            .rename(columns=RD_COL_MAP))

                    df['start_time'] = pd.to_datetime(
                        df['start_time'], format=RD_DT_FORM[year_lookup],
                        errors='coerce'
                    )
                    df['end_time'] = pd.to_datetime(
                        df['end_time'], format=RD_DT_FORM[year_lookup],
                        errors='coerce'
                    )

                    ride_dfs.append(df)

                elif stations and '_stations_' in fn.lower():
                    print(fn, year_lookup)
                    if fn.endswith('.csv'):
                        df = pd.read_csv(z.open(fpath))
                    elif fn.endswith('.xlsx'):
                        df = pd.read_excel(z.open(fpath))

                    df = df.rename(columns={
                        'dateCreated':'online_date',
                        'online date':'online_date',
                    })

                    df['source'] = year_lookup

                    if STN_DT_FORM.get(year_lookup):
                        df['online_date'] = pd.to_datetime(
                            df['online_date'], format=STN_DT_FORM[year_lookup],
                            errors='coerce'
                        )
                    else:
                        print('Could not lookup date format')

                    station_dfs.append(df)

    if ride_dfs:
        ride_dfs = (pd.concat(ride_dfs, ignore_index=True, sort=True)
                      .sort_values('start_time'))
        ride_dfs['tripduration'] = (ride_dfs.tripduration.astype(str)
                                                         .str
                                                         .replace(',', '')
                                                         .astype(float))
    if station_dfs:
        if '2018' in year:
            station_feed = stations_feed.get_data()
            cols = ['id', 'latitude', 'longitude',
                    'stationName', 'lastCommunicationTime']
            station_feed = station_feed[cols].rename(columns={
                'stationName':'name',
                'lastCommunicationTime':'source'
            })
            station_feed['source'] = station_feed.source.dt.strftime("%Y-%m-%d")
            station_dfs.append(station_feed)

        station_dfs = (pd.concat(station_dfs, ignore_index=True, sort=True)
                         .sort_values(['id', 'source', 'online_date']))

        drop_cols = ['city', 'Unnamed: 7', 'landmark']
        keep_cols = [_ for _ in station_dfs if _ not in drop_cols]
        station_dfs = station_dfs[keep_cols]

    return (ride_dfs, station_dfs)
