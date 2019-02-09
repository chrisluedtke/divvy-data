import datetime, requests, time

import pandas as pd


def get_data(url:str = "https://feeds.divvybikes.com/stations/stations.json"):
    r = requests.get(url)

    if r.status_code != requests.codes.ok:
        r.raise_for_status()

    r  = r.json()
    df = (pd.DataFrame(r['stationBeanList'])
            .assign(executionTime = r['executionTime']))
    df['lastCommunicationTime'] = pd.to_datetime(df.lastCommunicationTime)
    
    return df


def update_data(pre_df, dupe_cols):
    call_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        new_df = get_data()
    except requests.exceptions.HTTPError as e:
        print(f"{call_time}: {e}")
        new_df = pre_df
        diff = pd.DataFrame()
    else:
        diff = new_df.loc[~(new_df.set_index(dupe_cols)
                                  .index
                                  .isin(pre_df.set_index(dupe_cols).index))]

        if not diff.empty:
            print(f"{call_time}: Called & Updated")
        else:
            print(f"{call_time}: Called")
    finally:
        return new_df, diff


def monitor_data(interval_sec = 5):
    dupe_cols = ['id', 'availableBikes', 'availableDocks', 'status',
                 'kioskType']

    df = get_data()
    diff_log = [df.copy()]

    try:
        while True:
            df, diff = update_data(pre_df=df, dupe_cols=dupe_cols)

            if not diff.empty:
                diff_log.append(diff)

            time.sleep(interval_sec)

    except KeyboardInterrupt:
        pass

    finally:
        df = (pd.concat(diff_log, ignore_index=True)
                .sort_values(['id', 'executionTime'],
                             ascending=[True, True]))
        return df
