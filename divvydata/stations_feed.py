import requests
import time

import pandas as pd


class StationsFeed(object):
    """Client that pulls data from Divvy JSON feed:

    https://feeds.divvybikes.com/stations/stations.json

    Attributes:
        data:
        event_history:
    """

    def __init__(self):
        self.data = pd.DataFrame()
        self.event_history = pd.DataFrame()

    @staticmethod
    def get_current_data():
        """Pulls current data. Does not assign to an attribute."""
        feed_url = "https://feeds.divvybikes.com/stations/stations.json"
        r = requests.get(feed_url)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        r = r.json()
        df = (pd.DataFrame(r['stationBeanList'])
                .assign(callTime=r['executionTime']))
        df['lastCommunicationTime'] = pd.to_datetime(df.lastCommunicationTime)

        return df

    def update_data(self):
        """Updates `data` attribute with most recent station data."""
        self.data = StationsFeed.get_current_data()

    def monitor_event_history(self, interval_sec=5.0, runtime_sec=1000):
        """Updates `event_history` attribute with live data from  Divvy
        JSON feed. Only saves differences between updates.

        interval_sec: default 5 seconds.
        runtime_sec: default 1000 seconds. Set to None to run indefinitely.

        returns: pandas.DataFrame
        """

        self.event_history = StationsFeed.get_current_data()
        df = self.event_history.copy()

        if runtime_sec:
            end_time = time.time() + runtime_sec
        else:
            end_time = float('inf')

        try:
            while time.time() < end_time:
                query_start = time.time()

                df, diff = StationsFeed._get_monitor_update(pre_df=df)
                self.event_history = self.event_history.append(diff)

                elapsed = query_start - time.time()
                delay = interval_sec - elapsed
                if delay > 0:
                    time.sleep(delay)

        except KeyboardInterrupt:
            pass

        finally:
            return self.event_history

    @staticmethod
    def _get_monitor_update(pre_df):
        """Returns updated data difference between old and updated data"""
        call_time = time.strftime('%Y-%m-%d %H:%M:%S')

        try:
            new_df = StationsFeed.get_current_data()
        except requests.exceptions.HTTPError as e:
            print(f"{call_time}: {e}")
            new_df = pre_df
            diff = pd.DataFrame()
        else:
            dupe_cols = ['id', 'availableBikes', 'availableDocks', 'status',
                         'kioskType']
            mask = ~(new_df.set_index(dupe_cols).index
                           .isin(pre_df.set_index(dupe_cols).index))
            diff = new_df.loc[mask]

            if not diff.empty:
                print(f"{call_time}: Called & Updated")
            else:
                print(f"{call_time}: Called")
        finally:
            return new_df, diff
