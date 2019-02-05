import io, re, requests, zipfile
from typing import List

from lxml import html
import pandas as pd

__all__ = [
    'get_rides',
    'get_stations'
]

def get_rides(year, write_to:str = None):
#     cols = ['trip_id', 'start_time', 'end_time', 'bikeid', 'tripduration',
#             'from_station_id', 'from_station_name', 'to_station_id',
#             'to_station_name', 'usertype', 'gender', 'birthyear']

    col_maps = {
        '2018':{
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
            '05 - Member Details Member Birthday Year':'birthyear'
        },
        '2016':{
            'stoptime':'end_time',
            'starttime':'start_time',
        }
    }

    date_forms = {
        '2016':{
            'Q1':"%m/%d/%Y %H:%M",
            'MO':"%m/%d/%Y %H:%M", # Month digit used in name
            'Q3':"%m/%d/%Y %H:%M:%S",
            'Q4':"%m/%d/%Y %H:%M:%S",
        },
        '2017':{
            'Q1':"%m/%d/%Y %H:%M:%S",
            'Q2':"%m/%d/%Y %H:%M:%S",
            'Q3':"%m/%d/%Y %H:%M:%S",
            'Q4':"%m/%d/%Y %H:%M",
        },
        '2018':{
            'Q1':"%Y-%m-%d %H:%M:%S",
            'Q2':"%Y-%m-%d %H:%M:%S",
            'Q3':"%Y-%m-%d %H:%M:%S",
            'Q4':"%Y-%m-%d %H:%M:%S",
        }
    }

    if isinstance(year, str):
        year = [year]

    dfs = []

    r = requests.get('https://www.divvybikes.com/system-data')
    webpage = html.fromstring(r.content)

    base_source = 'https://s3.amazonaws.com/divvy-data/tripdata/'
    for url in set(webpage.xpath('//a/@href')):
        if not all(_ in url for _ in [base_source, '.zip']):
            continue

        z_year = re.findall(r'\d{4}', url.split('/')[-1])[0]
        if not z_year in year:
            continue

        print(url)

        r = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            if write_to:
                file_name = (url.split('/')[-1]).split('.')[0]
                z.extractall(f"data/{file_name}")

            for fn in z.namelist():
                if not (fn[-4:]=='.csv' and
                        '_Trips_' in fn.split('/')[-1] and
                        'MACOSX' not in fn):
                    continue

                quarter = re.findall(r'(Q\d)', fn.split('/')[-1])
                if quarter:
                    quarter = quarter[0]
                else:
                    quarter = 'MO'

                print(fn, z_year, quarter)
                df = pd.read_csv(z.open(fn))

                if col_maps.get(z_year):
                    df = df.rename(columns=col_maps.get(z_year))

                df['start_time'] = pd.to_datetime(
                    df['start_time'], format=date_forms[z_year][quarter],
                    errors='coerce'
                )

                dfs.append(df)

    return pd.concat(dfs)


def get_stations(year, write_to:str = None):
#     cols = ['trip_id', 'start_time', 'end_time', 'bikeid', 'tripduration',
#             'from_station_id', 'from_station_name', 'to_station_id',
#             'to_station_name', 'usertype', 'gender', 'birthyear']
    date_forms = {
        '2016':{
            'Q1':"%m/%d/%Y %H:%M",
            'MO':"%m/%d/%Y %H:%M", # Month digit used in name
            'Q3':"%m/%d/%Y %H:%M:%S",
            'Q4':"%m/%d/%Y %H:%M:%S",
        },
        '2017':{
            'Q1':"%m/%d/%Y %H:%M:%S",
            'Q2':"%m/%d/%Y %H:%M:%S",
            'Q3':"%m/%d/%Y %H:%M:%S",
            'Q4':"%m/%d/%Y %H:%M",
        },
        '2018':{
            'Q1':"%Y-%m-%d %H:%M:%S",
            'Q2':"%Y-%m-%d %H:%M:%S",
            'Q3':"%Y-%m-%d %H:%M:%S",
            'Q4':"%Y-%m-%d %H:%M:%S",
        }
    }

    if isinstance(year, str):
        year = [year]

    dfs = []

    r = requests.get('https://www.divvybikes.com/system-data')
    webpage = html.fromstring(r.content)

    base_source = 'https://s3.amazonaws.com/divvy-data/tripdata/'
    for url in set(webpage.xpath('//a/@href')):
        if not all(_ in url for _ in [base_source, '.zip']):
            continue

        z_year = re.findall(r'\d{4}', url.split('/')[-1])[0]
        if not z_year in year:
            continue

        print(url)

        r = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            if write_to:
                file_name = (url.split('/')[-1]).split('.')[0]
                z.extractall(f"data/{file_name}")

            for fn in z.namelist():
                if not (fn[-4:]=='.csv' and
                        '_Stations_' in fn.split('/')[-1] and
                        'MACOSX' not in fn):
                    continue

                quarter = re.findall(r'(Q\d)', fn.split('/')[-1])
                if quarter:
                    quarter = quarter[0]
                else:
                    quarter = 'MO'

                print(fn, z_year, quarter)
                df = pd.read_csv(z.open(fn))
                df = df.rename(columns={
                    'dateCreated':'online_date',
                    'online date':'online_date',
                })

                dfs.append(df)

    df = (pd.concat(dfs)
            .drop(columns=['city', 'Unnamed: 7', 'landmark']))
    return df
