# Six Years of Chicago Bikeshare

The best way to see any city is by bicycle. And yes, I am including those three brutal months of Chicago winter. Even as temperatures approached -50 degrees last week, our bikeshare logged [over 190 trips](https://twitter.com/DivvyBikes/status/1091398529975836673).

Our blissfully flat terrain, lakefront paths, and bike infrastructure investments landed us Bicycling Magazines [most bike-friendly city in the country](https://www.bicycling.com/news/a20048181/the-50-best-bike-cities-of-2016/) (6th in [2018](https://www.bicycling.com/culture/a23676188/best-bike-cities-2018/)). This past December, Chicago completed a [$12 million project](https://www.chicagoparkdistrict.com/parks-facilities/lakefront-trail) to repave and separate 18 miles of lakefront bike path from its pedestrian counterpart. Next month, another massive [$60 million project](http://www.navypierflyover.com/) will wrap to ferry cyclists and pedestrians peacefully over the highway intersections near Navy Pier.

With all this excitement for Chicago's cyclist future, I devoted my past week to a thorough shakedown of our bikeshare's [public datasets](https://www.divvybikes.com/system-data). You can find the code for this analysis on  [GitHub](https://github.com/chrisluedtke/divvy-data-analysis), including a [notebook](https://nbviewer.jupyter.org/github/chrisluedtke/divvy-data-analysis/blob/master/notebook.ipynb) that steps through my thought process.

## Data Sourcing
I wrote up [a python package](https://github.com/chrisluedtke/divvy-data-analysis/tree/master/divvy) to load the data neatly:
``` python
import pandas as pd

import divvy

rides, stations = divvy.historical_data.get_data(
    year=[str(_) for _ in range(2013,2019)],
    rides=True,
    stations=True
)

rides.to_pickle('data/rides.pkl')
stations.to_pickle('data/stations.pkl')
```

Divvy's data come in `zip` files grouped by quarter. Columns and date formats were not standardized across files, so I manually wrote them into the loading process.

Most challenging, the ride tables don't include geographic coordinates for ride origin and destination. That information is tied to stations, which are contained in their own files. Divvy also didn't provide station information at all in 2018, so I integrated data from their [live json station feed](https://feeds.divvybikes.com/stations/stations.json) to get the most recent locations.

After merging station tables together, I discovered stations had been physically moved while maintaining the same row-level ID. This greatly reduces the certainty of geographic analysis, as I can only be certain of a station's location at the end of the quarter on which the data were published. I calculated the geographic distance between these movements and dropped elements below a ~50 meter precision level.
```
stn_id   latitude  longitude          online_date     source
     2  41.872293 -87.624091                  NaN       2015
     2  41.881060 -87.619486  2013-06-10 10:43:46  2017_Q1Q2
     2  41.876393 -87.620328  2013-06-10 10:43:00  2017_Q3Q4
```
Here's a map of all the stations that moved:

"moved_stations.html"

#### Trip Records
With the data cleaned as thoroughly as possible, the beauty in the information began to shine through. There are never-ending lines of inquiry one may follow in this data.

For starters, the data comprise **17.5 million trips**, of a median 11.7 minutes duration. A typical bike has been ridden 2.8 thousand times.

<<rides histogram>>

<<rides per quarter>>

Farthest ridden bike: 10.5 thousand kilometers by haversine distance.

<<map of bike length>>

<<video>>

<<Winter vs Summer plot>>
split plot from here: https://nbviewer.jupyter.org/github/python-visualization/folium/blob/master/examples/Plugins.ipynb
