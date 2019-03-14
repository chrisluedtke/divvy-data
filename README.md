# divvy-data-analysis
Exploratory and explanatory analysis of Chicago's bikeshare system.

**Resources**
* Write-up: [The Ultimate Day of Chicago Bikeshare](https://chrisluedtke.github.io/divvy-data.html)
* [Analysis notebook on nbviewer](https://nbviewer.jupyter.org/github/chrisluedtke/divvy-data-analysis/blob/master/notebook.ipynb)

## Set up

Fork/clone the repository or pip install my `divvy` package:
```
pip install git+https://github.com/chrisluedtke/divvy-data-analysis.git
```

## Usage
```python
import pandas as pd

import divvy

df = divvy.stations_feed.monitor_data(runtime_sec=60)

# filter to stations that received interaction
df = df.loc[df['id'].duplicated(keep=False)]
```
