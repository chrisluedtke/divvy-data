# Divvy Data Analysis
Exploratory and explanatory analysis of Chicago's bikeshare system.

**Resources**
* Write-up: [The Ultimate Day of Chicago Bikeshare](https://chrisluedtke.github.io/divvy-data.html)
    * [Animation on YouTube](https://www.youtube.com/watch?v=SVueGQPpz14)
* [Analysis notebook on nbviewer](https://nbviewer.jupyter.org/github/chrisluedtke/divvy-data-analysis/blob/master/notebook.ipynb)

## Set up

Fork/clone the repository or pip install my `divvy` package:
```
pip install git+https://github.com/chrisluedtke/divvy-data-analysis.git
```

## Usage
### Historical Data
```python
import divvy

# gather historical data over all years
rides, stations = divvy.historical_data.get_data(
    years=[str(yr) for yr in range(2013,2019)],
    rides=True,
    stations=True
)
```

### Live Data
```python
import pandas as pd

import divvy

df = divvy.stations_feed.monitor_data(runtime_sec=60)

# filter to stations that received interactions
df = df.loc[df['id'].duplicated(keep=False)]
```

### License

If you find this repository helpful in your own analysis or project, please cite my name and repository URL.

This repository is not affiliated, approved, endorsed, or sponsored by Motivate. It is not provided for commercial purposes. See [Divvy's Data Liscense Agreement](https://www.divvybikes.com/data-license-agreement).
