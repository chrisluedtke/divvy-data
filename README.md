# Divvy Data
A package to access historical and live Chicago bikeshare data.

**Resources**
* Write-up: [The Ultimate Day of Chicago Bikeshare](https://chrisluedtke.github.io/divvy-data.html)
    * Animation: [YouTube](https://www.youtube.com/watch?v=SVueGQPpz14)
* Analysis notebook: [nbviewer](https://nbviewer.jupyter.org/github/chrisluedtke/divvy-data-analysis/blob/master/notebook.ipynb)

## Set up

Fork/clone the repository or pip install the `divvydata` package:
```
pip install -i https://test.pypi.org/simple/ divvy-data
pip install git+https://github.com/chrisluedtke/divvy-data.git
```

## Usage
### Historical Data
```python
import divvydata

# gather historical data over all years
rides, stations = divvydata.get_historical_data(
    years=[str(yr) for yr in range(2013,2019)],
    rides=True,
    stations=True
)
```

### Live Data
```python
import divvydata

sf = divvydata.StationsFeed()
sf.monitor_data(runtime_sec=60)

# filter to stations that received interactions
df = sf.event_history
df = df.loc[df['id'].duplicated(keep=False)]
```

### Data Usage Limitations

This package does not host or directly provide data, except as cited in analysis notebooks. When using Divvy data, follow [Divvy's Data License Agreement](https://www.divvybikes.com/data-license-agreement).
