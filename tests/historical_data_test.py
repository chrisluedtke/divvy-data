import os
import sys
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest

import divvydata


class TestHistoricalData(unittest.TestCase):

    def test_get_historical_data(self):
        rcols = ['trip_id', 'bikeid', 'start_time', 'end_time', 'tripduration',
                 'from_station_id', 'from_station_name', 'to_station_id',
                 'to_station_name', 'usertype', 'gender', 'birthyear']

        scols = ['id', 'name', 'as_of_date', 'lat', 'lon', 'dpcapacity',
                 'online_date', 'landmark']

        rides, stations = divvydata.get_historical_data(years='2013')

        self.assertEqual(set(rides.columns) ^ set(rcols), set())
        self.assertEqual(set(stations.columns) ^ set(scols), set())

if __name__=='__main__':
    unittest.main()
