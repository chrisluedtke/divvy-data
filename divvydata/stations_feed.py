import requests, time

import pandas as pd

class StationsFeed(object):
    """Client that pulls data from Divvy JSON feed:

    https://feeds.divvybikes.com/stations/stations.json
    """

    def __init__(self):
        self.data = pd.DataFrame()
        self.event_history = pd.DataFrame()

    @property
    def data_call_time(self):
        if self.data.empty:
            return None

        return self.data['callTime'].values[0]

    @property
    def event_history_time_span(self):
        if self.event_history.empty:
            return None

        return (self.event_history['callTime'].min(),
                self.event_history['callTime'].max())

    @staticmethod
    def get_current_data():
        """Pulls current data. Does not assign to an attribute."""
        feed_url = "https://feeds.divvybikes.com/stations/stations.json"
        r = requests.get(feed_url)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        r  = r.json()
        df = (pd.DataFrame(r['stationBeanList'])
                .assign(callTime = r['executionTime']))
        df['lastCommunicationTime'] = pd.to_datetime(df.lastCommunicationTime)

        return df

    def update_data(self):
        """Overwrites `data` attribute with most recent station data."""
        self.data = StationsFeed.get_current_data()

    @staticmethod
    def _get_diff(pre_df):
        dupe_cols = ['id', 'availableBikes', 'availableDocks', 'status',
                     'kioskType']

        call_time = time.strftime('%Y-%m-%d %H:%M:%S')

        try:
            new_df = StationsFeed.get_current_data()
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

    def monitor_data(self, interval_sec = 5, runtime_sec = 1000):
        """Listens to JSON feed and tracks events.

        interval_sec: default 5 seconds.
        runtime_sec: default 1000 seconds. Set to None to run indefinitely.

        returns: pandas.DataFrame
        """

        df = StationsFeed.get_current_data()
        diff_log = [df.copy()]

        try:
            if runtime_sec:
                end_time = time.time() + runtime_sec
            else:
                end_time = float('inf')

            while time.time() < end_time:
                query_start = time.time()

                df, diff = StationsFeed._get_diff(pre_df=df)
                if not diff.empty:
                    diff_log.append(diff)

                elapsed = query_start - time.time()
                delay = interval_sec - elapsed
                if delay > 0:
                    time.sleep(delay)

        except KeyboardInterrupt:
            pass

        finally:
            df = (pd.concat(diff_log, ignore_index=True)
                    .sort_values(['id', 'callTime'],
                                 ascending=[True, True]))

            self.event_history = df
